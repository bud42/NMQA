clc; clear all;

%% Load Data
NM_mask_s = spm_vol('Segmentation.nii');
NM_mask = spm_read_vols(NM_mask_s);
mask_SN_R = ismember(NM_mask,1);
mask_SN_L = ismember(NM_mask,2);
mask_CC_R = ismember(NM_mask,3);
mask_CC_L = ismember(NM_mask,4);

NM_s = spm_vol('swmeanNM.nii');
NM = spm_read_vols(NM_s);
CR_s = NM_s;

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

CR_mean = mean(nonzeros(CR(:)));
CR_mean_R = mean(nonzeros(CR_R(:)));
CR_mean_L = mean(nonzeros(CR_L(:)));

fprintf('CR=%g\n', CR_mean);

disp('finished creating map');

fid = fopen('stats.csv','w');
fprintf(fid, 'cr_mean=%g\n' CR_mean);
fprintf(fid, 'cr_mean_lh=%g\n' CR_mean_L);
fprintf(fid, 'cr_mean_rh=%g\n' CR_mean_R);
fclose(fid);

disp('saving');
CR_s.fname = ['CR.nii'];
spm_write_vol(CR_s, CR);
