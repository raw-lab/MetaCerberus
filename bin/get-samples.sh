#!/bin/bash

### Phages ###

OUTDIR=PHAGES
GENOMES=$OUTDIR/genomes
rm -r $GENOMES
mkdir -p $GENOMES

wget https://millardlab-inphared.s3.climb.ac.uk/13Jun2023_refseq_genomes.fa.gz -P $OUTDIR
gunzip $OUTDIR/13Jun2023_refseq_genomes.fa.gz

COUNT=$(grep -c ">" $OUTDIR/13Jun2023_refseq_genomes.fa)
COUNT=$(( $COUNT - 1 )) #exclude last sequnce from list, bug with last sed
grep -n ">" $OUTDIR/13Jun2023_refseq_genomes.fa > $OUTDIR/list.txt

echo "Getting 100 random phages from $OUTDIR/13Jun2023_refseq_genomes.fa"
rm -f samples_phages.txt
i=0
while [ $i -le 99 ]
do
	LINE=$(sed -n "$((1 + $RANDOM % $COUNT))p" $OUTDIR/list.txt)
	LINE=$(grep -oE "^[0-9]+" <<<$LINE)
	HEADER=$(sed -n "$LINE"p $OUTDIR/13Jun2023_refseq_genomes.fa)
	ACC=$(grep -oE "^>[A-Za-z0-9_.]+" <<<$HEADER)
	ACC=${ACC#*>}

	if test -f "$GENOMES/$ACC.fna"; then
                echo "$ACC exists, trying another"
                continue
        fi

	sed -n "$LINE,/>/ p" $OUTDIR/13Jun2023_refseq_genomes.fa | sed \$d > $GENOMES/$ACC.fna
	echo $GENOMES/$ACC.fna >>samples_phages.txt
  	i=$(( $i + 1 ))
done


### CPR ###

OUTDIR=CPR
mkdir -p $OUTDIR

echo "Getting CPR sequences from list_cpr-ACC.txt"
rm -f samples_cpr.txt
exec 4<list_cpr-ACC.txt
while read -u4 acc
do
  	esearch -db nucleotide -query "$acc" | efetch -format fasta > $OUTDIR/"$acc".fna
	if test -f $OUTDIR/"$acc".fna; then
		echo $OUTDIR/"$acc".fna >>samples_cpr.txt
	fi
done


### Archaea Viruses ###

OUTDIR=VIRAL_ARCHAEA
mkdir -p $OUTDIR

echo "Getting archaeal virus sequences from list_archaeal_viruses-ACC.txt"
rm -f samples_archaea-viruses.txt
exec 4<list_archaeal_viruses-ACC.txt
while read -u4 acc
do
	esearch -db nucleotide -query "$acc" | efetch -format fasta > $OUTDIR/"$acc".fna
	if test -f $OUTDIR/"$acc".fna; then
		echo $OUTDIR/"$acc".fna >>samples_archaea-viruses.txt
	fi
done


### REFSEQ VIRUSES ###
VIRUSES=/projects/raw_lab/databases/RefSeq/viral.genomic.combined.fna

OUTDIR=VIRAL
GENOMES=$OUTDIR/genomes
rm -r $GENOMES
mkdir -p $GENOMES

COUNT=$(grep -c ">" $VIRUSES)
COUNT=$(( $COUNT - 1 )) #exclude last sequnce from list, bug with last sed
grep -n ">" $VIRUSES > $OUTDIR/list.txt

echo "Getting 100 random viruses from $VIRAL"
rm -f samples_virus.txt
i=0
while [ $i -le 99 ]
do
  	LINE=$(sed -n "$((1 + $RANDOM % $COUNT))p" $OUTDIR/list.txt)
        LINE=$(grep -oE "^[0-9]+" <<<$LINE)
        HEADER=$(sed -n "$LINE"p $VIRUSES)
        ACC=$(grep -oE "^>[A-Za-z0-9_.]+" <<<$HEADER)
        ACC=${ACC#*>}

        if test -f "$GENOMES/$ACC.fna"; then
                echo "$ACC exists, trying another"
                continue
        fi

	sed -n "$LINE,/>/ p" $VIRUSES | sed \$d > $GENOMES/$ACC.fna
        echo $GENOMES/$ACC.fna >>samples_virus.txt
        i=$(( $i + 1 ))
done


### GTDB ###

GTDB=/projects/raw_lab/databases/GTDB

OUTDIR=GTDB-100
rm -r $OUTDIR
mkdir -p $OUTDIR/contigs/archaea
mkdir -p $OUTDIR/genomes/archaea
mkdir -p $OUTDIR/protein/archaea
mkdir -p $OUTDIR/contigs/bacteria
mkdir -p $OUTDIR/genomes/bacteria
mkdir -p $OUTDIR/protein/bacteria


# Get file lists
echo "Gathering GTDB file lists"
find $GTDB/protein_fna_reps/archaea/ -name "*.gz" >list_archaea-contigs.txt
find $GTDB/protein_faa_reps/archaea/ -name "*.gz" >list_archaea-protein.txt
find $GTDB/protein_fna_reps/bacteria/ -name "*.gz" >list_bacteria-contigs.txt
find $GTDB/protein_faa_reps/bacteria/ -name "*.gz" >list_bacteria-protein.txt
find $GTDB/gtdb_genomes_reps_r214/ -name "*.gz" >list_genomes.txt

CNT_ARC=$(wc -l list_archaea-contigs.txt | cut -f1 -d' ')
CNT_BAC=$(wc -l list_bacteria-contigs.txt | cut -f1 -d' ')

echo "Copying ARCHAEA"
i=0
while [ $i -le 99 ]
do
	CONTIGS=$(sed -n $((1 + $RANDOM % $CNT_ARC))p list_archaea-contigs.txt)
	NAME=$(grep -oE "GC[AF]_[0-9.]+" <<<$(basename $CONTIGS))
	GENOMES=$(grep "$NAME" list_genomes.txt)
	PROTEIN=$(grep "$NAME" list_archaea-protein.txt)

	if test -f "$OUTDIR/contigs/archaea/$NAME.fna.gz"; then
		echo "$NAME exists, getting another"
		continue
	fi

	cp $CONTIGS $OUTDIR/contigs/archaea/$NAME.fna.gz
	cp $GENOMES $OUTDIR/genomes/archaea/$NAME.fna.gz
	cp $PROTEIN $OUTDIR/protein/archaea/$NAME.faa.gz
	i=$(( $i + 1 ))
done

echo "Extracting archaea"
gunzip $OUTDIR/*/archaea/* &

echo "Copying BACTERIA"
i=0
while [ $i -le 99 ]
do
  	CONTIGS=$(sed -n $((1 + $RANDOM % $CNT_BAC))p list_bacteria-contigs.txt)
        NAME=$(grep -oE "GC[AF]_[0-9.]+" <<<$(basename $CONTIGS))
        GENOMES=$(grep "$NAME" list_genomes.txt)
        PROTEIN=$(grep "$NAME" list_bacteria-protein.txt)

        if test -f "$OUTDIR/contigs/bacteria/$NAME.fna.gz"; then
                echo "$NAME exists, getting another"
                continue
        fi

        cp $CONTIGS $OUTDIR/contigs/bacteria/$NAME.fna.gz
        cp $GENOMES $OUTDIR/genomes/bacteria/$NAME.fna.gz
        cp $PROTEIN $OUTDIR/protein/bacteria/$NAME.faa.gz
	i=$(( $i + 1 ))
done

echo "Extracting bacteria"
gunzip $OUTDIR/*/bacteria/*

wait
echo "Saving sample lists"
find GTDB-100/contigs/ -name "*.*" > samples_contigs.txt
find GTDB-100/genomes/ -name "*.*" > samples_genomes.txt
find GTDB-100/protein/ -name "*.*" > samples_protein.txt


echo "Combining sample list"
cat samples_genomes.txt samples_phages.txt samples_cpr.txt samples_archaea-viruses.txt samples_virus.txt > samples_combined_fna.txt
