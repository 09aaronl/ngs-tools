#!/bin/bash
#
# This script requires INSTALL_PATH (typically /opt/ngs-tools),
# NGSTOOLS_PATH (typically /opt/ngs-tools/source), and
# CONDA_DEFAULT_ENV (typically /opt/miniconda) to be set.
#
# A miniconda install must exist at $CONDA_DEFAULT_ENV
# and $CONDA_DEFAULT_ENV/bin must be in the PATH
#
# Otherwise, this only requires the existence of the following files:
#	requirements-conda.txt

set -e -o pipefail

echo "PATH:              ${PATH}"
echo "INSTALL_PATH:      ${INSTALL_PATH}"
echo "CONDA_PREFIX:      ${CONDA_PREFIX}"
echo "NGSTOOLS_PATH:     ${NGSTOOLS_PATH}"
echo "MINICONDA_PATH:    ${MINICONDA_PATH}"
echo "CONDA_DEFAULT_ENV: ${CONDA_DEFAULT_ENV}"

CONDA_CHANNEL_STRING="--override-channels -c conda-forge -c bioconda"

# setup/install ngs-tools directory tree and conda dependencies
sync

conda install -y \
	-q $CONDA_CHANNEL_STRING \
	--file "$NGSTOOLS_PATH/requirements-conda.txt" \
	-p "${CONDA_PREFIX}"

# clean up
conda clean -y --all