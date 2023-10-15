FROM antsx/ants:latest

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install \
     unzip xorg wget \
     && apt-get clean \
     && rm -rf \
     /tmp/hsperfdata* \
     /var/*/apt/*/partial \
     /var/lib/apt/lists/* \
     /var/log/apt/term*

# Install MATLAB MCR
ENV MCR_INHIBIT_CTF_LOCK 1
RUN mkdir /opt/mcr_install && \
    mkdir /opt/mcr && \
    wget -P /opt/mcr_install \
    https://www.mathworks.com/supportfiles/downloads/R2017a/deployment_files/R2017a/installers/glnxa64/MCR_R2017a_glnxa64_installer.zip && \
    unzip -q /opt/mcr_install/MCR_R2017a_glnxa64_installer.zip -d /opt/mcr_install && \
    /opt/mcr_install/install -destinationFolder /opt/mcr -agreeToLicense yes -mode silent && \
    rm -rf /opt/mcr_install /tmp/*

# Install SPM Standalone in /opt/spm12/
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/opt/ants/lib:/opt/mcr/v92/runtime/glnxa64:/opt/mcr/v92/bin/glnxa64:/opt/mcr/v92/sys/os/glnxa64:/opt/mcr/v92/sys/opengl/lib/glnxa64:/opt/mcr/v92/extern/bin/glnxa64
RUN wget --no-check-certificate --progress=bar:force \
    -P https://www.fil.ion.ucl.ac.uk/spm/download/restricted/utopia/spm12/spm12_r7771_Linux_R2017a.zip \
    && unzip -q /opt/spm12_r7771_Linux_R2017a.zip -d /opt \
    && rm -f spm12_r7771_Linux_R2017a.zip \
    && /opt/spm12/spm12 function exit \
    && chmod +x /opt/spm12/spm12

ADD src /opt
ADD ext /opt

# Configure entry point
#ENTRYPOINT ["/opt/spm12/spm12"]
#CMD ["--help"]
