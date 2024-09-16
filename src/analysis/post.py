import glob

import nibabel as nib
from nilearn import plotting
from nilearn import image

ATLAS_FILE = '/OUTPUTS/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz'
AXIAL_SLICES = (-19, -18, -17, -16, -15, -14, -13, -12, -11, -10)

# Merge smoothed and warped Neuromelanin images from all sessions to 4d image
images = glob.glob('/OUTPUTS/DATA/SUBJECTS/*/sw*.nii.gz')
print(f'merging NM:{images=}')
nm_images = nib.funcs.concat_images(images)
nib.save(nm_images, '/OUTPUTS/DATA/merged_NM.nii.gz')

# Merge CR images from all sessions to 4d image
images = glob.glob('/OUTPUTS/DATA/SUBJECTS/*/CR*.nii.gz')
print(f'merging CR:{images=}')
cr_images = nib.funcs.concat_images(images)
nib.save(cr_images, '/OUTPUTS/DATA/merged_CR.nii.gz')

# Make plots of NM with CR overlay
for i, (cr, nm) in enumerate(zip(image.iter_img(cr_images), image.iter_img(nm_images))):
    print(i)
    plotting.plot_roi(
        cr,
        threshold=0.1,
        bg_img=nm,
        cut_coords=(0, -18, -16),
        draw_cross=False,
        output_file=f'/OUTPUTS/DATA/NM-{i}.pdf'
    )

# Image plot the mean CR
mean_cr = image.mean_img(cr_images)
mean_nm = image.mean_img(nm_images)
plotting.plot_stat_map(
    mean_cr,
    bg_img=mean_nm,
    cut_coords=(0, -18, -16),
    draw_cross=False,
    output_file=f'/OUTPUTS/DATA/mean1.pdf',
)

output_file = f'/OUTPUTS/DATA/mean2.pdf'
disp = plotting.plot_stat_map(
    mean_cr,
    bg_img=mean_nm,
    draw_cross=False,
    display_mode='z',
    cut_coords=AXIAL_SLICES,
)

# Zoom by setting axis limits
for cut_ax in disp.axes.values():
    cut_ax.ax.set_xlim(-20, 20)
    cut_ax.ax.set_ylim(-40, 0)

# Update and save
plotting.show()
disp.savefig(output_file)

# Image plot seg overlay on mean
disp = plotting.plot_roi(
    '/OUTPUTS/Segmentation.nii',
    bg_img=ATLAS_FILE,
    draw_cross=False,
    display_mode='z',
    cmap='gist_rainbow',
    alpha=1.0,
    cut_coords=AXIAL_SLICES,
)

# Zoom by setting axis limits
for cut_ax in disp.axes.values():
    cut_ax.ax.set_xlim(-30, 30)
    cut_ax.ax.set_ylim(-50, 10)

# Update and save
plotting.show()
disp.savefig(f'/OUTPUTS/DATA/seg1.pdf')

# Image plot mean CR per group


# Image plot CR vs age


# Image plot CR vs sex


# Boxplots of CR for each hemi by site (for this is in garjus dashboard stats)

# Subject covariates plots age, sex, site
