from glob import glob
import os

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from nilearn.plotting import plot_stat_map, plot_design_matrix
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img
from nilearn.image import load_img, math_img
from nilearn.reporting import make_glm_report


SUBJECTS_FILE = '/OUTPUTS/subjects.txt'
MASK_FILE = '/REPO/src/Segmentation.nii'
OUTPDF = '/OUTPUTS/report.pdf'
OUTRPT = '/OUTPUTS/report.html'
CSV_FILE = '/INPUTS/covariates.csv'
AXIAL_SLICES = (-17, -16, -15, -14, -13)
PTHRESH = 0.05
CTHRESH = 0
TITLE = 'Neuromelanin Contrast Ratio voxelwise stats'
lh_mask = math_img("img == 2", img=MASK_FILE)
rh_mask = math_img("img == 1", img=MASK_FILE)


def _plot_design(design, pdf):
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
        design,
        ax=ax[2])

    ax[3].axis('off')
    ax[4].axis('off')

    # Finish page and save
    pdf.savefig(fig, dpi=300)
    plt.close(fig)


def _pairplots(df, pdf):
    # seaborn pairplot without grouping, then group by sex, then subject group
    sns.pairplot(df)
    pdf.savefig(plt.gcf(), dpi=300)
    sns.pairplot(df, hue='SEX')
    pdf.savefig(plt.gcf(), dpi=300)
    sns.pairplot(df, hue='GROUP')
    pdf.savefig(plt.gcf(), dpi=300)


def _glm_report(df, images):
    sex_all, sex_all_key = pd.factorize(df['SEX'])
    group_all, group_all_key = pd.factorize(df['GROUP'])

    # Comparing age
    subject_count = len(df)
    df['AGE'] = df['AGE'].astype(float)
    df['SPEED'] = df['SPEED'].astype(float)
    design_matrix = pd.DataFrame({
        "AGE": (df['AGE'] - df['AGE'].mean()) / df['AGE'].std(),
        "SEX": sex_all,
        "GROUP": group_all,
        "SPEED": (df['SPEED'] - df['SPEED'].mean()) / df['SPEED'].std(),
        "intercept": [1] * subject_count,
    })

    print('Fitting full model')
    second_level_model = SecondLevelModel().fit(
        images,
        design_matrix=design_matrix
    )

    print('make_glm_report() age,sex,group,speed')
    report = make_glm_report(
        model=second_level_model,
        alpha=PTHRESH,
        contrasts=["AGE", "SEX", "GROUP", "SPEED"],
    )

    print('save report')
    report.save_as_html(OUTRPT)


def _add_masks(disp):
    # Trace the masks
    disp.add_contours(
        lh_mask, levels=[0.5], colors='green', linewidths=1.0, alpha=1.0)
    disp.add_contours(
        rh_mask, levels=[0.5], colors='red', linewidths=1.0, alpha=1.0)


def _plot_voxels(voxels, count, name, ax):
    # Apply pval and cluster size thresholds
    thr_voxels, thr = threshold_stats_img(
        voxels,
        alpha=PTHRESH,
        cluster_threshold=CTHRESH
    )

    # Plot the thresholded zmap coronal and axial views
    disp = plot_stat_map(
        thr_voxels,
        threshold=thr,
        colorbar=False,
        display_mode='yz',
        cut_coords=[-18,-15],
        draw_cross=False,
        title= f'{name} GLM p < {PTHRESH}, k > {CTHRESH} (n={count})',
        axes=ax[0],
        alpha=1.0,
        black_bg=True,
    )

    # Trace masks
    _add_masks(disp)

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-18, 18)
        cut_ax.ax.set_ylim(-35, 0)

    # Plot sagittal views
    disp = plot_stat_map(
        thr_voxels,
        threshold=thr,
        colorbar=True,
        display_mode='x',
        cut_coords=(-8,8),
        draw_cross=False,
        axes=ax[1],
        alpha=1.0,
        black_bg=True,
    )

    # Trace masks
    _add_masks(disp)

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-30, -5)
        cut_ax.ax.set_ylim(-35, -5)


def _voxelwise(image_files, df, pdf):
    # Import covariate data
    count = len(df)
    age = df['AGE'].astype(float)
    age = (age - age.mean()) / age.std()
    speed = df['SPEED'].astype(float)
    speed = (speed - speed.mean()) / speed.std()
    sex = df['SEX']
    group = df['GROUP']

    # Factorize categorical variables
    sex_all, sex_all_key = pd.factorize(sex)
    group_all, group_all_key = pd.factorize(group)

    # Build our design matrix
    design = pd.DataFrame({
        "AGE": age,
        "SEX": sex_all,
        "GROUP": group_all,
        "SPEED": speed,
        "intercept": [1] * count,
    })

    # Fit our model
    model = SecondLevelModel().fit(image_files, design_matrix=design)

    # Make contrast images
    def_z_map = model.compute_contrast([0, 0, 0, 0, 1])
    age_z_map = model.compute_contrast([1, 0, 0, 0, 0])
    sex_z_map = model.compute_contrast([0, 1, 0, 0, 0])
    grp_z_map = model.compute_contrast([0, 0, 1, 0, 0])
    spd_z_map = model.compute_contrast([0, 0, 0, 1, 0])

    # Plot design matrix page
    _plot_design(design, pdf)

    # Make plots of contrasts
    fig, ax = plt.subplots(5, 2, figsize=(8.5,11))
    fig.suptitle(TITLE)
    plt.subplots_adjust(
        left=0.07,
        bottom=0.07,
        right=0.93,
        top=0.93,
        wspace=0.0,
        hspace=0.05,
    )

    _plot_voxels(def_z_map, count, 'intercept', ax[0])
    _plot_voxels(age_z_map, count, 'Age', ax[1])
    _plot_voxels(sex_z_map, count, 'Sex', ax[2])
    _plot_voxels(grp_z_map, count, 'Group', ax[3])
    _plot_voxels(spd_z_map, count, 'Speed', ax[4])

    # Finish page and save
    pdf.savefig(fig, dpi=300)
    plt.close(fig)


def _get_means(row):
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

    # Filter subjects to get intersection of images and covariates
    for subj in df.id.unique():
        subj_files = glob(f'/INPUTS/{subj}/*a/assessors/*/CR.nii.gz')
        if subj_files:
            image_subjects.append(subj)
            image_files.append(subj_files[0])

    # Set index and select subjects by id
    df = df.set_index('id')
    df = df.loc[image_subjects]

    # Write list of subjects to text file
    with open(SUBJECTS_FILE, 'w') as f:
        for s in image_subjects:
            f.write(f"{s}\n")

    # Load mean CR means for each subject
    df['IMAGE'] = image_files
    df = df.apply(_get_means, axis=1)

    # Make reports
    print('Making nilearn.glm report')
    _glm_report(df, image_files)

    print('Making voxelwise report')
    with PdfPages(OUTPDF) as pdf:
        _voxelwise(image_files, df, pdf)
        _pairplots(df, pdf)


    print('Done!')


if __name__ == '__main__':
    main()
