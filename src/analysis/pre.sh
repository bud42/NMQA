set -x

# Make the subjects folder
mkdir -p /OUTPUTS/DATA/SUBJECTS

cd /INPUTS

# Copy subjects to outputs
for i in *;do

    cd /INPUTS/$i

    for j in *;do

        # Copy from inputs to outputs
        cp -r /INPUTS/$i/$j/assessors/* /OUTPUTS/DATA/SUBJECTS/${j}

        # Append to subject list
        echo ${j} >> /OUTPUTS/subjects.txt

    done
done

# Decompress for loading in SPM
gunzip /OUTPUTS/DATA/SUBJECTS/*/*.nii.gz
