
# 1. 
# spm realign spm imcalc SPM-ImCalc
# NM
# avgNM

# 2.
# antsBrainExtraction.sh 
# T1
# bT1

# 3.
# antsRegistrationSyN.sh (rigid + affine + deformable syn)
# bT1 
# MNI152NLin2009cAsym
# wbT1

# 4.
# antsRegistrationSyN.sh (rigid)
# avgNM 
# T1

# 5. antsApplyTransforms 
# wavgNM

# 6. spm smooth 1mm
# swavgNM

echo "Prepping inputs"
mkdir /OUTPUTS/DATA
cp -r /INPUTS/* /OUTPUTS/DATA/
gunzip /OUTPUTS/DATA/*.nii.gz

echo "1. Running realign"
xvfb-run \
-e /OUTPUTS/xvfb.err -f /OUTPUTS/xvfb.auth \
-a --server-args "-screen 0 1600x1200x24" \
/opt/spm12/run_spm.sh /opt/mcr/R2019b /opt/src/realign.m
rm /OUTPUTS/xvfb.auth /OUTPUTS/xvfb.err

echo "2. Extracting brain"
antsBrainExtraction.sh \
-d 3 \
-a T1 \
-e /opt/ext/OASIS/T_template0.nii.gz \
-m /opt/ext/OASIS/T_template0_BrainCerebellumProbabilityMask.nii.gz \
-o b

echo "3. Registering T1 to template"
antsRegistrationSyNQuick.sh \
-d 3 \
-f /opt/ext/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz \
-m bT1.nii \
-o T1toTEMPLATE

echo "4. Registering NM to T1"
antsRegistrationSyNQuick.sh \
-d 3 \
-f T1.nii.gz \
-t r \
-m mean_NM.nii.gz \
-o NMtoT1

echo "5. Apply transforms to NM"
antsApplyTransforms \
-d 3 \
-i mean_NM.nii.gz \
-r /opt/ext/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz \
-o wNM.nii.gz \
-t T1toTEMPLATE1Warp.nii.gz \
-t T1toTEMPLATE0GenericAffine.mat \
-t NMtoT10GenericAffine.mat

echo "6. Smoothing NM"
xvfb-run \
-e /OUTPUTS/xvfb.err \
-f /OUTPUTS/xvfb.auth \
-a --server-args "-screen 0 1600x1200x24" \
/opt/spm12/run_spm.sh /opt/mcr/R2019b /opt/src/smooth.m
rm /OUTPUTS/xvfb.auth /OUTPUTS/xvfb.err

echo "ALL DONE!"
