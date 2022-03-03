# Welcome to MetaCerberus

Python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data

![GitHub Logo](cerberus_logo.jpg)

## Installing MetaCerberus

### Option 1) Anaconda

- Anaconda install from bioconda with all dependencies:

    ```bash
    conda create -n metacerberus -c conda-forge -c bioconda metacerberus -y
    conda activate metacerberus
    setup-metacerberus.sh -d
    setup-metacerberus.sh -f
    ```

### Option 2) pip

```bash
pip install metacerberus
```

- This installs the latest build (may be unstable) using pip
- Next run the setup script to download the Database and install FGS+

```bash
setup-metacerberus.sh -f
setup-metacerberus.sh -d
```

- *Dependencies should be installed manually and specified in the config file or path

### Option 3) Manual Install

*Latest code might be unstable

1. Clone github Repo

    ```bash
    git clone https://github.com/raw-lab/metacerberus.git
    ```

2. Run Setup File

    ```bash
    cd metacerberus
    python3 install_metacerberus.py
    conda activate metacerberus
    ```

This creates an anaconda environment called "metacerberus" with all dependencies installed.

## Prerequisites and dependencies

python >= 3.7

MetaCerberus currently runs best with Python version 3.7, 3.8, 3.9 due to compatibility with dependencies, namely "Ray".  
Python 3.10 is not currently supported.

### Available from Bioconda

- fastqc - <https://github.com/s-andrews/FastQC>
- fastp - <https://github.com/OpenGene/fastp>
- porechop - <https://github.com/rrwick/Porechop>
- bbmap - <https://sourceforge.net/projects/bbmap/> or <https://github.com/BioInfoTools/BBMap>
- prodigal - <https://github.com/hyattpd/Prodigal>
- hmmer - <https://github.com/EddyRivasLab/hmmer>

### Other dependencies

- Cerberus depends on a database available at osf.io
- FGS+ needs to be cloned and compiled to run properly
Both of these can be installed after installing cerberus by running:

```bash
cerberus_setup.sh -d
cerberus_setup.sh -f
```

*When using the included install script these are installed automatically.

- NOTE: The KEGG database contains KOs related to Human disease. It is possible that these will show up in the results, even when analyzing microbes.

## Running MetaCerberus

- If needed, activate the MetaCerberus environment in Anaconda

```bash
conda activate metacerberus
```

- If the metacerberus environment is not used, make sure the dependencies are in PATH or specified in the config file.
- Run metacerberus.py with the options required for your project.

```bash
usage: metacerberus.py [-c CONFIG] [--prodigal PRODIGAL] [--fraggenescan FRAGGENESCAN]
                       [--meta META] [--super SUPER] [--protein PROTEIN]
                       [--illumina | --nanopore | --pacbio] [--dir_out DIR_OUT]
                       [--scaffolds] [--minscore MINSCORE] [--cpus CPUS]
                       [--chunker CHUNKER] [--replace] [--keep] [--hmm HMM] [--version]
                       [-h] [--adapters ADAPTERS] [--control_seq CONTROL_SEQ]

optional arguments:
  --illumina            Specifies that the given FASTQ files are from Illumina
  --nanopore            Specifies that the given FASTQ files are from Nanopore
  --pacbio              Specifies that the given FASTQ files are from PacBio

Required arguments
At least one sequence is required.
<accepted formats {.fastq .fasta .faa .fna .ffn}>
Example:
> metacerberus.py --prodigal file1.fasta
> metacerberus.py --config file.config
*Note: If a sequence is given in .fastq format, one of --nanopore, --illumina, or --pacbio is required.:
  -c CONFIG, --config CONFIG
                        Path to config file, command line takes priority
  --prodigal PRODIGAL   Prokaryote nucleotide sequence (includes microbes, bacteriophage)
  --fraggenescan FRAGGENESCAN
                        Eukaryote nucleotide sequence (includes other viruses, works all
                        around for everything)
  --meta META           Metagenomic nucleotide sequences (Uses prodigal)
  --super SUPER         Run sequence in both --prodigal and --fraggenescan modes
  --protein PROTEIN, --amino PROTEIN
                        Protein Amino Acid sequence

optional arguments:
  --dir_out DIR_OUT     path to output directory, creates "pipeline" folder. Defaults to
                        current directory.
  --scaffolds           Sequences are treated as scaffolds
  --minscore MINSCORE   Filter for parsing HMMER results
  --cpus CPUS           Number of CPUs to use per task. System will try to detect
                        available CPUs if not specified
  --chunker CHUNKER     Split files into smaller chunks, in Megabytes
  --replace             Flag to replace existing files. False by default
  --keep                Flag to keep temporary files. False by default
  --hmm HMM             Specify a custom HMM file for HMMER. Default uses downloaded FOAM
                        HMM Database
  --version, -v         show the version number and exit
  -h, --help            show this help message and exit

  --adapters ADAPTERS   FASTA File containing adapter sequences for trimming
  --control_seq CONTROL_SEQ
                        FASTA File containing control sequences for decontamination

Args that start with '--' (eg. --prodigal) can also be set in a config file (specified via
-c). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see
syntax at https://goo.gl/R74nmi). If an arg is specified in more than one place, then
commandline values override config file values which override defaults.
```

- example:

```bash
metacerberus.py --protein <input file path> 
```

### Multiprocessing / Multi-Computing

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
source slurm-metacerberus.sh
# run MetaCerberus
metacerberus.py --prodigal [input_folder] --illumina --dir_out [out_folder]

echo ""
echo "======================================================"
echo "End Time   : $(date)"
echo "======================================================"
echo ""
```

## Input formats

- From any NextGen sequencing technology (from Illumina, PacBio, Oxford Nanopore)
- type 1 raw reads (.fastq format)
- type 2 nucleotide fasta (.fasta, .fa, .fna, .ffn format), assembled raw reads into contigs
- type 3 protein fasta (.faa format), assembled contigs which genes are converted to amino acid sequence

## Output Files

- If an output directory is given, a 'pipeline' subfolder will be created there.
- If no output directory is specified, the 'pipeline' subfolder will be created in the current directory.

## Visualization of outputs

- We use Plotly to visualize the data
- Once the program is executed the html reports with the visuals will be saved to the last step of the pipeline.
- The HTML files require plotly.js to be present. One has been provided in the package and is saved to the report folder.

## Citing MetaCerberus

MetaCerberus: python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data. Preprints.

## CONTACT

The informatics point-of-contact for this project is [Dr. Richard Allen White III](https://github.com/raw-lab).  
If you have any questions or feedback, please feel free to get in touch by email.  
Dr. Richard Allen White III - rwhit101@uncc.edu or raw937@gmail.com.  
Jose Figueroa - jlfiguer@uncc.edu  
Or [open an issue](https://github.com/raw-lab/metacerberus/issues).  
