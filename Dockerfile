FROM quay.io/broadinstitute/viral-baseimage:0.1.15

# Largely borrowed from https://github.com/broadinstitute/viral-ngs/blob/master/Dockerfile

LABEL maintainer "aelin@princeton.edu"

# to build:
#   docker build .
#
# to run:
#   docker run --rm <image_ID> "<command>.py subcommand"
#
# to run interactively:
#   docker run --rm -it <image_ID>

ENV \
	INSTALL_PATH="/opt/ngs-tools" \
	NGSTOOLS_PATH="/opt/ngs-tools/source" \
	MINICONDA_PATH="/opt/miniconda" \
	CONDA_DEFAULT_ENV=ngs-tools-env

ENV \
	PATH="$NGSTOOLS_PATH/scripts:$NGSTOOLS_PATH:$MINICONDA_PATH/envs/$CONDA_DEFAULT_ENV/bin:$MINICONDA_PATH/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
	CONDA_PREFIX=$MINICONDA_PATH/envs/$CONDA_DEFAULT_ENV \
	JAVA_HOME=$MINICONDA_PATH

# Prepare ngs-tools user and installation directory
# Set it up so that this slow & heavy build layer is cached
# unless the requirements* files or the install scripts actually change
WORKDIR $INSTALL_PATH
RUN conda update -n base -c defaults conda
RUN conda create -n $CONDA_DEFAULT_ENV
RUN echo "source activate $CONDA_DEFAULT_ENV" > ~/.bashrc
RUN hash -r
COPY ./ $NGSTOOLS_PATH/
RUN $NGSTOOLS_PATH/docker/install_ngs-tools.sh

RUN /bin/bash -c "set -e; echo -n 'version: '; samtools --version | head -n 1"

CMD ["/bin/bash"]