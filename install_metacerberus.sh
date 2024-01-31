#!/usr/bin/env bash

set -e

ENV_NAME=metacerberus

# initialize conda environment in bash script
eval "$(conda shell.bash hook)"

# create the metacerberus environment in conda
mamba create -y -n $ENV_NAME -c conda-forge -c bioconda python'>=3.8' grpcio'=1.43' fastqc flash2 fastp porechop bbmap prodigal prodigal-gv trnascan-se hmmer ray-default ray-core ray-tune ray-dashboard pandas plotly scikit-learn dominate python-kaleido configargparse psutil metaomestats

conda activate $ENV_NAME

pip install .

metacerberus.py --setup
