Welcome to Cerberus
===================

Python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data

![GitHub Logo](cerberus_logo.jpg)

Input formats
--------------

- From any NextGen sequencing technology (from Illumina, PacBio, Oxford Nanopore)
- type 1 raw reads (.fastq format)
- type 2 nucleotide fasta (.fasta, .fa, .fna, .ffn format), assembled raw reads into contigs
- type 3 protein fasta (.faa format), assembled contigs which genes are converted to amino acid sequence

Installing Cerberus (from source)
----------------------------------

Clone github Repo

- Run the below code to clone the Cerberus Repository.

```bash
git clone https://github.com/raw-lab/cerberus.git
```

Run Setup File

- Open Cerberus repo folder
- Run setup “cerberus_setup.py”

```bash
cd cerberus
python3 cerberus_setup.py -p PATH
```

- It will create directory specified by the path and copy binary and package files
- It also downloads the FOAM and KO database files

- The setup script can also create an Anaconda environment with all dependencies installed.

```bash
cd cerberus
python3 cerberus_setup.py -e
```

Running code by passing data file
---------------------------------

- If needed, activate Cerberus environment

```bash
conda activate cerberus
```

- If the Cerberus environment is not used, make sure executable scripts are in the PATH or specified in the config file.
- Run cerberus.py with the options required for your project.

```bash
usage: cerberus.py [-c CONFIG] [--mic MIC] [--euk EUK] [--super SUPER]
                   [--prot PROT] [--nanopore | --illumina | --pacbio]
                   [--dir_out DIR_OUT] [--scaf] [--minscore MINSCORE]
                   [--cpus CPUS] [--replace] [--version] [-h]
                   [--adapters ADAPTERS] [--refseq REFSEQ]
```

- One of --mic, --euk, --super, or --prot is required.
- cerberus.py -h will show more details about each option.
- For example, to use the microbial option: you should use the argument `--mic` along with `<input file path>`.

```bash
python3 cerberus.py --mic <input file path>
```

- For eukaryote option: you should use the argument `--euk` along with `<input file path>`.

```bash
python cerberus.py --euk <input file path> 
```

Output Files
------------

- If an output directory is given a 'pipeline' subfolder will be created there.
- If no output directory is specified the 'pipeline' subfolder will be created in the current directory.

Visualization of outputs
------------------------

- We use Plotly to visualize the data
- Once the program is executed the html reports with the visuals will be saved to the last step of the pipeline.
- The HTML files require plotly.js to be present. One has been provided in the package and is saved to the report folder.

Citing Cerberus
---------------

Cerberus: python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data. Preprints.

CONTACT
-------

The informatics point-of-contact for this project is [Dr. Richard Allen White III](https://github.com/raw-lab).<br />
If you have any questions or feedback, please feel free to get in touch by email.<br />
Dr. Richard Allen White III - rwhit101@uncc.edu or raw937@gmail.com.  <br />
Jose Figueroa - jlfiguer@uncc.edu  <br />
Or [open an issue](https://github.com/raw-lab/cerberus/issues).
