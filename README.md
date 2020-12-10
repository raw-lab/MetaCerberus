# Welcome to RoboMax
>python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data



Installing RoboMax: 
-------
- needs a pip installer
- needs a conda installer
- needs source installer
- maybe a gpu down the road

Input formats:
-----
- From any NextGen sequencing technology (from Illumina, Pacbio, Oxford Nanopore)
- type 1 raw reads (.fastq format)
- type 2 nucleotide fasta (.fasta, .fa, .fna, .ffn format), assembled raw reads into contigs
- type 3 protein fasta (.faa format), assembled contigs which genes are converted to amino acid sequence 

Clone the Robomax Repository 
-----
- Run the below code to clone the Robomax Repository.
```bash
git clone https://github.com/raw-lab/robomax.git
```


Run Setup File
-----
- Open Robomax repo Folder
- Run setup “robomax_setup.py”
```bash
cd robomax
```
```bash
python robomax_setup.py
```
- It will create directory “Robomax” on desktop
- It will install all dependencies from the setup file
- It also download osf files and Latest Version of Primary code file(Wrapper).

Running code by passing data file
-----
- Go to the desktop folder ->Robomax
- Give `input file path` followed by '-i' while running the Wrapper File.
```python robomax.py -i <input file path>```

Output Files
-----
- Output folder will be created on the input folder path.
- Let the Input be RW2.faa, the output folder created will be RW2_output.

visualisation outputs based on output file
-----
- We are Using Dash and Plotly for visualise the data
- Once the program is executed the visuals will be displayed on screen.
- If you want to open those visuals again,Give `rollup file path` (which created in output folder) followed by '-i' while running the Wrapper File.
```
python robomax.py -i <rollup file path>
```


Citing RoboMax
-------------
 RoboMax: python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data. PeerJ Preprints. 

CONTACT
-------
The informatics point-of-contact for this project is [Dr. Richard Allen White III](https://github.com/raw-lab).<br />
If you have any questions or feedback, please feel free to get in touch by email.<br />
Dr. Richard Allen White III - rwhit101@uncc.edu or raw937@gmail.com.  <br />
Thrilok Kumar Reddy Aouk - taouk@uncc.edu.  <br />
Or [open an issue](https://github.com/raw-lab/robomax/issues).
