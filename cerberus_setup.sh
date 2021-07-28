#!/usr/bin/env bash

access_rights=0o755
pathDB="cerberusDB"

function install {
    path=$1
    mkdir -p $path

    #for file_name in os.listdir('bin/'):
    #    file = os.path.join('bin', file_name)
    #    if os.path.isfile(file):
    #        shutil.copy(file, path)
    #par = 'src/FragGeneScanPlus-master.zip'
    #cmd_unzip = "unzip "+par
    #subprocess.call(cmd_unzip, shell=True)
    #os.rename('FragGeneScanPlus-master', 'FGS+')
    #shutil.move('FGS+', path)
    #make = os.path.join(path, 'FGS+')
    #subprocess.call(['make', '-C', make])
    #print("\nProgram files copied to '"+ path +"'")
    #print("Add this to your PATH or .bashrc for easier use:")
    #print(f'export PATH="{path}:$PATH"')
    return
}

function download_db {
    dbdir="$1/$pathDB"
    echo $dbdir

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
    conda create -n cerberus -c conda-forge -c bioconda gzip fastqc fastp porechop bbmap checkm-genome magpurify prodigal hmmer pandas numpy plotly openpyxl scikit-learn configargparse python=3.7 -y

    # install additional pip requirements
    conda activate cerberus
    pip install metaomestats ray[default]

    # install cerberus as local development.
    # TODO: Change this to proper install.
    pip install -e .
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

[ ! $ARG_ENV $ARG_DOWN $ARG_PATH $ARG_HELP ] && echo "
No options given.
" && ARG_HELP=true

[ $ARG_HELP ] && echo "
usage: [--path PATH] [--download] [--dependencies] [--help]

    -p, --path PATH     Copy scripts and downloads the database
    -d, --download      Setting this flag only downloads the database to --path
    -e, --environment   Creates a conda environment with all dependencies in it (requires Anaconda3 to be installed)
" && exit 0

[ $ARG_ENV ] && install_dependencies
[ $ARG_PATH -a ! $ARG_DOWN ] && echo "Install files and download database to: $ARG_PATH"
[ $ARG_PATH -a $ARG_DOWN ] && download_db $ARG_PATH
