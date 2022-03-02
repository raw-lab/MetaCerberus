#!/usr/bin/env bash

set -eu
IFS=$'\n'
umask 0022

ABSPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pathDB="cerberusDB"
pathFGS="FGS+"

install_fgs() {
  local fgspath="$ABSPATH/$pathFGS"
  echo
  echo "Cloning FGS+ to $fgspath"
  echo
  git clone https://github.com/hallamlab/FragGeneScanPlus "$fgspath"
  rm -rf "$fgspath/.git*"
  make CFLAG="-fcommon -w" -C "$fgspath"
  return
}

download_db() {
  local dbdir="$ABSPATH/$pathDB"
  echo
  echo "Downloading database to $dbdir"
  echo
  install -m 0755 -d "$dbdir"

  curl -L https://osf.io/72p6g/download -o "$dbdir/FOAM_readme.txt"
  curl -L https://osf.io/muan4/download -o "$dbdir/FOAM-onto_rel1.tsv"
  curl -L https://osf.io/2hp7t/download -o "$dbdir/KEGG-onto_rel1.tsv"
  curl -L https://osf.io/bdpv5/download -o "$dbdir/FOAM-hmm_rel1a.hmm.gz"
  return
}

clean() {
  rm -rf "$ABSPATH/$pathFGS"
  rm -rf "$ABSPATH/$pathDB"
  return
}

usage() {
  cat <<EOF
usage: $0 [--path PATH] [--download] [--fgs] [--help]

  -d, --download      Download the database files to "$ABSPATH/$pathDB"
  -f, --fgs           Install FGS+ from git repository
  -c, --clean         Removes database files and FGS+

EOF
}


options="$(getopt -o 'cdfh' -l 'clean,download,fgs,help' -n "$(basename "$0")" -- "$@")"

if  [[ $# -eq 0 ]]; then
  printf "error: no arguments specified\n\n"
  usage
  exit 1
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--download)
      download_db
      shift
      ;;
    -f|--fgs)
      install_fgs
      shift
      ;;
    -c|--clean)
      clean
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf "error: unknown argument: '%s'\n\n" "$1"
      usage
      exit 1
      ;;
  esac
done
