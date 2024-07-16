cd /OUTPUTS/DATA/SUBJECTS

for i in *;do
    cd /OUTPUTS/DATA/SUBJECTS/$i
    echo "-v swmeanNM.nii:visible=1" > commands.txt
    echo "-v /OUTPUTS/Segmentation.nii:visible=1:colormap=lut" >> commands.txt
    echo "-viewsize 400 400 --layout 1 --zoom 3 --viewport z" >> commands.txt
    echo "-slice 95 113 59 -ss ax059.png -noquit" >> commands.txt
    echo "-slice 95 113 60 -ss ax060.png -noquit" >> commands.txt
    echo "-slice 95 113 61 -ss ax061.png -noquit" >> commands.txt
    echo "-slice 95 113 62 -ss ax062.png -noquit" >> commands.txt
    echo "-slice 95 113 63 -ss ax063.png -noquit" >> commands.txt
    echo "-slice 95 113 64 -ss ax064.png -noquit" >> commands.txt
    echo "-slice 95 113 65 -ss ax065.png -noquit" >> commands.txt
    echo "-slice 95 113 66 -ss ax066.png -noquit" >> commands.txt
    echo "-slice 95 113 67 -ss ax067.png -noquit" >> commands.txt
    echo "-slice 95 113 68 -ss ax068.png -noquit" >> commands.txt
    echo "-quit" >> commands.txt
    xvfb-run -a --server-args "-screen 0 1920x1080x24" freeview -cmd commands.txt
    montage -mode concatenate -quality 100 -pointsize 24 -tile 2x -title "SUBJECT: $i" -label "%f" ax*.png -bordercolor white -border 0x50 montage.axl.png
done;

convert /OUTPUTS/DATA/SUBJECTS/*/montage*.png -bordercolor white -border 40x300 -page letter /OUTPUTS/report.pdf
