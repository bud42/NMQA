SUBJECT=$1

# Make screenshots of warped NM with masks overlaid
echo "making screenshots"
/Applications/freesurfer/7.4.1/Freeview.app/Contents/MacOS/freeview -cmd /Users/boydb1/git/NMQA/src/freeview_batch.txt > /dev/null 2>&1

# Make screenshots of warped NM with masks overlaid
echo "making montage"
montage -mode concatenate -quality 100 -pointsize 24 -tile 2x -title "SUBJECT: $SUBJECT" -label "%f" ax*.png -bordercolor white -border 0x50 montage.axl.png

