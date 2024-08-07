#!/bin/bash

#eval "$(conda shell.bash hook)"
#conda activate MetaCerberus
rm -r build *egg-info*
pip install ~/raw-lab/HydraMPP >/dev/null
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
command time metacerberus.py --prodigal data/five_genomes/ --hmm KOFam_prokaryote COG --keep --dir-out temp-results --db-path $DBPATH --grouped --cpus 12

#rm -r temp-NfixDB
#command time metacerberus.py --prodigal data/rhizobium_test/ --hmm temp-db/NFixDB.hmm.gz --dir-out temp-NfixDB --db-path $DBPATH

#rm -r temp-rhizobium
#command time metacerberus.py --phanotate data/rhizobium_test/ --hmm COG --dir-out temp-rhizobium --class data/rhizobium_test/samples.tsv --db-path $DBPATH

#rm -r temp-GV
#command time metacerberus.py --pyrodigalgv data/giantvirus.fna --hmm VOG --dir-out temp-GV --chunk 1 --db-path $DBPATH

#rm -r temp-paired
##--super ~/temp/raw-reads 
##command time metacerberus.py --prodigal ~/temp/raw-reads --illumina --hmm KOFam_all COG --dir-out temp-paired --db-path $DBPATH --cpus 8
#
#args="--prodigalgv ~/temp/raw-reads --illumina --hmm COG --dir-out temp-paired --db-path $DBPATH"
#command time metacerberus.py $args --address "host" --cpus 2 &
#sleep 1
#command time metacerberus.py $args --address localhost --cpus 8 # &> client.log
#wait
