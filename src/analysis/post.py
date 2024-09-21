import glob
import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import nibabel as nib
from nilearn.plotting import plot_roi, plot_stat_map, plot_anat
from nilearn.image import math_img, binarize_img, mean_img
from nilearn.masking import apply_mask


MASK_FILE = '/OUTPUTS/Segmentation.nii'
ATLAS_FILE = '/OUTPUTS/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz'
AXIAL_SLICES = (-19, -18, -17, -16, -15, -14, -13, -12, -11, -10)
TITLE = 'Neuromelanin Summary (NMQA_v2)'
TITLE += '\nSubstantia Nigra(SN) Crus Cerebri(CC) Contrast Ratio(CR)\nvoxel CR = [voxel SN - mean CC] / mean CC'


# Find data
sessions = os.listdir('/OUTPUTS/DATA/SUBJECTS')
print(f'{sessions=}')

cr_files = sorted(glob.glob('/OUTPUTS/DATA/SUBJECTS/*/CR*.nii.gz'))
nm_files = sorted(glob.glob('/OUTPUTS/DATA/SUBJECTS/*/sw*.nii.gz'))

if len(cr_files) != len(nm_files):
    raise Exception('unequal number of images found for CR/NM')

# Make means
mean_cr = mean_img(cr_files)
mean_nm = mean_img(nm_files)

# Make merged for voxelwise stats
nib.funcs.concat_images(cr_files).to_filename('/OUTPUTS/DATA/CR_all.nii.gz')

# Make masks of each ROI
lh_mask = math_img("img == 2", img=MASK_FILE)
lh_mask.to_filename('/OUTPUTS/DATA/lh_mask.nii.gz')
rh_mask = math_img("img == 1", img=MASK_FILE)
rh_mask.to_filename('/OUTPUTS/DATA/rh_mask.nii.gz')
tot_mask = math_img('(img == 1) | (img == 2)', img=MASK_FILE)
tot_mask.to_filename('/OUTPUTS/DATA/tot_mask.nii.gz')
cc_lh_mask = math_img("img == 3", img=MASK_FILE)
cc_lh_mask.to_filename('/OUTPUTS/DATA/cc_lh_mask.nii.gz')
cc_rh_mask = math_img("img == 4", img=MASK_FILE)
cc_rh_mask.to_filename('/OUTPUTS/DATA/cc_rh_mask.nii.gz')

