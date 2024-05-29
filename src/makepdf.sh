
#xvfb-run -a --server-args "-screen 0 1920x1080x24" freeview -cmd /OUTPUTS/commands.txt;

echo "convert to pdf"
convert montage*.png -bordercolor white -border 40x300 -page letter report.pdf

