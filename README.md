# Welcome to MetaCerberus

[![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io/recipes/metacerberus/README.html)

## About

MetaCerberus transforms raw shotgun metaomics sequencing (i.e. metagenomics/metatranscriptomic) data into knowledge. It is a start to finish python code for versatile analysis of the Functional Ontology Assignments for Metagenomes (FOAM) database and KEGG via Hidden Markov Models (HMM) for whole ecosystem metabolomic analysis.

![GitHub Logo](https://raw.githubusercontent.com/raw-lab/MetaCerberus/main/metacerberus_logo.jpg)

## Installing MetaCerberus

### Option 1) Anaconda

- Anaconda install from bioconda with all dependencies:

```bash
conda create -n metacerberus -c conda-forge -c bioconda metacerberus -y
conda activate metacerberus
metacerberus.py --setup
```

### Option 2) Manual Install

1. Clone github Repo

```bash
git clone https://github.com/raw-lab/metacerberus.git
```

2. Run Setup File

```bash
cd metacerberus
bash install_metacerberus.sh
conda activate metacerberus
```

This creates an anaconda environment called "metacerberus" with all dependencies installed.

## Input formats

- From any NextGen sequencing technology (from Illumina, PacBio, Oxford Nanopore)
- type 1 raw reads (.fastq format)
- type 2 nucleotide fasta (.fasta, .fa, .fna, .ffn format), assembled raw reads into contigs
- type 3 protein fasta (.faa format), assembled contigs which genes are converted to amino acid sequence

## Output Files

- If an output directory is given, that folder will be created where all files are stored.
- If no output directory is specified, the 'pipeline' subfolder will be created in the current directory.
- Gage/Pathview R analysis provided as separate scripts within R. 

## Visualization of Outputs

- We use Plotly to visualize the data
- Once the program is executed the html reports with the visuals will be saved to the last step of the pipeline.
- The HTML files require plotly.js to be present. One has been provided in the package and is saved to the report folder.

## Quick start examples

### Illumina data

#### Bacterial, Archaea and Bacteriophage

```bash
conda activate metacerberus
metacerberus.py --prodigal [input_folder] --illumina --meta --dir_out [out_folder] 
```

#### Eukaryotes and Viruses

```bash
conda activate metacerberus
metacerberus.py --fraggenescan [input_folder] --illumina --meta --dir_out [out_folder] 
```

### Nanopore data

#### Bacterial, Archaea and Bacteriophage

```bash
conda activate metacerberus
metacerberus.py --prodigal [input_folder]  --nanopore --meta --dir_out [out_folder]
```

#### Eukaryotes and Viruses

```bash
conda activate metacerberus
metacerberus.py --fraggenescan [input_folder] --nanopore --meta --dir_out [out_folder] 
```

### PacBio data

#### Microbial, Archaea and Bacteriophage

```bash
conda activate metacerberus
metacerberus.py --prodigal [input_folder]  --pacbio --meta --dir_out [out_folder]
```

#### Eukaryotes and Viruses

```bash
conda activate metacerberus
metacerberus.py --fraggenescan [input_folder]  --pacbio --meta --dir_out [out_folder]
```

### SUPER (both methods)

```bash
conda activate metacerberus
metacerberus.py --super [input_folder]  --pacbio/--nanopore/--illumina --meta --dir_out [out_folder]
```

- Note: Fraggenescan will work for prokaryotes and viruses/bacteriophage but prodigal will not work for eukaryotes. 

## Prerequisites and dependencies

- python >= 3.8

### Available from Bioconda

- fastqc - <https://github.com/s-andrews/FastQC>
- fastp - <https://github.com/OpenGene/fastp>
- porechop - <https://github.com/rrwick/Porechop>
- bbmap - <https://sourceforge.net/projects/bbmap/> or <https://github.com/BioInfoTools/BBMap>
- prodigal - <https://github.com/hyattpd/Prodigal>
- hmmer - <https://github.com/EddyRivasLab/hmmer>

- NOTE: The KEGG database contains KOs related to Human disease. It is possible that these will show up in the results, even when analyzing microbes.

## MetaCerberus Options

- If the metacerberus environment is not used, make sure the dependencies are in PATH or specified in the config file.
- Run metacerberus.py with the options required for your project.

```
usage: metacerberus.py [-c CONFIG] [--prodigal PRODIGAL] [--fraggenescan FRAGGENESCAN] [--super SUPER] [--protein PROTEIN] [--illumina | --nanopore | --pacbio] [--setup]
                       [--uninstall] [--dir_out DIR_OUT] [--meta] [--scaffolds] [--minscore MINSCORE] [--evalue EVALUE] [--cpus CPUS] [--chunker CHUNKER] [--replace]
                       [--keep] [--hmm HMM] [--class CLASS] [--tmpdir TMPDIR] [--version] [-h] [--adapters ADAPTERS] [--qc_seq QC_SEQ]

options:
  --illumina            Specifies that the given FASTQ files are from Illumina
  --nanopore            Specifies that the given FASTQ files are from Nanopore
  --pacbio              Specifies that the given FASTQ files are from PacBio

Required arguments
At least one sequence is required.
<accepted formats {.fastq .fasta .faa .fna .ffn .rollup}>
Example:
> metaerberus.py --prodigal file1.fasta
> metacerberus.py --config file.config
*Note: If a sequence is given in .fastq format, one of --nanopore, --illumina, or --pacbio is required.:
  -c CONFIG, --config CONFIG
                        Path to config file, command line takes priority
  --prodigal PRODIGAL   Prokaryote nucleotide sequence (includes microbes, bacteriophage)
  --fraggenescan FRAGGENESCAN
                        Eukaryote nucleotide sequence (includes other viruses, works all around for everything)
  --super SUPER         Run sequence in both --prodigal and --fraggenescan modes
  --protein PROTEIN, --amino PROTEIN
                        Protein Amino Acid sequence

optional arguments:
  --setup               Set this flag to ensure dependencies are setup [False]
  --uninstall           Set this flag to remove downloaded databases and FragGeneScan+ [False]
  --dir_out DIR_OUT     path to output directory, creates "pipeline" folder. Defaults to current directory. [./results-metacerberus]
  --meta                Metagenomic nucleotide sequences (for prodigal) [False]
  --scaffolds           Sequences are treated as scaffolds [False]
  --minscore MINSCORE   Score cutoff for parsing HMMER results [25]
  --evalue EVALUE       E-value cutoff for parsing HMMER results [1e-09]
  --cpus CPUS           Number of CPUs to use per task. System will try to detect available CPUs if not specified [Auto Detect]
  --chunker CHUNKER     Split files into smaller chunks, in Megabytes [Disabled by default]
  --replace             Flag to replace existing files. [False]
  --keep                Flag to keep temporary files. [False]
  --hmm HMM             Specify the database for HMMER. (KOFam_all, KOFam_eukariote, KOFam_prokaryote, COG, CAZy, PHROG, COG) [KOFam_all]
  --class CLASS         path to a tsv file which has class information for the samples. If this file is included scripts will be included to run Pathview in R
  --tmpdir TMPDIR       temp directory for RAY [system tmp dir]
  --version, -v         show the version number and exit
  -h, --help            show this help message and exit

  --adapters ADAPTERS   FASTA File containing adapter sequences for trimming
  --qc_seq QC_SEQ       FASTA File containing control sequences for decontamination

Args that start with '--' (eg. --prodigal) can also be set in a config file (specified via -c). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for
details, see syntax at https://goo.gl/R74nmi). If an arg is specified in more than one place, then commandline values override config file values which override defaults.
```

### GAGE / PathView

After processing the HMM files MetaCerberus calculates a KO (KEGG Orthology) counts table from KEGG/FOAM for processing through GAGE and PathView.
GAGE is recommended for pathway enrichment followed by PathView for visualize the metabolic pathways. A "class" file is required through the --class option to run this analysis. The output is saved under the step_10-visualizeData/combined/pathview folder. Also, at least 4 samples need to be used for this type of analysis.  
  
GAGE and PathView also require internet access to be able to download information from a database. MetaCerberus will save a bash script 'run_pathview.sh' in the step_10-visualizeData/combined/pathview directory along with the KO Counts tsv files and the class file for running manualy in case MetaCerberus was run on a cluster without access to the internet.

### Multiprocessing / Multi-Computing with RAY

MetaCerberus uses Ray for distributed processing. This is compatible with both multiprocessing on a single node (computer) or multiple nodes in a cluster.  
MetaCerberus has been tested on a cluster using Slurm <https://github.com/SchedMD/slurm>.  
  
A script has been included to facilitate running MetaCerberus on Slurm. To use MetaCerberus on a Slurm cluster, setup your slurm script and run it using sbatch.  

```bash
sbatch example_script.sh
```

example script:  

```bash
#!/usr/bin/env bash

#SBATCH --job-name=test-job
#SBATCH --nodes=3
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128MB
#SBATCH -e slurm-%j.err
#SBATCH -o slurm-%j.out
#SBATCH --mail-type=END,FAIL,REQUEUE

echo "====================================================="
echo "Start Time  : $(date)"
echo "Submit Dir  : $SLURM_SUBMIT_DIR"
echo "Job ID/Name : $SLURM_JOBID / $SLURM_JOB_NAME"
echo "Node List   : $SLURM_JOB_NODELIST"
echo "Num Tasks   : $SLURM_NTASKS total [$SLURM_NNODES nodes @ $SLURM_CPUS_ON_NODE CPUs/node]"
echo "======================================================"
echo ""

# Load any modules or resources here
conda activate metacerberus
# source the slurm script to initialize the Ray worker nodes
source ray-slurm-metacerberus.sh
# run MetaCerberus
metacerberus.py --prodigal [input_folder] --illumina --dir_out [out_folder]

echo ""
echo "======================================================"
echo "End Time   : $(date)"
echo "======================================================"
echo ""
```

## Citing MetaCerberus

MetaCerberus: python code for versatile Functional Ontology Assignments for Metagenomes (FOAM) database searching via Hidden Markov Models (HMM) with environmental focus of shotgun metaomics data. Preprints.

## CONTACT

The informatics point-of-contact for this project is [Dr. Richard Allen White III](https://github.com/raw-lab).  
If you have any questions or feedback, please feel free to get in touch by email.  
Dr. Richard Allen White III - rwhit101@uncc.edu or raw937@gmail.com.  
Jose L. Figueroa III - jlfiguer@uncc.edu  
Or [open an issue](https://github.com/raw-lab/metacerberus/issues).  
