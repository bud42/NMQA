# Make the subjects folder
mkdir -p /OUTPUTS/DATA/SUBJECTS

# Copy subjects to outputs
cp -r /INPUTS/*/* /OUTPUTS/DATA/SUBJECTS/
 
# Decompress for loading in SPM
gunzip /OUTPUTS/DATA/SUBJECTS/*/*.nii.gz
