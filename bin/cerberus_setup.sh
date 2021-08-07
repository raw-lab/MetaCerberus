#!/usr/bin/env bash

ABSPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
access_rights=0o755
pathDB="cerberusDB"
pathFGS="FGS+"

function install_FGS+ {
    fgspath="$ABSPATH/$pathFGS"
    git clone https://github.com/hallamlab/FragGeneScanPlus $fgspath
    make -C $fgspath
    return
}

function download_db {
    dbdir="$ABSPATH/$pathDB"
    mkdir -p $dbdir

    wget https://osf.io/72p6g/download -v -O "$dbdir/FOAM_readme.txt" -c
    wget https://osf.io/muan4/download -v -O "$dbdir/FOAM-onto_rel1.tsv" -c
    wget https://osf.io/2hp7t/download -v -O "$dbdir/KO_classification.txt" -c
    wget https://osf.io/bdpv5/download -v -O "$dbdir/FOAM-hmm_rel1a.hmm.gz" -c
    return
}

function install_dependencies {
    # initialize conda environment in bash script
    eval "$(conda shell.bash hook)"

    # create the cerberus environment in conda
    conda env remove --name cerberus -y
    conda create -n cerberus -c conda-forge -c bioconda gzip fastqc fastp porechop bbmap checkm-genome magpurify prodigal hmmer pandas numpy plotly openpyxl scikit-learn configargparse python-kaleido python=3.7 -y

    # install additional pip requirements
    conda activate cerberus
    pip install metaomestats ray[default]

    return
}

### Begin Main Script ###

# Parse Arguments
while (( "$#" )); do
  case "$1" in
    -d|--download)
      ARG_DOWN=true
      shift
      ;;
    -e|--environment)
      ARG_ENV=true
      shift
      ;;
    -f|--fgs)
      ARG_FGS=true
      shift
      ;;
    -h|--help)
      ARG_HELP=true
      shift
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
  esac
done

[ ! $ARG_ENV $ARG_DOWN $ARG_FGS $ARG_HELP ] && echo "
No options given.
" && ARG_HELP=true

[ $ARG_HELP ] && echo "
usage: [--path PATH] [--download] [--dependencies] [--help]

    -d, --download      Download the database files to <cerberus path>/cerberusDB
    -f, --fgs           Clone and install FGS+ to <cerberus path>/FGS+
    -e, --environment   Creates a conda environment named 'cerberus' with all dependencies in it (requires Anaconda3 to be installed)
" && exit 0

[ $ARG_ENV ] && install_dependencies
[ $ARG_FGS ] && install_FGS+
[ $ARG_DOWN ] && download_db
