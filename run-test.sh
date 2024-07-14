#!/bin/bash

#eval "$(conda shell.bash hook)"
#conda activate MetaCerberus
pip install ~/raw-lab/MetaCerberus >/dev/null


DBPATH=~/database/db-metacerberus

#metacerberus.py -h

#metacerberus.py --setup -h
#metacerberus.py --db-path $DBPATH --download CAZy COG flop
#metacerberus.py --setup --db-path $DBPATH
#metacerberus.py --update --db-path $DBPATH

#metacerberus.py --list-db --db-path $DBPATH

#metacerberus.py --download COG CAZy --db-path $DBPATH
#metacerberus.py --download --db-path $DBPATH

rm -r temp-results
command time metacerberus.py --phanotate data/five_genomes/RW1.fna --hmm COG --keep --dir-out temp-results --db-path $DBPATH --slurm-single

#rm -r temp-NfixDB
#command time metacerberus.py --prodigal data/rhizobium_test/ --hmm temp-db/NFixDB.hmm.gz --dir-out temp-NfixDB --db-path $DBPATH --slurm-single

#rm -r temp-rhizobium
#command time metacerberus.py --phanotate data/rhizobium_test/ --hmm COG --dir-out temp-rhizobium --slurm-single --class data/rhizobium_test/samples.tsv --db-path $DBPATH --slurm-single

#rm -r temp-GV
#command time metacerberus.py --pyrodigalgv data/giantvirus.fna --hmm VOG --dir-out temp-GV --chunk 1 --db-path $DBPATH --slurm-single

#rm -r temp-paired
#command time metacerberus.py --fraggenescan ~/temp/raw-reads --illumina --hmm COG --dir-out temp-paired --db-path $DBPATH --slurm-single
