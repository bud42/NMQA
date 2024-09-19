import glob
import os

import pandas as pd
import numpy as np
import nibabel as nib
from nilearn import plotting
from nilearn import image
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img

ATLAS_FILE = '/OUTPUTS/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz'
AXIAL_SLICES = (-19, -18, -17, -16, -15, -14, -13, -12, -11, -10)
CSV_FILE = '/INPUTS/covariates.csv'
PTHRESH = 0.05
CTHRESH = 1

cr_files = glob.glob('/OUTPUTS/DATA/SUBJECTS/*a/CR*.nii.gz')
nm_files = glob.glob('/OUTPUTS/DATA/SUBJECTS/*a/sw*.nii.gz')

# Merge smoothed and warped Neuromelanin images from all sessions to 4d image
print(f'merging NM:{nm_files=}')
nm_images = nib.funcs.concat_images(nm_files)
nib.save(nm_images, '/OUTPUTS/DATA/merged_NM.nii.gz')

# Merge CR images from all sessions to 4d image
print(f'merging CR:{cr_files=}')
cr_images = nib.funcs.concat_images(cr_files)
nib.save(cr_images, '/OUTPUTS/DATA/merged_CR.nii.gz')

# Make plots of NM with CR overlay
for i, (cr, nm) in enumerate(zip(image.iter_img(cr_images), image.iter_img(nm_images))):
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


if not os.path.exists(CSV_FILE):
    print('no covariates, exiting early.')
else:
    # Find input files
    subjects = os.listdir('/OUTPUTS/DATA/SUBJECTS')
    subjects = set(list([x[:-1] for x in subjects]))
    print(f'{subjects=}')

    # Load covariates from csv file to pandas dataframe
    df = pd.read_csv(CSV_FILE)

    # TODO: select subset and match covariate ordering to image data ordering

    # Filter subjects to get intersection of images and covariates
    subjects = [x for x in subjects if x in df.id.unique()]
    df = df[df['id'].isin(subjects)]

    cr_files = [f'/OUTPUTS/DATA/SUBJECTS/{x}a/CR.nii.gz' for x in subjects]
    nm_files = [f'/OUTPUTS/DATA/SUBJECTS/{x}a/swmeanNM.nii.gz' for x in subjects]

    # Import covariate data
    subject_count = len(df)
    print(f'n={subject_count}')
    df = df.set_index('id')
    age = df['AGE'].astype(float)
    sex = df['SEX']
    group = df['GROUP']


    design_matrix_age = pd.DataFrame({
        "age": age,
        "intercept": np.ones(subject_count)
    })
    print(design_matrix_age)

    # Fit a model for CR vs age
    model = SecondLevelModel().fit(cr_files, design_matrix=design_matrix_age)

    # Get the age single t-test
    z_map = model.compute_contrast(
        second_level_contrast=[1, 0],
        output_type="z_score"
    )

    # Apply pval and cluster size thresholds
    thresholded_map, threshold = threshold_stats_img(
        z_map,
        alpha=PTHRESH,
        cluster_threshold=CTHRESH
    )

    # Plot the thresholded zmap of age
    output_file = f'/OUTPUTS/DATA/age.pdf'
    disp = plotting.plot_stat_map(
        thresholded_map,
        threshold=threshold,
        colorbar=True,
        display_mode="z",
        cut_coords=AXIAL_SLICES,
        title=f'GLM output p < {PTHRESH}, cluster size {CTHRESH} (z-scores)',
    )

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-20, 20)
        cut_ax.ax.set_ylim(-40, 0)

    # Update and save
    plotting.show()
    disp.savefig(output_file)

    # Now compare sexes
    #sex_all, sex_all_key = pd.factorize(sex)
    #design_matrix_sex = pd.DataFrame({
    #    "sex": sex_all,
    #    "intercept": np.ones(subject_count),
    #})

    # Compare groups
    group_all, group_all_key = pd.factorize(group)
    print(group_all, group_all_key)

    # Boxplots of CR for each hemi by site (for this is in garjus dashboard stats)

    # Subject covariates plots age, sex, site
