XNATHOST="https://xnat.vanderbilt.edu/xnat"
TESTDIR="$HOME/TEST-nmqa"

if [ -d "$TESTDIR/" ]; then
    echo "Already exists, delete first"
    exit 1;
fi

echo "Downloading inputs"

mkdir $TESTDIR
mkdir $TESTDIR/INPUTS
mkdir $TESTDIR/OUTPUTS

curl -k -s -n \
"${XNATHOST}/data/projects/D3/subjects/V1180/experiments/V1180a/scans/401/resources/NIFTI/files/401_ABCD_T1W3D.nii.gz" \
-o $TESTDIR/INPUTS/T1.nii.gz

curl -k -s -n \
"${XNATHOST}/data/projects/D3/subjects/V1180/experiments/V1180a/scans/1401/resources/NIFTI/files/1401_NN_Columbia.nii.gz" \
-o $TESTDIR/INPUTS/NM.nii.gz

echo "Running docker"
docker run \
--platform linux/amd64 \
-it --rm \
-v $TESTDIR/INPUTS:/INPUTS \
-v $TESTDIR/OUTPUTS:/OUTPUTS \
bud42/nmqa:v3.1
