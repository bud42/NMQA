set -x

# Make the subjects folder
mkdir -p /OUTPUTS/DATA/SUBJECTS

cd /INPUTS

# Copy subjects to outputs
for i in */;do

    cd /INPUTS/$i

    for j in *;do

        # Copy from inputs to outputs
        cp -r /INPUTS/$i$j/assessors/* /OUTPUTS/DATA/SUBJECTS/${j}

        # Append to subject list
        echo ${j} >> /OUTPUTS/subjects.txt

    done
done

# Copy the atlas and masks images for screenshots
cp /opt/src/Segmentation.nii /OUTPUTS/
cp /opt/ext/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz /OUTPUTS/
