# 1. spm realign NM
# 2. antsBrainExtraction.sh T1
# 3. antsRegistrationSyN.sh (rigid + affine + deformable syn) bT1 to MNI
# 4. antsRegistrationSyN.sh (rigid) NM to T1
# 5. antsApplyTransforms NM
# 6. spm smooth 1mm NM

echo "Prepping inputs"
mkdir /OUTPUTS/DATA
cp -r /INPUTS/* /OUTPUTS/DATA/

cd /OUTPUTS/DATA

echo "1. Running realign"
gunzip NM.nii.gz
/opt/spm12/run_spm12.sh /opt/mcr/v92 script /opt/src/realign.m
gzip meanNM.nii

echo "2. Extracting brain"
ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=1 && \
LD_LIBRARY_PATH=/opt/ants/lib && \
antsBrainExtraction.sh \
-d 3 \
-a T1.nii.gz \
-e /opt/ext/OASIS/T_template0.nii.gz \
-m /opt/ext/OASIS/T_template0_BrainCerebellumProbabilityMask.nii.gz \
-f /opt/ext/OASIS/T_template0_BrainCerebellumRegistrationMask.nii.gz \
-o T1

echo "3. Registering T1 to template"
LD_LIBRARY_PATH=/opt/ants/lib && \
antsRegistrationSyNQuick.sh \
-d 3 \
-f /opt/ext/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz \
-m T1BrainExtractionBrain.nii.gz \
-o T1toTEMPLATE

echo "4. Registering NM to T1"
LD_LIBRARY_PATH=/opt/ants/lib && \
antsRegistrationSyNQuick.sh \
-d 3 \
-f T1.nii.gz \
-t r \
-m meanNM.nii.gz \
-o NMtoT1

echo "5. Apply transforms to NM"
LD_LIBRARY_PATH=/opt/ants/lib && \
antsApplyTransforms \
-d 3 \
-i meanNM.nii.gz \
-r /opt/ext/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz \
-o wmeanNM.nii.gz \
-t T1toTEMPLATE1Warp.nii.gz \
-t T1toTEMPLATE0GenericAffine.mat \
-t NMtoT10GenericAffine.mat

echo "6. Smoothing NM"
gunzip wmeanNM.nii.gz
/opt/spm12/run_spm12.sh /opt/mcr/v92 script /opt/src/smooth.m
gzip *.nii

echo "ALL DONE!"
