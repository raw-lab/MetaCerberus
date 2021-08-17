# Welcome to Cerberus

Python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data

![GitHub Logo](cerberus_logo.jpg)

## Installing Cerberus

### Prerequisites and dependencies

python=3.7

Cerberus currently runs best with Python version 3.7 due to compatibility with dependencies, namely "Ray".

#### Available from bioconda

- fastqc - <https://github.com/s-andrews/FastQC>
- fastp - <https://github.com/OpenGene/fastp>
- porechop - <https://github.com/rrwick/Porechop>
- bbmap - <https://sourceforge.net/projects/bbmap/> or <https://github.com/BioInfoTools/BBMap>
- prodigal - <https://github.com/hyattpd/Prodigal>
- hmmer - <https://github.com/EddyRivasLab/hmmer>

These can be installed manually and the paths added to a config file, or installed in an Anaconda environment with this command:

```bash
conda install -c conda-forge -c bioconda fastqc fastp porechop bbmap prodigal hmmer pandas numpy plotly scikit-learn configargparse python=3.7 -y
```

#### Available from PyPi (pip)

- pandas
- numpy
- plotly
- scikit-learn
- configargparse
- ray
- metaomestats

### 1) Clone latest build from github

1. Clone github Repo

```bash
git clone https://github.com/raw-lab/cerberus.git
```

2. Run Setup File

```bash
cd cerberus
python3 install_cerberus.py
```

- --instal option copies the script files to a custom folder and downloads database files
- --pip option uses pip to install Cerberus from the local folder
- --conda option creates a conda environment named "cerberus" and installs cerberus with all dependencies in it
- --help gives more information about the options

### 2) Install with pip from github

```bash
pip install git+https://github.com/raw-lab/cerberus/
```

- This installs the latest build (may be unstable) using pip
- Next run the setup script to download the Database and install FGS+

```bash
cerberus_setup.py -f -d
```

### 3) Anaconda and pip installs (comming soon, stable versions)

1. Anaconda install from bioconda with all dependencies:

```bash
conda install -c bioconda cerberus
```

2. PIP install:

```bash
pip install cerberus
```

- The pip installer will not install all dependencies (since they are not available from pip)
- Many dependencies will need to be installed manually. Running cerberus will let you know what is missing from your environment.

## Database

- The database files are located at <https://osf.io/5ba2v/>
- NOTE: The KEGG database contains KOs related to Human disease. It is possible that these will show up in the results, even when analyzing microbes.

## Running Cerberus

- If needed, activate the Cerberus environment in Anaconda

```bash
conda activate cerberus
```

- If the Cerberus environment is not used, make sure the dependencies are in PATH or specified in the config file.
- Run cerberus-pipeline.py with the options required for your project.

```bash
usage: cerberus-pipeline.py [-c CONFIG] [--mic MIC] [--euk EUK] [--super SUPER]
                   [--prot PROT] [--nanopore | --illumina | --pacbio]
                   [--dir_out DIR_OUT] [--scaf] [--minscore MINSCORE]
                   [--cpus CPUS] [--replace] [--version] [-h]
                   [--adapters ADAPTERS] [----control_seq SEQUENCE]
```

- One of --mic, --euk, --super, or --prot is required.
- --help option will show more details about each option.

- example:

```bash
python cerberus-pipeline.py --euk <input file path> 
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

## Citing Cerberus

Cerberus: python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data. Preprints.

## CONTACT

The informatics point-of-contact for this project is [Dr. Richard Allen White III](https://github.com/raw-lab).  
If you have any questions or feedback, please feel free to get in touch by email.  
Dr. Richard Allen White III - rwhit101@uncc.edu or raw937@gmail.com.  
Jose Figueroa - jlfiguer@uncc.edu  
Or [open an issue](https://github.com/raw-lab/cerberus/issues).  