# Make the PDF
with PdfPages('/OUTPUTS/report.pdf') as pdf:
    # First page showing overview
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

    # Show 3 views, not zoomed
    plot_roi(
        MASK_FILE,
        bg_img=ATLAS_FILE,
        cut_coords=(10, -18, -16),
        axes=ax[0],
        alpha=1.0,
        title='Masks / Atlas',
        cmap='gist_rainbow',
    )

    # Image plot seg overlay on mean
    disp = plot_roi(
        MASK_FILE,
        bg_img=ATLAS_FILE,
        draw_cross=False,
        display_mode='z',
        cmap='gist_rainbow',
        alpha=1.0,
        cut_coords=AXIAL_SLICES,
        axes=ax[1],
    )

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-25, 25)
        cut_ax.ax.set_ylim(-85, 45)

    # Show mean CR/NM 3 views, not zoomed
    disp = plot_stat_map(
        mean_cr,
        bg_img=mean_nm,
        cut_coords=(10, -18, -16),
        draw_cross=False,
        axes=ax[2],
        title=f'Mean CR / Mean NM (n={len(cr_files)})',
        vmin=0,
        vmax=0.5,
        cmap='turbo',
        alpha=1.0,
    )

    # Show all axial slices zoomed
    disp = plot_stat_map(
        mean_cr,
        bg_img=mean_nm,
        draw_cross=False,
        display_mode='z',
        cut_coords=AXIAL_SLICES,
        axes=ax[3],
        colorbar=False,
        annotate=True,
        vmin=0,
        vmax=0.5,
        cmap='turbo',
        alpha=1.0,
    )

    # Zoom by setting axis limits
    for cut_ax in disp.axes.values():
        cut_ax.ax.set_xlim(-25, 25)
        cut_ax.ax.set_ylim(-85, 45)

    # load data from mean image masked by
    df = pd.DataFrame({'LCR': apply_mask(mean_cr, lh_mask)})
    df = pd.concat([df, pd.DataFrame({'RCR': apply_mask(mean_cr, rh_mask)})])
    df = pd.concat([df, pd.DataFrame({'TCR': apply_mask(mean_cr, tot_mask)})])
    df = df.rename(columns={
        'LCR': f'Left CR\nmean={df.LCR.mean():.2f}', 
        'RCR': f'Right CR\nmean={df.RCR.mean():.2f}', 
        'TCR': f'Total CR\nmean={df.TCR.mean():.2f}', 
    })

    # Create the boxplot of CR value
    df.boxplot(ax=ax[4], showfliers=True, patch_artist=True)
    ax[4].set_ylim(-0.01, 0.5)

    # Color each box
    colors = ['lawngreen', 'red', 'brown']
    for patch, color in zip(ax[4].patches, colors):
        patch.set_facecolor(color)

    # Save first page to PDF
    pdf.savefig(fig, dpi=300)

    # Page for each subject/session
    for i, (cr, nm) in enumerate(zip(cr_files, nm_files)):
        # Make a letter paper size figure with 6 plots in 1 column
        fig, ax = plt.subplots(6, 1, figsize=(8.5,11))

        session = cr_files[i].split('/')[4]
        print(i, session)

        # Display the session as page title
        fig.suptitle(session)

        plt.subplots_adjust(
            left=0.07,
            bottom=0.07,
            right=0.93,
            top=0.93,
            wspace=0.015,
            hspace=0.015,
        )

        # Make plots of NM with CR overlay
        plot_stat_map(
            cr,
            bg_img=nm,
            cut_coords=(10, -18, -16),
            draw_cross=False,
            axes=ax[0],
            vmin=0,
            vmax=0.5,
            cmap='turbo',
            alpha=1.0,
        )

        # Show first 5 axial slices zoomed
        disp = plot_anat(
            nm,
            draw_cross=False,
            display_mode='z',
            cut_coords=AXIAL_SLICES[:5],
            axes=ax[1],
            colorbar=False,
            alpha=1.0,
        )

        # Zoom each cut by setting axis limits
        for cut_ax in disp.axes.values():
            cut_ax.ax.set_xlim(-22, 22)
            cut_ax.ax.set_ylim(-44, 4)

        disp.add_contours(lh_mask, levels=[0.5], colors='green', linewidths=1.0, alpha=1.0)
        disp.add_contours(rh_mask, levels=[0.5], colors='red', linewidths=1.0, alpha=1.0)
        disp.add_contours(cc_lh_mask, levels=[0.5], colors='cyan', linewidths=1.0, alpha=1.0)
        disp.add_contours(cc_rh_mask, levels=[0.5], colors='magenta', linewidths=1.0, alpha=1.0)

        # Show last 5 axial slices zoomed
        disp = plot_anat(
            nm,
            draw_cross=False,
            display_mode='z',
            cut_coords=AXIAL_SLICES[5:],
            axes=ax[2],
            annotate=True,
            alpha=1.0,
        )

        # Zoom each cut by setting axis limits
        for cut_ax in disp.axes.values():
            cut_ax.ax.set_xlim(-22, 22)
            cut_ax.ax.set_ylim(-44, 4)

        disp.add_contours(lh_mask, levels=[0.5], colors='green', linewidths=1.0, alpha=1.0)
        disp.add_contours(rh_mask, levels=[0.5], colors='red', linewidths=1.0, alpha=1.0)
        disp.add_contours(cc_lh_mask, levels=[0.5], colors='cyan', linewidths=1.0, alpha=1.0)
        disp.add_contours(cc_rh_mask, levels=[0.5], colors='magenta', linewidths=1.0, alpha=1.0)

        # Show first 5 axial slices zoomed
        disp = plot_stat_map(
            cr,
            bg_img=nm,
            draw_cross=False,
            display_mode='z',
            cut_coords=AXIAL_SLICES[:5],
            axes=ax[3],
            colorbar=False,
            annotate=True,
            vmin=0,
            vmax=0.5,
            cmap='turbo',
            alpha=1.0,
        )

        # Zoom by setting axis limits
        for cut_ax in disp.axes.values():
            cut_ax.ax.set_xlim(-22, 22)
            cut_ax.ax.set_ylim(-44, 4)

        # Show last 5 axial slices zoomed
        disp = plot_stat_map(
            cr,
            bg_img=nm,
            draw_cross=False,
            display_mode='z',
            cut_coords=AXIAL_SLICES[5:],
            axes=ax[4],
            colorbar=False,
            annotate=True,
            vmin=0,
            vmax=0.5,
            cmap='turbo',
            alpha=1.0,
        )

        # Zoom by setting axis limits
        for cut_ax in disp.axes.values():
            cut_ax.ax.set_xlim(-22, 22)
            cut_ax.ax.set_ylim(-44, 4)

        # load data from subject image masked by
        df = pd.DataFrame({'LCR': apply_mask(cr, lh_mask)})
        df = pd.concat([df, pd.DataFrame({'RCR': apply_mask(cr, rh_mask)})])
        df = pd.concat([df, pd.DataFrame({'TCR': apply_mask(cr, tot_mask)})])
        df = df.rename(columns={
            'LCR': f'Left CR\nmean={df.LCR.mean():.2f}',
            'RCR': f'Right CR\nmean={df.RCR.mean():.2f}',
            'TCR': f'Total CR\nmean={df.TCR.mean():.2f}',
        })

        # Create the boxplot of CR values
        df.boxplot(ax=ax[5], showfliers=True, patch_artist=True)
        ax[5].set_ylim(-0.01, 0.5)

        # Color each box
        colors = ['lawngreen', 'red', 'brown']
        for patch, color in zip(ax[5].patches, colors):
            patch.set_facecolor(color)

        pdf.savefig(fig, dpi=300)
        plt.close(fig)

