from glob import glob
import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from nilearn.plotting import plot_stat_map, plot_design_matrix
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img


CSV_FILE = '/INPUTS/covariates.csv'
AXIAL_SLICES = (-17, -16, -15, -14, -13)
PTHRESH = 0.05
CTHRESH = 0
TITLE = 'Neuromelanin Contrast Ratio voxelwise stats'
EXCLUDE = [
    'P3005', 'P3016', 'P3023',
    'V1014', 'V1016', 'V1021', 'V1026', 'V1029', 'V1063', 'V1065', 'V1071',
    'V1079', 'V1099', 'V1113', 'V1115', 'V1118', 'V1122', 'V1129', 'V1136',
    'V1040', 'V1089', 'V1158', 'V1161', 'V1162', 'V1189', 'V1197']
INCLUDE = [
    'P3001', 'P3002', 'P3004', 'P3007', 'P3008', 'P3009', 'P3013', 'P3017',
    'P3019', 'P3026', 'V1003', 'V1004', 'V1006', 'V1010', 'V1015', 'V1017',
    'V1018', 'V1019', 'V1024', 'V1027', 'V1030', 'V1033', 'V1037', 'V1045',
    'V1048', 'V1051', 'V1068', 'V1081', 'V1084', 'V1086', 'V1087', 'V1091',
    'V1097', 'V1104', 'V1107', 'V1119', 'V1120', 'V1125', 'V1130', 'V1145',
    'V1146', 'V1149', 'V1152', 'V1164', 'V1170', 'V1174', 'V1178', 'V1179',
    'V1180', 'V1187'
]

image_subjects = []
image_files = []

# Check for covariates file
if not os.path.exists(CSV_FILE):
    raise Exception('no csv file, cannot run covars')

# Load covariates from csv file to pandas dataframe
print('loading csv data')
df = pd.read_csv(CSV_FILE)
print(df)

# Filter subjects to get intersection of images and covariates
subjects = df.id.unique()
subjects = [x for x in subjects if x in INCLUDE]
subjects = [x for x in subjects if x not in EXCLUDE]

for subj in subjects:
    subj_files = glob(f'/INPUTS/{subj}/*a/assessors/*/CR.nii.gz')
    if subj_files:
        image_subjects.append(subj)
        image_files.append(subj_files[0])

print(image_subjects)
print(image_files)

df = df.set_index('id')
df = df.loc[image_subjects]

# TODO: Load mean CR for each subject

# Import covariate data
subject_count = len(df)
print(f'n={subject_count}')
age = df['AGE'].astype(float)
age = (age - age.mean()) / age.std()
sex = df['SEX']
group = df['GROUP']

# Comparing age
print('Building age model')
design_matrix_age = pd.DataFrame({
    "age": age,
    "intercept": np.ones(subject_count)
})
print(design_matrix_age)
print(subject_count)

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
print(sex_all_key)

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
print(group_all_key)

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

# Make the report
print('Making report')
with PdfPages('/OUTPUTS/covars.pdf') as pdf:
    # Creat figure for covariates page
    fig, ax = plt.subplots(4, 1, figsize=(8.5,11))
    fig.suptitle(TITLE)
    plt.subplots_adjust(
        left=0.07,
        bottom=0.07,
        right=0.93,
        top=0.93,
        wspace=0.1,
        hspace=0.015,
    )

    # Plot covariates vs mean CR
    print('Plotting covariates')
    # barplot by sex
    # scatterplot by age
    # barplot by group
    #df.barplot(x='AGE', y='GROUP', ax=ax[0])
    #df.barplot(x='AGE', y='SEX', ax=ax[1])

    # Plot colorful view of GLM design
    plot_design_matrix(
        design_matrix_group,
        ax=ax[0])

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

    # Plot the thresholded zmap of sex
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

    # Finish page and save
    pdf.savefig(fig, dpi=300)
    plt.close(fig)


print('Done!')
