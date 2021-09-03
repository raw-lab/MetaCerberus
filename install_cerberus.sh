#!/usr/bin/env bash

access_rights=0o755
pathDB="cerberusDB"

function install {
    install_path=$1
    mkdir -p $install_path
    cp bin/*.py $install_path
    cp bin/*.sh $install_path
    # TODO: Copy package as well.
    $install_path/cerberus_setup.sh -d
    
    unzip src/FragGeneScanPlus-master.zip
    mv FragGeneScanPlus-master "$install_path/FGS+"
    make -C "$install_path/FGS+"
    echo 
    echo "Program files copied to '$install_path'"
    echo "Add this to your PATH or .bashrc for easier use:"
    echo "export PATH=\"$install_path:\$PATH\""
    return
}

function install_pip {
    # TODO: This option is mainly for developmental purposes.
    rm -r dist/
    python -m build > /dev/null #2>&1
    rm -r cerberus.egg-info/
    # install latest build version
    latest=$(ls dist/*.whl | sort -V | tail -n 1)
    python -m pip uninstall cerberus -y
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

    # create the cerberus environment in conda
    conda env remove --name cerberus -y
    conda create -n cerberus -c conda-forge -c bioconda fastqc flash2 fastp porechop bbmap prodigal hmmer pandas numpy plotly scikit-learn configargparse python=3.7 -y

    # install additional pip requirements
    conda activate cerberus
    python -m pip install setuptools build metaomestats ray[default]

    # install cerberus from local folder for now
    # TODO: Change this to proper install once uploaded to pypi and bioconda.
    install_pip
    return
}

function develop_env {
  ABSPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
  export PATH="$ABSPATH/bin:$PATH"
  export PYTHONPATH="$ABSPATH:$PYTHONPATH"
  return
}

### Begin Main Script ###

# Parse Arguments
while (( "$#" )); do
  case "$1" in
    -i|--install)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        ARG_INSTALL=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    -p|--pip)
      ARG_PIP=true
      shift
      ;;
    -c|--conda)
      ARG_CONDA=true
      shift
      ;;
    -e|--env)
      ARG_ENV=true
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

[ ! $ARG_INSTALL $ARG_PIP $ARG_CONDA $ARG_ENV $ARG_HELP ] && echo "
No options given.
" && ARG_HELP=true

[ $ARG_HELP ] && echo "
usage: [--path PATH] [--download] [--dependencies] [--help]

    -i, --install PATH  Copy scripts to PATH and downloads the database.
                        Use this option for a manual install.
                        Assumes dependencies are already installed.
                        (requires 'unzip', 'wget', and 'git')
    -p, --pip           Instal Cerberus using pip from local folder.
                        Dependencies must be installed manually.
                        (requires 'pip')
    -c, --conda         Creates a conda environment named 'cerberus' with all dependencies and installs Cerberus in it
                        (requires Anaconda3 to be installed)
    -h, --help          Display this message and exit
" && exit 0

[ $ARG_INSTALL ] && install $ARG_INSTALL && exit 0
[ $ARG_PIP ] && install_pip && exit 0
[ $ARG_CONDA ] && install_conda && exit 0
[ $ARG_ENV ] && develop_env
