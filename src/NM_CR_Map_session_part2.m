clc; clear all;

%% Load Data
NM_mask_s = spm_vol('rlr_SN_group_segncc_3_ncut_new.nii');
NM_mask = spm_read_vols(NM_mask_s);
mask_SN_1 = ismember(NM_mask,1);
mask_SN_2 = ismember(NM_mask,2);
mask_SN_3 = ismember(NM_mask,3);

CC_mask_s = spm_vol('Segmentation.nii');
CC_mask = spm_read_vols(CC_mask_s);
mask_CC_R = ismember(CC_mask,3);
mask_CC_L = ismember(CC_mask,4);
mask_CC = mask_CC_R + mask_CC_L;

NM_s = spm_vol('swmeanNM.nii');
NM = spm_read_vols(NM_s);
CR_s = NM_s;

CC = NM .* mask_CC;

SN_1 = NM .* mask_SN_1;
SN_2 = NM .* mask_SN_2;
SN_3 = NM .* mask_SN_3;

for ii = 1:size(NM,3)
    CC_i = CC(:,:,ii);
    CC_mean = mean(nonzeros(CC_i(:)));
    CR_1(:,:,ii) = (SN_1(:,:,ii) - CC_mean)./CC_mean;
    CR_2(:,:,ii) = (SN_2(:,:,ii) - CC_mean)./CC_mean;
    CR_3(:,:,ii) = (SN_3(:,:,ii) - CC_mean)./CC_mean;
end

CR_1(CR_1==-1)=0;
CR_2(CR_2==-1)=0;
CR_3(CR_3==-1)=0;

CR_1(isnan(CR_1))=0;
CR_2(isnan(CR_2))=0;
CR_3(isnan(CR_3))=0;

CR_1(CR_1<0)=0;
CR_2(CR_2<0)=0;
CR_3(CR_3<0)=0;

CR = CR_1 + CR_2 + CR_3;

CR_mean_1 = mean(nonzeros(CR_1(:)));
CR_mean_2 = mean(nonzeros(CR_2(:)));
CR_mean_3 = mean(nonzeros(CR_3(:)));

fprintf('CR1=%g\n', CR_mean_1);
fprintf('CR2=%g\n', CR_mean_2);
fprintf('CR3=%g\n', CR_mean_3);

disp('finished creating map');

fid = fopen('stats.csv', 'a+');
fprintf(fid, 'cr_mean_sn1=%g\n', CR_mean_1);
fprintf(fid, 'cr_mean_sn2=%g\n', CR_mean_2);
fprintf(fid, 'cr_mean_sn3=%g\n', CR_mean_2);
fclose(fid);

disp('saving');
CR_s.fname = 'CR_part2.nii';
spm_write_vol(CR_s, CR);
