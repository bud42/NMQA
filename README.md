# NMQA
Neuromelanin QA pipeline


Processing Steps:
- SPM realign NM for motion-corrected average NM
- ANTS Brain Extraction
- ANTS register brain T1 to brain-only MNI template 1mm
- ANTS rigid register NM to T1
- ANTS apply warps to get NM in MNI
- smooth warped NM, FWHM of 1 ​mm


(ROI-analysis should use non-smoothed, voxelwise-analysis should use smoothed)


TODO: add masks of crus cerebri and substantia nigra


TODO: CNR at each voxel in the NM-MRI image was calculated as the percent signal difference in NM-MRI signal intensity at a given voxel (IV) from the signal intensity in 


CNRV = {[IV - mode(ICC)] / mode(ICC)}*100
