TESTDIR="$HOME/TEST-nmqa"

echo "Running docker"
docker run \
--platform linux/amd64 \
-it --rm \
-v $TESTDIR/INPUTS:/INPUTS \
-v $TESTDIR/OUTPUTS:/OUTPUTS \
bud42/nmqa:v3
