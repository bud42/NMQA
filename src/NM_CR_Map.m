clc; clear all;

%% Load Data
%NM_mask_s = load_nii('/opt/src/Segmentation.nii');
%NM_mask = NM_mask_s.img;
NM_mask_s = spm_vol('/opt/src/Segmentation.nii');
NM_mask = spm_read_vols(N_mask_s);
mask_SN_R = ismember(NM_mask,1);
mask_SN_L = ismember(NM_mask,2);
mask_CC_R = ismember(NM_mask,3);
mask_CC_L = ismember(NM_mask,4);

%NM_all_s = load_nii('/OUTPUTS/DATA/merged_swmeanNM.nii');
%NM_all = NM_all_s.img;
NM_all_s = spm_vol('/OUTPUTS/DATA/merged_swmeanNM.nii');
NM_all = spm_read_vols(NM_all_s);
CR_all_s = NM_all_s;

%% Create CR Maps
for id = 1:size(NM_all,4)
    NM = NM_all(:,:,:,id);
    CC_R = NM .* mask_CC_R;
    CC_L = NM .* mask_CC_L;
    SN_R = NM .* mask_SN_R;
    SN_L = NM .* mask_SN_L;
    for ii = 1:size(NM,3)
        CC_R_i = CC_R(:,:,ii);
        CC_R_mean = mean(nonzeros(CC_R_i(:)));
        CR_R(:,:,ii) = (SN_R(:,:,ii) - CC_R_mean)./CC_R_mean; 
        CC_L_i = CC_L(:,:,ii);
        CC_L_mean = mean(nonzeros(CC_L_i(:)));
        CR_L(:,:,ii) = (SN_L(:,:,ii) - CC_L_mean)./CC_L_mean;
    end

    CR_R(CR_R==-1)=0;
    CR_L(CR_L==-1)=0;
    CR_R(isnan(CR_R))=0;
    CR_L(isnan(CR_L))=0;
    CR_R(CR_R<0)=0;
    CR_L(CR_L<0)=0;
    CR = CR_R + CR_L;

    CR_all(:,:,:,id) = CR;
    CR_mean_all(id,1) = mean(nonzeros(CR(:)));
    CR_mean_R_all(id,1) = mean(nonzeros(CR_R(:)));
    CR_mean_L_all(id,1) = mean(nonzeros(CR_L(:)));
    fprintf('Subject %g: CR=%g \n', id, CR_mean_all(id,1))
end

%CR_all_s.img = CR_all;

%save_nii(CR_all_s,'/OUTPUTS/DATA/CR_all.nii');
CR_all_s.fname = '/OUTPUTS/DATA/CR_all.nii'
spm_write_vol(CR_all_s, CR_all)
