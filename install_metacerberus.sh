#!/usr/bin/env bash

set -e

ENV_NAME=MetaCerberus-1.3.0
echo "Creating conda environment: "$ENV_NAME

# initialize conda environment in bash script
eval "$(conda shell.bash hook)"

# create the metacerberus environment in conda
mamba create -y -n $ENV_NAME -c conda-forge -c bioconda python'>=3.8' setuptools"<70.0.0" grpcio=1.43 fastqc flash2 fastp porechop bbmap prodigal-gv trnascan-se phanotate pyhmmer pyrodigal ray-default"<=2.6.3" ray-core"<=2.6.3" ray-tune"<=2.6.3" ray-dashboard"<=2.6.3" plotly scikit-learn dominate python-kaleido configargparse psutil metaomestats

conda activate $ENV_NAME

pip install .

metacerberus.py --setup

echo "Created conda environment: "$ENV_NAME
echo "run metacerberus.py --download to download databases"
