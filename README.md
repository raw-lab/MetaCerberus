# Welcome to Cerberus
Python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data

![GitHub Logo](cerberus_logo.jpg)


Input formats:
-----
- From any NextGen sequencing technology (from Illumina, Pacbio, Oxford Nanopore)
- type 1 raw reads (.fastq format)
- type 2 nucleotide fasta (.fasta, .fa, .fna, .ffn format), assembled raw reads into contigs
- type 3 protein fasta (.faa format), assembled contigs which genes are converted to amino acid sequence 

Installing Cerberus (from source): 
-----
Clone github Repo
- Run the below code to clone the Robomax Repository.
```bash
git clone https://github.com/raw-lab/cerberus.git
```
Run Setup File
- Open Cerberus repo Folder
- Run setup “Cerberus_setup.py”
```bash
cd cerberus
```
```bash
python cerberus_setup.py
```
- It will create directory “cerberus” on desktop
- It will install all dependencies from the setup file
- It also download osf files and Latest Version of Primary code file(Wrapper).

Running code by passing data file
-----
- Go to the desktop folder 
- Open Cerberus in new terminal.
- Activate prokka environment by running the following code.
```bash
conda activate cerberus_env
```
- Activating cerberus_env is must before running cerberus.
- Give `input file path` followed by '-i' while running the Wrapper File.
```python cerberus.py -i <input file path>```
- Here the input path can either be folder path or file path.

Output Files
-----
- Output folder will be created on the input folder path.
- Let the Input be RW2.faa, the output folder created will be RW2_output.


Visualisation of outputs
-----
- We are Using Dash and Plotly for visualise the data
- Once the program is executed the visuals will be displayed on screen.
- If you want to open those visuals again,
- Give `rollup file path` (which created in output folder) followed by '-i' while running the Wrapper File.
```
python cerberus.py -i <rollup file path>
```

Citing Cerberus
-------------
Cerberus: python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data. Preprints. 

CONTACT
-------
The informatics point-of-contact for this project is [Dr. Richard Allen White III](https://github.com/raw-lab).<br />
If you have any questions or feedback, please feel free to get in touch by email.<br />
Dr. Richard Allen White III - rwhit101@uncc.edu or raw937@gmail.com.  <br />
Thrilok Kumar Reddy Aouk - taouk@uncc.edu.  <br />
Or [open an issue](https://github.com/raw-lab/cerberus/issues).
