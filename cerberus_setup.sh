#!/usr/bin/env bash

function install_dependencies {
    # initialize conda environment in bash script
    eval "$(conda shell.bash hook)"

    # create the cerberus environment in conda
    conda remove env --name cerberus -y
    conda create -n cerberus -c conda-forge -c bioconda gzip fastqc fastp porechop bbmap checkm-genome magpurify prodigal hmmer pandas numpy plotly openpyxl scikit-learn configargparse python=3.7 -y

    # install additional pip requirements
    conda activate cerberus
    pip install metaomestats
    pip install ray[default]

    # install cerberus as local development.
    # TODO: Change this to proper install.
    pip install -e .
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
    -h|--help)
      ARG_HELP=true
      shift
      ;;
    -p|--path)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        ARG_PATH=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
  esac
done

[ ! $ARG_ENV $ARG_DOWN $ARG_PATH $ARG_HELP] && echo "
No options given.
" && ARG_HELP=true

[ $ARG_HELP ] && echo "
usage: [--path PATH] [--download] [--dependencies] [--help]

    -p, --path PATH     Copy scripts and downloads the database
    -d, --download      Setting this flag only downloads the database to --path
    -e, --environment   Creates a conda environment with all dependencies in it (requires Anaconda3 to be installed)
" && exit 0

[ $ARG_ENV ] && install_dependencies
[ $ARG_PATH -a ! $ARG_DOWN ] && echo "Install and download database to: $ARG_PATH"
[ $ARG_DOWN -a $ARG_PATH ] && echo "Download database only to: $ARG_PATH"
