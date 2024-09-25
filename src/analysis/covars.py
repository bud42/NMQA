from glob import glob
import os

import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import scatter_matrix
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from nilearn.plotting import plot_stat_map, plot_design_matrix
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img
from nilearn.image import load_img


MASK_FILE = '/REPO/src/Segmentation.nii'
OUTPDF = '/OUTPUTS/covars.pdf'
OUTRPT = '/OUTPUTS/report.html'
CSV_FILE = '/INPUTS/covariates.csv'
AXIAL_SLICES = (-17, -16, -15, -14, -13)
PTHRESH = 0.05
CTHRESH = 0
TITLE = 'Neuromelanin Contrast Ratio voxelwise stats'


def pair_covars(df, pdf):
    # Plot covariates
    print('Plotting covariates')

    # Full design matrix
    subject_count = len(df)
    print(f'n={subject_count}')
    age = df['AGE'].astype(float)
    age = (age - age.mean()) / age.std()
    sex = df['SEX']
    group = df['GROUP']
    speed = df['SPEED'].astype(float)
    speed = (speed - speed.mean()) / speed.std()
    sex_all, sex_all_key = pd.factorize(sex)
    group_all, group_all_key = pd.factorize(group)

    # Comparing age
    print('Building age model')
    design_matrix = pd.DataFrame({
        "age": age,
        "sex": sex_all,
        "group": group_all,
        "speed": speed,
        "intercept": [1] * subject_count,
    })
    print(design_matrix)

    # Creat figure for covariates page
    fig, ax = plt.subplots(1, 5, figsize=(8.5,11))
    fig.suptitle(TITLE)
    plt.subplots_adjust(
        left=0.07,
        bottom=0.07,
        right=0.93,
        top=0.93,
        wspace=0.1,
        hspace=0.015,
    )

    ax[0].axis('off')
    ax[1].axis('off')

    # Plot colorful view of GLM design
    plot_design_matrix(
        design_matrix,
        ax=ax[2])

    ax[3].axis('off')
    ax[4].axis('off')

    # Finish page and save
    pdf.savefig(fig, dpi=300)
    plt.close(fig)

    # seaborn pairplot
    sns.pairplot(df)
    pdf.savefig(plt.gcf(), dpi=300)
    sns.pairplot(df, hue='SEX')
    pdf.savefig(plt.gcf(), dpi=300)
    sns.pairplot(df, hue='GROUP')
    pdf.savefig(plt.gcf(), dpi=300)


def test_report(df, images):
    from nilearn.reporting import make_glm_report

    sex_all, sex_all_key = pd.factorize(df['SEX'])
    group_all, group_all_key = pd.factorize(df['GROUP'])

    # Comparing age
    print('Building model')
    subject_count = len(df)
    df['AGE'] = df['AGE'].astype(float)
    df['SPEED'] = df['SPEED'].astype(float)
    design_matrix = pd.DataFrame({
        "age": (df['AGE'] - df['AGE'].mean()) / df['AGE'].std(),
        "sex": sex_all,
        "group": group_all,
        "speed": (df['SPEED'] - df['SPEED'].mean()) / df['SPEED'].std(),
        "intercept": [1] * subject_count,
    })
    print(design_matrix)
    print(subject_count)

    print('Fitting full model')
    second_level_model = SecondLevelModel().fit(
        images,
        design_matrix=design_matrix
    )

    print('make_glm_report() age,sex,group,speed')
    report = make_glm_report(
        model=second_level_model,
        alpha=PTHRESH,
        contrasts=["age", "sex", "group", "speed"],
    )

    print('save report')
    report.save_as_html(OUTRPT)


