#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate metacerberus
pip install ~/raw-lab/MetaCerberus >/dev/null

#rm -r result-inphared
#command time metacerberus.py --protein inphared/1Mar2024_vConTACT2_proteins.faa --hmm pvog/PVOG.hmm.gz --dir_out result-inphared --keep --chunker 10

rm -r results
command time metacerberus.py --protein ~/raw-lab/MetaCerberus/data/KO_validated_proteins.faa --hmm COG,pvog/PVOG.hmm.gz --keep --dir-out results
