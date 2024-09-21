echo "POST!"

cd /OUTPUTS/DATA/SUBJECTS
python -u /REPO/src/analysis/post.py
python -u /REPO/src/analysis/covars.py
