import glob

import nibabel as nib
from nilearn import plotting
from nilearn import image

# Merge smoothed and warped Neuromelanin images from all sessions to 4d image
images = glob.glob('/OUTPUTS/DATA/SUBJECTS/*/sw*.nii.gz')
print(f'merging NM:{images=}')
out_image = nib.funcs.concat_images(images)
nib.save(out_image, '/OUTPUTS/DATA/merged_NM.nii.gz')

# Display NM
for i, img in enumerate(image.iter_img(out_image)):
	plotting.plot_img(img, output_file=f'/OUTPUTS/DATA/NM-{i}.pdf')

# Merge CR images from all sessions to 4d image
images = glob.glob('/OUTPUTS/DATA/SUBJECTS/*/CR*.nii.gz')
print(f'merging CR:{images=}')
out_image = nib.funcs.concat_images(images)
nib.save(out_image, '/OUTPUTS/DATA/merged_CR.nii.gz')
