#!/bin/bash

mkdir -p KEGG
cd KEGG
pathview-metacerberus.R ../KEGG_counts.tsv ../KEGG_class.tsv
cd ..
mkdir -p FOAM
cd FOAM
pathview-metacerberus.R ../FOAM_counts.tsv ../FOAM_class.tsv
cd ..
mkdir -p COG
cd COG
pathview-metacerberus.R ../COG_counts.tsv ../COG_class.tsv
cd ..
