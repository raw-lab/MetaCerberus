#!/usr/bin/env bash

set -e

ENV_NAME=MetaCerberus-1.3.0
echo "Creating conda environment: "$ENV_NAME

# initialize conda environment in bash script
eval "$(conda shell.bash hook)"

# create the metacerberus environment in conda
mamba create -y -n $ENV_NAME -c conda-forge -c bioconda python'>=3.8' setuptools"<70.0.0" fastqc flash2 fastp porechop bbmap prodigal prodigal-gv trnascan-se phanotate hmmer ray-default ray-core ray-tune ray-dashboard plotly scikit-learn dominate python-kaleido configargparse psutil metaomestats

conda activate $ENV_NAME

pip install .

metacerberus.py --setup

echo "Created conda environment: "$ENV_NAME
echo "run metacerberus.py --download to download databases"
