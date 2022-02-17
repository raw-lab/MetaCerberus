#!/usr/bin/env bash

pathDB="cerberusDB"

function install_pip {
    rm -r dist/
    echo "Building MetaCerberus distribution..."
    python -m build > /dev/null #2>&1
    rm -r metacerberus.egg-info/
    # install latest build version
    latest=$(ls dist/*.whl | sort -V | tail -n 1)
    python -m pip uninstall metacerberus -y
    echo
    echo "Installing $latest"
    echo
    python -m pip install $latest
    cerberus_setup.sh -d
    cerberus_setup.sh -f
    return
}

function install_conda {
    # initialize conda environment in bash script
    eval "$(conda shell.bash hook)"

    # create the metacerberus environment in conda
    conda create -n metacerberus -c conda-forge -c bioconda gcc make fastqc flash2 fastp porechop bbmap prodigal hmmer ray-core ray-dashboard pandas numpy plotly scikit-learn dominate configargparse metaomestats -y

    # install additional pip requirements
    conda activate metacerberus
    pip install setuptools build

    install_pip
    return
}

### Begin Main Script ###

install_conda
