FROM bud42/nmqa:v1

# Install Covariate Processing Standalone (also uses mcr v92)
COPY covarproc_standalone /opt/covarproc_standalone/
RUN chmod a+rx /opt/covarproc_standalone/*


# Copy our code
COPY src /opt/src
