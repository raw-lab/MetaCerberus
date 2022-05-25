#!/usr/bin/env bash

set -e

function install_pip() {
    rm -rf dist/
    echo "Building MetaCerberus distribution..."
    python -m build > /dev/null 2>&1
    rm -rf metacerberus.egg-info/
    # install latest build version
    latest=$(ls dist/*.gz | sort -V | tail -n 1)
    python -m pip uninstall metacerberus -y
    echo
    echo "Installing $latest"
    echo
    python -m pip install $latest
    metacerberus.py --setup
    return
}

function install_conda() {
    # initialize conda environment in bash script
    eval "$(conda shell.bash hook)"

    # create the metacerberus environment in conda
    conda create -n metacerberus -y -c conda-forge -c bioconda gcc make grpcio fastqc flash2 fastp porechop bbmap prodigal hmmer ray-default ray-core ray-dashboard gitpython pandas plotly scikit-learn dominate python-kaleido configargparse psutil metaomestats

    conda activate metacerberus

    pip install --use-feature=in-tree-build .
    metacerberus.py --setup

    return
}

### Begin Main Script ###

install_conda
