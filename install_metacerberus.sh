#!/usr/bin/env bash

pathDB="cerberusDB"

function install_pip {
    rm -r dist/
    echo "Building MetaCerberus distribution..."
    python -m build > /dev/null #2>&1
    rm -r metacerberus.egg-info/
    # install latest build version
    latest=$(ls dist/*.gz | sort -V | tail -n 1)
    python -m pip uninstall metacerberus -y
    echo
    echo "Installing $latest"
    echo
    python -m pip install $latest
    setup-metacerberus.sh -f
    setup-metacerberus.sh -d
    return
}

function install_conda {
    # initialize conda environment in bash script
    eval "$(conda shell.bash hook)"

    # create the metacerberus environment in conda
    conda create -n metacerberus -c conda-forge -c bioconda gcc make fastqc flash2 fastp porechop bbmap prodigal hmmer ray-core ray-dashboard pandas numpy plotly scikit-learn dominate python-kaleido configargparse metaomestats -y

    status=$?
    [ $status -eq 0 ] && echo "Conda environment successfully created" || exit 1

    # install additional pip requirements
    conda activate metacerberus
    pip install setuptools build

    install_pip
    return
}

### Begin Main Script ###

install_conda
