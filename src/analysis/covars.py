import glob
import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from nilearn.plotting import plot_stat_map
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img


CSV_FILE = '/INPUTS/covariates.csv'
AXIAL_SLICES = (-19, -18, -17, -16, -15, -14, -13, -12, -11, -10)
PTHRESH = 0.05
CTHRESH = 1


# Merge CR images from all sessions to 4d image
#print(f'merging CR:{cr_files=}')
#cr_images = nib.funcs.concat_images(cr_files)
#nib.save(cr_images, '/OUTPUTS/DATA/merged_CR.nii.gz')
#make_mean_image(cr_files, )

# Merge smoothed and warped Neuromelanin images from all sessions to 4d image
#print(f'merging NM:{nm_files=}')
#nm_images = nib.funcs.concat_images(nm_files)
#nib.save(nm_images, '/OUTPUTS/DATA/merged_NM.nii.gz')


if not os.path.exists(CSV_FILE):
    raise Exception('no csv file, cannot run covars')


with PdfPages('/OUTPUTS/covars.pdf') as pdf:
    print('loading csv data')

     # Creat figure for covariates page
    fig, ax = plt.subplots(4, 1, figsize=(8.5,11))

    # Load covariates from csv file to pandas dataframe
    df = pd.read_csv(CSV_FILE)

    # Filter subjects to get intersection of images and covariates
    subjects = [x for x in subjects if x in df.id.unique()]
    df = df[df['id'].isin(subjects)]

    # Get baseline scans only
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
    model = SecondLevelModel().fit(
        cr_files,
        design_matrix=design_matrix_age
    )

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
    disp = plot_stat_map(
        thresholded_map,
        threshold=threshold,
        colorbar=True,
        display_mode="z",
        cut_coords=AXIAL_SLICES,
        title=f'GLM output p < {PTHRESH}, cluster size {CTHRESH} (z-scores)',
        axes=ax[0],
        alpha=1.0,
    )

    plt.close(fig)

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-22, 22)
        cut_ax.ax.set_ylim(-44, 4)

    # Now compare sexes
    sex_all, sex_all_key = pd.factorize(sex)
    design_matrix_sex = pd.DataFrame({
        "sex": sex_all,
        "intercept": np.ones(subject_count),
    })
    print(sex_all, sex_all_key)
    print(design_matrix_sex)

    # Compare groups
    group_all, group_all_key = pd.factorize(group)
    print(group_all, group_all_key)
    design_matrix_group = pd.DataFrame({
        "group": group_all,
        "intercept": np.ones(subject_count),
    })
    print(group_all, group_all_key)
    print(design_matrix_group)

    # Compare sites
    site_all, site_all_key = pd.factorize(site)
    print(site_all, site_all_key)
    design_matrix_site = pd.DataFrame({
        "site": site_all,
        "intercept": np.ones(subject_count),
    })
    print(site_all, site_all_key)
    print(design_matrix_site)

