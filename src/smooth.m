clear matlabbatch;
fig = spm_figure('CreateWin','Graphics');
spm('defaults', 'fmri');
spm_jobman('initcfg');

% smoothing with 1mm kernel
matlabbatch{1}.spm.spatial.smooth.data = { '/OUTPUTS/DATA/wmeanNM.nii'};
matlabbatch{1}.spm.spatial.smooth.fwhm = [1 1 1];
matlabbatch{1}.spm.spatial.smooth.dtype = 0;
matlabbatch{1}.spm.spatial.smooth.im = 0;
matlabbatch{1}.spm.spatial.smooth.prefix = 's';

spm_jobman('run', matlabbatch);

exit;