def voxelwise_covars(image_files, df, pdf):
    # Import covariate data
    subject_count = len(df)
    print(f'n={subject_count}')
    age = df['AGE'].astype(float)
    age = (age - age.mean()) / age.std()
    speed = df['SPEED'].astype(float)
    speed = (speed - speed.mean()) / speed.std()
    sex = df['SEX']
    group = df['GROUP']

    # one sample t-test
    design = pd.DataFrame([1] * subject_count, columns=["intercept"])
    model = SecondLevelModel().fit(image_files, design_matrix=design)
    z_map = model.compute_contrast()

    # Comparing age
    print('Building age model')
    design_matrix_age = pd.DataFrame({
        "age": age,
        "intercept": np.ones(subject_count)
    })

    # Fit a model for CR vs age
    print('Fitting model')
    model = SecondLevelModel().fit(
        image_files,
        design_matrix=design_matrix_age
    )

    # Get the age single t-test
    print('Computing contrast')
    age_z_map = model.compute_contrast(
        second_level_contrast=[1, 0],
        output_type="z_score"
    )

    # Apply pval and cluster size thresholds
    print('Thresholding stats')
    age_thr_map, age_thr = threshold_stats_img(
        age_z_map,
        alpha=PTHRESH,
        cluster_threshold=CTHRESH
    )

    # Now compare sexes
    print('Comparing sexes')
    sex_all, sex_all_key = pd.factorize(sex)
    design_matrix_sex = pd.DataFrame({
        "sex": sex_all,
        "intercept": np.ones(subject_count),
    })

    print('Fitting model')
    model = SecondLevelModel().fit(
        image_files,
        design_matrix=design_matrix_sex)

    print('Computing contrast')
    sex_z_map = model.compute_contrast([1,0])

    # Apply pval and cluster size thresholds
    print('Thresholding stats')
    sex_thr_map, sex_thr = threshold_stats_img(
        sex_z_map,
        alpha=PTHRESH,
        cluster_threshold=CTHRESH
    )

    # Compare groups
    print('Comparing groups')
    group_all, group_all_key = pd.factorize(group)
    design_matrix_group = pd.DataFrame({
        "group": group_all,
        "intercept": np.ones(subject_count),
    })

    print('Fitting model')
    model = SecondLevelModel().fit(
        image_files,
        design_matrix=design_matrix_group)

    print('Computing contrast')
    group_z_map = model.compute_contrast([1,0])

    # Apply pval and cluster size thresholds
    print('Thresholding stats')
    group_thr_map, group_thr = threshold_stats_img(
        group_z_map,
        alpha=PTHRESH,
        cluster_threshold=CTHRESH
    )

    # Compare soeed
    print('Comparing speed')
    design_matrix_speed = pd.DataFrame({
        "speed": speed,
        "intercept": np.ones(subject_count),
    })

    print('Fitting speed model')
    model = SecondLevelModel().fit(
        image_files,
        design_matrix=design_matrix_speed)

    print('Computing speed contrast')
    speed_z_map = model.compute_contrast([1,0])

    # Apply pval and cluster size thresholds
    print('Thresholding speed stats')
    speed_thr_map, speed_thr = threshold_stats_img(
        speed_z_map,
        alpha=PTHRESH,
        cluster_threshold=CTHRESH
    )

    # Creat figure for covariates page
    fig, ax = plt.subplots(5, 1, figsize=(8.5,11))
    fig.suptitle(TITLE)
    plt.subplots_adjust(
        left=0.07,
        bottom=0.07,
        right=0.93,
        top=0.93,
        wspace=0.1,
        hspace=0.015,
    )

    # Plot zmap 
    print('Plotting default zmap')
    disp = plot_stat_map(
        z_map,
        colorbar=True,
        display_mode="z",
        cut_coords=AXIAL_SLICES,
        title=f'default (n={subject_count})',
        axes=ax[0],
        alpha=1.0,
        black_bg=True,
    )

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-22, 22)
        cut_ax.ax.set_ylim(-44, 4)

    # Plot the thresholded zmap of age
    print('Plotting age')
    disp = plot_stat_map(
        age_thr_map,
        threshold=age_thr,
        colorbar=True,
        display_mode="z",
        cut_coords=AXIAL_SLICES,
        title=f'Age GLM p < {PTHRESH}, k > {CTHRESH} (n={subject_count})',
        axes=ax[1],
        alpha=1.0,
        black_bg=True,
    )

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-22, 22)
        cut_ax.ax.set_ylim(-44, 4)

    # Plot the thresholded zmap of sex
    print('Plotting sexes')
    disp = plot_stat_map(
        sex_thr_map,
        threshold=sex_thr,
        colorbar=True,
        display_mode="z",
        cut_coords=AXIAL_SLICES,
        title=f'Sex GLM p < {PTHRESH}, k > {CTHRESH} (n={subject_count})',
        axes=ax[2],
        alpha=1.0,
        black_bg=True,
    )

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-22, 22)
        cut_ax.ax.set_ylim(-44, 4)

    # Plot the thresholded zmap for group
    print('Plotting groups')
    disp = plot_stat_map(
        group_thr_map,
        threshold=group_thr,
        colorbar=True,
        display_mode="z",
        cut_coords=AXIAL_SLICES,
        title=f'Group GLM p < {PTHRESH}, k > {CTHRESH} (n={subject_count})',
        axes=ax[3],
        alpha=1.0,
        black_bg=True,
    )

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-22, 22)
        cut_ax.ax.set_ylim(-44, 4)

    # Plot the thresholded zmap for speed
    print('Plotting speed')
    disp = plot_stat_map(
        speed_thr_map,
        threshold=speed_thr,
        colorbar=True,
        display_mode="z",
        cut_coords=AXIAL_SLICES,
        title=f'Speed GLM p < {PTHRESH}, k > {CTHRESH} (n={subject_count})',
        axes=ax[4],
        alpha=1.0,
        black_bg=True,
    )

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-22, 22)
        cut_ax.ax.set_ylim(-44, 4)


    # Finish page and save
    pdf.savefig(fig, dpi=300)
    plt.close(fig)


def get_means(row):
    mask = load_img(MASK_FILE).get_fdata()
    data = load_img(row['IMAGE']).get_fdata()

    row['CR_lh'] = np.mean(data[mask == 2])
    row['CR_rh'] = np.mean(data[mask == 1])

    return row


def main():
    image_subjects = []
    image_files = []

    # Check for covariates file
    if not os.path.exists(CSV_FILE):
        raise Exception('no csv file, cannot run covars')

    # Load covariates from csv file to pandas dataframe
    print(f'loading csv:{CSV_FILE}')
    df = pd.read_csv(CSV_FILE)
    print(df)

    # Filter subjects to get intersection of images and covariates
    subjects = df.id.unique()
    for subj in subjects:
        subj_files = glob(f'/INPUTS/{subj}/*a/assessors/*/CR.nii.gz')
        if subj_files:
            image_subjects.append(subj)
            image_files.append(subj_files[0])

    df = df.set_index('id')
    df = df.loc[image_subjects]

    # Load mean CR means for each subject
    df['IMAGE'] = image_files
    df = df.apply(get_means, axis=1)

    print('Making nilearn.glm report')
    test_report(df, image_files)

    print('Making report')
    with PdfPages(OUTPDF) as pdf:
        pair_covars(df, pdf)
        voxelwise_covars(image_files, df, pdf)

    print('Done!')


if __name__ == '__main__':
    main()
