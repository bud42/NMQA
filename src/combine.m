clear matlabbatch;
fig = spm_figure('CreateWin','Graphics');
spm('defaults', 'fmri');
spm_jobman('initcfg');

merged_filename = '/OUTPUTS/merged_swmeanNM.nii'

files = spm_select('ExtFPListRec', '/INPUTS', '.*');
input_filenames = {cellstr(files)};

matlabbatch{1}.spm.util.cat.vols = input_filenames;
matlabbatch{1}.spm.util.cat.name = merged_filename;
matlabbatch{1}.spm.util.cat.dtype = 4;
matlabbatch{1}.spm.util.cat.RT = NaN;

spm_jobman('run', matlabbatch);

exit;