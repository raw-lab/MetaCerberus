#!/usr/bin/env bash

ABSPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
access_rights=0o755
pathDB="cerberusDB"
pathFGS="FGS+"

function install_FGS+ {
  fgspath="$ABSPATH/$pathFGS"
  echo
  echo "Cloning FGS+ to $fgspath"
  echo
  git clone https://github.com/hallamlab/FragGeneScanPlus $fgspath
  rm -rf "$fgspath/.git*"
  make -C $fgspath
  return
}

function download_db {
  dbdir="$ABSPATH/$pathDB"
  echo
  echo "Downloading database to $dbdir"
  echo
  mkdir -p $dbdir

  wget https://osf.io/72p6g/download -v -O "$dbdir/FOAM_readme.txt" -c
  wget https://osf.io/muan4/download -v -O "$dbdir/FOAM-onto_rel1.tsv" -c
  wget https://osf.io/2hp7t/download -v -O "$dbdir/KO_classification.txt" -c
  wget https://osf.io/bdpv5/download -v -O "$dbdir/FOAM-hmm_rel1a.hmm.gz" -c
  return
}

function clean {
  rm -rf "$ABSPATH/$pathFGS"
  rm -rf "$ABSPATH/$pathDB"
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
    -f|--fgs)
      ARG_FGS=true
      shift
      ;;
    -c|--clean)
      ARG_CLEAN=true
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

[ ! $ARG_DOWN $ARG_FGS $ARG_CLEAN $ARG_HELP ] && echo "
No options given.
" && ARG_HELP=true

[ $ARG_HELP ] && echo "
usage: [--path PATH] [--download] [--dependencies] [--help]

  -d, --download      Download the database files to <cerberus path>/cerberusDB
  -f, --fgs           Clone and install FGS+ to <cerberus path>/FGS+
  -c, --clean         Removes database files and FGS+
" && exit 0

[ $ARG_FGS ] && install_FGS+
[ $ARG_DOWN ] && download_db
[ $ARG_CLEAN ] && clean
