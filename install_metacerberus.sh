#!/usr/bin/env bash

set -e

ENV_NAME=MetaCerberus
echo "Creating conda environment: "$ENV_NAME

# initialize conda environment in bash script
eval "$(conda shell.bash hook)"

# create the metacerberus environment in conda
mamba create -y -n $ENV_NAME -c conda-forge -c bioconda \
	python'>=3.8' setuptools"<70.0.0" hydrampp pyhmmer">=0.11.0" flash2 \
	pyrodigal pyrodigal-gv \
	metaomestats plotly scikit-learn dominate python-kaleido configargparse psutil pandas \
	fastqc flash2 fastp porechop bbmap trnascan-se phanotate \


conda activate $ENV_NAME

pip install .

metacerberus.py --setup

echo "Created conda environment: "$ENV_NAME
echo "To activate run 'conda activate $ENV_NAME'"
echo "Run metacerberus.py --download to download databases"
