.. MetaCerberus ReadTheDocs documentation master file, created by
   sphinx-quickstart on Thu Jun 20 16:34:08 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MetaCerberus ReadTheDocs!
========================================

|Paper| |Pre-print| |Downloads PePY overall| |Downloads PePy monthly| |Downloads PePy weekly| |BioConda Install Downloads| |Version| |Anaconda-Server Latest Release date| |Anaconda-Server Relative Release date| |Anaconda-Server Platforms| |Anaconda-Server License|

.. |Paper| image:: https://img.shields.io/badge/paper-Bioinformatics-teal.svg?style=flat-square&maxAge=3600
   :target: https://doi.org/10.1093/bioinformatics/btae119  

.. |Pre-print| image:: https://img.shields.io/badge/preprint-BioRxiv-red.svg?style=flat-square&maxAge=3600
   :target: https://doi.org/10.1101/2023.08.10.552700

.. |Downloads PePY overall| image:: https://static.pepy.tech/badge/metacerberus
   :target: https://pepy.tech/project/metacerberus

.. |Downloads PePY monthly| image:: https://static.pepy.tech/badge/metacerberus/month
   :target: https://pepy.tech/project/metacerberus

.. |Downloads PePy weekly| image:: https://static.pepy.tech/badge/metacerberus/week
   :target: https://pepy.tech/project/metacerberus

.. |BioConda Install Downloads| image:: https://anaconda.org/bioconda/metacerberus/badges/downloads.svg
   :target: https://anaconda.org/bioconda/metacerberus

.. |Version| image:: https://anaconda.org/bioconda/metacerberus/badges/version.svg
   :target: https://anaconda.org/bioconda/metacerberus

.. |Anaconda-Server Latest Release date| image:: https://anaconda.org/bioconda/metacerberus/badges/latest_release_date.svg
   :target: https://anaconda.org/bioconda/metacerberus

.. |Anaconda-Server Relative Release date| image:: https://anaconda.org/bioconda/metacerberus/badges/latest_release_relative_date.svg
   :target: https://anaconda.org/bioconda/metacerberus

.. |Anaconda-Server Platforms| image:: https://anaconda.org/bioconda/metacerberus/badges/platforms.svg
   :target: https://anaconda.org/bioconda/metacerberus

.. |Anaconda-Server License| image:: https://anaconda.org/bioconda/metacerberus/badges/license.svg
   :target: https://anaconda.org/bioconda/metacerberus      

.. note:: Metacerberus version 1.3 is the newest version via manual install due to current Conda/Mamba issue.

About
============== 
MetaCerberus transforms raw sequencing (i.e. genomic, transcriptomics, metagenomics, metatranscriptomic) data into knowledge. It is a start to finish python code for versatile analysis of the Functional Ontology Assignments for Metagenomes (FOAM), KEGG, CAZy/dbCAN, VOG, pVOG, PHROG, COG, and a variety of other databases including user customized databases via Hidden Markov Models (HMM) for functional annotation for complete metabolic analysis across the tree of life (i.e., bacteria, archaea, phage, viruses, eukaryotes, and whole ecosystems). Metacerberus also provides automatic differential statistics using DESeq2/EdgeR, pathway enrichments with GAGE, and pathway visualization with Pathview R.


.. image:: https://raw.githubusercontent.com/raw-lab/MetaCerberus/main/img/Screenshot_20240614_205914_Gallery.jpg
   :width: 600px

General Terminal Info and Help Links for Novices
=========================================================
The following are links to helpful webpages based on your operating system. These contain basic starter info for those who have no previous experience with terminals or commands. 

Operating System
------------------ 

* **Linux** 
~~~~~~~~~~~~

`Here <3_>`_, you can find a tutorial covering the basics of the Linux command line, using Ubuntu.

.. _3: https://ubuntu.com/tutorials/command-line-for-beginners#1-overview

Other informative pages can be found `here <4_>`_ and `here <marq_>`_.

.. _4: https://ryanstutorials.net/linuxtutorial/
.. _marq: https://www.marquette.edu/high-performance-computing/linux-intro.php

* **Mac**
~~~~~~~~~~

Click `here`_ for terminal basics.

.. _here: https://support.apple.com/guide/terminal/welcome/mac

* **Windows - MUST use Ubuntu**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Click `here <5_>`_ for the Ubuntu download page, or download in the Microsoft store.

.. _5: https://ubuntu.com/desktop/wsl 

`Here <6_>`_, you can find a tutorial covering the basics of the Linux command line, using Ubuntu.

.. _6: https://ubuntu.com/tutorials/command-line-for-beginners#1-overview

Installation
=============

Installing MetaCerberus 1.3 manually due to Mamba/Conda issue (Newest Version)
---------------------------------------------------------------------------------
.. important:: 
   You still need to have Mamba and Conda installed. You cannot just use Mamba/Conda directly for the new version, currently. Click `here <7_>`_ for Conda download instructions.
   For each command given, enter the first line of the command, then press ENTER. Once the operation completes, the terminal prompt will reappear (blinking vertical line where you type). Proceed to the next line of the given command, press ENTER. Continue as such, line by line, until the entire given command has been entered.  

.. _7: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html 

In the command line, type: 

::

  git clone https://github.com/raw-lab/MetaCerberus.git 
  cd metacerberus
  bash install_metacerberus.sh
  conda activate MetaCerberus-1.3.0
  metacerberus.py --download


Installing MetaCerberus 1.2.1 and below (due to current Mamba and Conda errors)
-------------------------------------------------------------------------------------
.. note:: 
   We will update this as soon as Mamba/Conda corrects this error. 

Option 1) Mamba
~~~~~~~~~~~~~~~~~
.. note::
   Make sure to install Mamba in your base Conda environment unless you have OSX with ARM architecture (M1/M2 Macs). Follow the OSX-ARM instructions below if you have a Mac with ARM architecture.

Mamba install from bioconda with all dependencies:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Linux/OSX-64**

1. Install Mamba using Conda

In command line, type:

::

  conda install mamba

2. Install MetaCerberus with Mamba

In command line, type:

::

   mamba create -n metacerberus -c bioconda -c conda-forge metacerberus
   conda activate metacerberus
   metacerberus.py --setup

OSX-ARM (M1/M2) [if using a Mac with ARM architecture]
 
1. Set up Conda environment

In command line, type:
::

   conda create -y -n metacerberus 
   conda activate metacerberus
   conda config --env --set subdir osx-64

2. Install Mamba, Python, and Pydantic inside the environment

In command line, type:
::

   conda install -y -c conda-forge mamba python=3.10 "pydantic<2"

3. Install MetaCerberus with Mamba

In command line, type:
::

   mamba install -y -c bioconda -c conda-forge metacerberus
   metacerberus.py --setup


.. note:: 
   Mamba is the fastest installer. Anaconda or miniconda can be slow. Also, install Mamba from Conda, **NOT from pip. The Mamba from pip doesn't work for install.** 

Option 2) Anaconda - Linux/OSX-64 Only
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Anaconda install from bioconda with all dependencies:

In command line, type:

::

   conda create -n metacerberus -c conda-forge -c bioconda metacerberus -y
   conda activate metacerberus
   metacerberus.py --setup

Overview 
=============

.. image:: https://raw.githubusercontent.com/raw-lab/metacerberus/main/img/workflow.jpg
   :width: 600px

General Info
---------------

* MetaCerberus has **three** basic modes: 
    1. Quality Control (QC) for raw reads
    2. Formatting/gene prediction
    3. Annotation 
- MetaCerberus can use **three** different input files:
    1. Raw read data from any sequencing platform (Illumina, PacBio, or Oxford Nanopore)
    2. Assembled contigs, as MAGs, vMAGs, isolate genomes, or a collection of contigs
    3. Amino acid fasta (.faa), previously called pORFs
- We offer customization, including running all databases together, individually or specifying select databases. For example, if a user wants to run prokaryotic or eukaryotic-specific KOfams, or an individual database alone such as dbCAN, both are easily customized within Metacerberus.
- In QC mode, raw reads are quality controlled with pre- and post-trim via `FastQC`_. Raw reads are then trimmed via data type; if the data is Illumina or PacBio, `fastp`_  is called, otherwise it assumes the data is Oxford Nanopore then `PoreChop`_ is utilized.
- If Illumina reads are utilized, an optional bbmap step to remove the phiX174 genome is available or user provided contaminate genome. Phage phiX174 is a common contaminant within the Illumina platform as their library spike-in control. We highly recommend this removal if viral analysis is conducted, as it would provide false positives to ssDNA microviruses within a sample.
- We include a ``--skip_decon`` option to skip the filtration of phiX174, which may remove common k-mers that are shared in ssDNA phages.
- In the formatting and gene prediction stage, contigs and genomes are checked for N repeats. These N repeats are removed by default.
- We impute contig/genome statistics (e.g., N50, N90, max contig) via our custom module `Metaome Stats`_.
- Contigs can be converted to pORFs using `Prodigal <8_>`_ , `FragGeneScanRs`_, and `Prodigal-gv`_ as specified by user preference.
- Scaffold annotation is not recommended due to N's providing ambiguous annotation.
- Both Prodigal and FragGeneScanRs can be used via our ``--super`` option, and we recommend using FragGeneScanRs for samples rich in eukaryotes.
- FragGeneScanRs found more ORFs and KOs than Prodigal for a stimulated eukaryote rich metagenome. HMMER searches against the above databases via user specified bitscore and e-values or our minimum defaults (i.e., bitscore = 25, e-value = 1 x 10\ :sup:`-9`).
.. _fastp: https://doi.org/10.1093/bioinformatics/bty560
.. _PoreChop: https://github.com/rrwick/Porechop
.. _FastQC: https://github.com/s-andrews/FastQC
.. _Metaome Stats: https://github.com/raw-lab/metaome_stats 
.. _8: https://anaconda.org/bioconda/prodigal
.. _FragGeneScanRs: https://github.com/unipept/FragGeneScanRs/
.. _Prodigal-gv: https://github.com/apcamargo/prodigal-gv

Input File Formats
----------------------
- From any NextGen sequencing technology (from Illumina, PacBio, Oxford Nanopore)
- Type 1 raw reads (.fastq format)
- Type 2 nucleotide fasta (.fasta, .fa, .fna, .ffn format), assembled raw reads into contigs
- Type 3 protein fasta (.faa format), assembled contigs which genes are converted to amino acid sequence

Output Files
----------------

- If an output directory is given, that folder will be created where all files are stored.
- If no output directory is specified, the 'results_metacerberus' subfolder will be created **in the current directory.**
- Gage/Pathview R analysis provided as separate scripts within R.  

Visualization of Outputs
----------------------------

- We use Plotly to visualize the data
- Once the program is finished running, the html reports with the visuals will be saved to the _last_ step of the pipeline.
- The HTML files require plotly.js to be present. One has been provided in the package and is saved to the report folder.

Annotation
===========

.. image:: https://raw.githubusercontent.com/raw-lab/metacerberus/main/img/Rules.jpg
   :width: 600px 

- **Rule 1** is for finding high quality matches across databases. It is a score pre-filtering module for pORFs thresholds: which states that each pORF match to an HMM is recorded by default or a user-selected cut-off (i.e.,  e-value/bit scores) per database independently, or across all default databases (e.g, finding best hit), or per user specification of the selected database.
- **Rule 2** is to avoid missing genes encoding proteins with dual domains that are not overlapping. It is imputed for non-overlapping dual domain module pORF threshold: if two HMM hits are non-overlapping from the same database, both are counted as long as they are within the default or user selected score (i.e., e-value/bit scores).
- **Rule 3** is to ensure overlapping dual domains are not missed. This is the dual independent overlapping domain module for convergent binary domain pORFs. If two domains within a pORF are overlapping <10 amino acids (e.g, COG1 and COG4) then both domains are counted and reported due to the dual domain issue within a single pORF. If a function hits multiple pathways within an accession, both are counted, in pathway roll-up, as many proteins function in multiple pathways.
- **Rule 4** is the equal match counter to avoid missing high quality matches within the same protein. This is an independent accession module for a single pORF: if both hits within the same database have equal values for both e-value and bit score but are different accessions from the same database (e.g., KO1 and KO3) then both are reported.
- **Rule 5** is the ‘winner take all’ match rule for providing the best match. It is computed as the winner takes all module for overlapping pORFs: if two HMM hits are overlapping (>10 amino acids) from the same database the lowest resulting e-value and highest bit score wins.
- **Rule 6** is to avoid partial or fractional hits being counted. This ensures that only whole discrete integer counting (e.g., 0, 1, 2 to n) are computed and that partial or fractional counting is excluded. 

Quick Start Examples
========================

Genome examples
----------------

- All databases
~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --prodigal lambda.fna --hmm ALL --dir_out lambda_dir


- Only KEGG/FOAM all
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --prodigal lambda.fna --hmm KOFam_all --dir_out lambda_ko-only_dir


- Only KEGG/FOAM prokaryotic centric
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --prodigal ecoli.fna --hmm KOFam_prokaryote --dir_out ecoli_ko-only_dir



- Only KEGG/FOAM eukaryotic centric
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --fraggenescan human.fna --hmm KOFam_eukaryote --dir_out human_ko-only_dir

- Only Viral/Phage databases
::

   conda activate metacerberus
   metacerberus.py --prodigal lambda.fna --hmm VOG, PHROG --dir_out lambda_vir-only_dir

.. tip::

   You can pick any single database you want for your analysis including KOFam_all, COG, VOG, PHROG, CAZy or specific KO databases for eukaryotes and prokaryotes (KOFam_eukaryote or KOFam_prokaryote).

- Custom HMM
~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --prodigal lambda.fna --hmm Custom.hmm --dir_out lambda_vir-only_dir

Illumina data
------------------
- Bacterial, Archaea and Bacteriophage metagenomes/metatranscriptomes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --prodigal [input_folder] --illumina --meta --dir_out [out_folder] 

- Eukaryotes and Viruses metagenomes/metatranscriptomes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --fraggenescan [input_folder] --illumina --meta --dir_out [out_folder] 

Nanopore data
-----------------
- Bacterial, Archaea and Bacteriophage metagenomes/metatranscriptomes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --prodigal [input_folder]  --nanopore --meta --dir_out [out_folder]


- Eukaryotes and Viruses metagenomes/metatranscriptomes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --fraggenescan [input_folder] --nanopore --meta --dir_out [out_folder] 


PacBio data
-----------------------
- Microbial, Archaea and Bacteriophage metagenomes/metatranscriptomes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus 
   metacerberus.py --prodigal [input_folder]  --pacbio --meta --dir_out [out_folder]


- Eukaryotes and Viruses metagenomes/metatranscriptomes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda activate metacerberus
   metacerberus.py --fraggenescan [input_folder]  --pacbio --meta --dir_out [out_folder]


SUPER (both methods)
----------------------

::

   conda activate metacerberus
   metacerberus.py --super [input_folder]  --pacbio/--nanopore/--illumina --meta --dir_out [out_folder]


.. important:: 
   Fraggenescan will work for prokaryotes and viruses/bacteriophage but prodigal will not work well for eukaryotes.

Prerequisites and Dependencies
================================
- **python >= 3.8**
Available from Bioconda - external tool list
---------------------------------------------
+---------------------+------------------+------------------------------+
| Tool                |     Version      |           Publication        |
+---------------------+------------------+------------------------------+
| `Fastqc`_           |    0.12.1        |            None              |
+---------------------+------------------+------------------------------+
| `Fastp <9_>`_       |    0.23.4        |    `Chen et al. 2018`_       | 
+---------------------+------------------+------------------------------+
| `PoreChop`_         |    0.2.4         |              None            |
+---------------------+------------------+------------------------------+
| `bbmap`_            |     39.06        |              None            |
+---------------------+------------------+------------------------------+
| `Prodigal`_         |     2.6.3        |     `Hyatt et al. 2010`_     | 
+---------------------+------------------+------------------------------+
| `FragGeneScanRs`_   | v1.1.0           | `Van der Jeugt et al. 2022`_ |
+---------------------+------------------+------------------------------+
| `Prodigal-gv`_      |   2.2.1          |   `Camargo et al. 2023`_     |
+---------------------+------------------+------------------------------+
| `Phanotate`_        |    1.5.0         |   `McNair et al. 2019`_      | 
+---------------------+------------------+------------------------------+
| `HMMR`_             |     3.4          |    `Johnson et al. 2010`_    |
+---------------------+------------------+------------------------------+

.. _Fastqc: https://github.com/s-andrews/FastQC
.. _9: https://github.com/OpenGene/fastp
.. _PoreChop: https://github.com/rrwick/Porechop
.. _bbmap: https://github.com/BioInfoTools/BBMap
.. _Prodigal: https://github.com/hyattpd/Prodigal
.. _FragGeneScanRs: https://github.com/unipept/FragGeneScanRs/
.. _Prodigal-gv: https://github.com/apcamargo/prodigal-gv
.. _Phanotate: https://github.com/deprekate/PHANOTATE
.. _HMMR: https://github.com/EddyRivasLab/hmmer
.. _Chen et al. 2018: https://doi.org/10.1093/bioinformatics/bty560
.. _Hyatt et al. 2010: https://doi.org/10.1186/1471-2105-11-119
.. _Van der Jeugt et al. 2022: https://doi.org/10.1186/s12859-022-04736-5
.. _Camargo et al. 2023: https://www.nature.com/articles/s41587-023-01953-y
.. _McNair et al. 2019: https://doi.org/10.1093/bioinformatics/btz265
.. _Johnson et al. 2010: https://doi.org/10.1186/1471-2105-11-431

Metacerberus Databases
==========================

All pre-formatted databases are present at `OSF`_. 

.. _OSF: https://osf.io/3uz2j

Database sources
---------------------------------------------------------------------------------

+-------------------+--------------+------------+----------------------------------+------------------------------+
| Database          |  Last Update |  Version   |  Publication                     | Metacerberus Update Version  |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `KEGG/KOfams`_    | 2024-01-01   |   Jan24    | `Aramaki et al. 2020`_           |     beta                     |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `FOAM/KOfams`_    | 2017         |    1       | `Prestat et al. 2014`_           |     beta                     |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `COG`_	           | 2020	        |   2020     | `Galperin et al. 2020`_          |     beta                     |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `dbCAN/CAZy`_     | 2023-08-02	  |    12	   | `Yin et al., 2012`_	           |     beta                     |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `VOG`_	           | 2017-03-03	  |    80	   | `Website`_	                    |     beta                     |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `pVOG`_	        |  2016	     |    2016	   | `Grazziotin et al. 2017`_        |	  1.2                      |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `PHROG`_	        | 2022-06-15	  |    4	      | `Terizan et al., 2021`_	        |     1.2                      |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `PFAM`_	        | 2023-09-12	  |    36	   | `Mistry et al. 2020`_	           |     1.3                      |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `TIGRfams`_	     | 2018-06-19	  |    15	   |  `Haft et al. 2003`_	           |     1.3                      |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `PGAPfams`_	     | 2023-12-21	  |    14	   |  `Tatusova et al. 2016`_	        |     1.3                      |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `AMRFinder-fams`_ | 2024-02-05	  | 2024-02-05 |  `Feldgarden et al. 2021`_       |	  1.3                      |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `NFixDB`_	        | 2024-01-22	  |    2	      |  `Bellanger et al. 2024`_        |	  1.3                      |
+-------------------+--------------+------------+----------------------------------+------------------------------+
|  `GVDB`_	        | 2021	        |    1	      |  `Aylward et al. 2021`_	        |     1.3                      |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `Pads Arsenal`_	  | 2019-09-09	  |    1	      |  `Zhang et al. 2020`_	           |    Coming soon               |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `efam-XC`_	     | 2021-05-21	  |    1	      |  `Zayed et al. 2021`_	           |    Coming soon               |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `NMPFams`_	     | 2021	        |    1	      |  `Baltoumas et al. 2024`_        |    Coming soon               |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `MEROPS`_	        |  2017	     |    1 	   |  `Rawlings et al. 2018`_	        |    Coming soon               |
+-------------------+--------------+------------+----------------------------------+------------------------------+
| `FESNov`_	        | 2024	        |    1	      | `Rodríguez del Río et al. 2024`_ |    Coming soon               |
+-------------------+--------------+------------+----------------------------------+------------------------------+

.. _KEGG/KOfams: https://www.genome.jp/ftp/db/kofam/
.. _FOAM/KOfams: https://osf.io/3uz2j/
.. _COG: https://ftp.ncbi.nlm.nih.gov/pub/COG/COG2020/data/
.. _dbCAN/CAZy: https://bcb.unl.edu/dbCAN2/download/
.. _VOG: https://vogdb.org/download
.. _pVOG: https://ftp.ncbi.nlm.nih.gov/pub/kristensen/pVOGs/downloads.html#
.. _PHROG: https://phrogs.lmge.uca.fr/
.. _PFAM: http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release
.. _TIGRfams: https://ftp.ncbi.nlm.nih.gov/hmm/TIGRFAMs/release_15.0/
.. _PGAPfams: https://ftp.ncbi.nlm.nih.gov/hmm/current/
.. _AMRFinder-fams: https://ftp.ncbi.nlm.nih.gov/hmm/NCBIfam-AMRFinder/latest/
.. _NFixDB: https://github.com/raw-lab/NFixDB
.. _GVDB: https://faylward.github.io/GVDB/
.. _Pads Arsenal: https://ngdc.cncb.ac.cn/padsarsenal/download.php
.. _efam-XC: https://datacommons.cyverse.org/browse/iplant/home/shared/iVirus/Zayed_efam_2020.1
.. _NMPFams: https://bib.fleming.gr/NMPFamsDB/downloads
.. _MEROPS: https://www.ebi.ac.uk/merops/download_list.shtml
.. _FESNov: https://zenodo.org/records/10242439
.. _Aramaki et al. 2020: https://doi.org/10.1093/bioinformatics/btz859
.. _Prestat et al. 2014: https://doi.org/10.1093/nar/gku702
.. _Galperin et al. 2020: https://doi.org/10.1093/nar/gkaa1018
.. _Yin et al., 2012: https://doi.org/10.1093/nar/gks479
.. _Website: https://vogdb.org/
.. _Grazziotin et al. 2017: https://doi.org/10.1093/nar/gkw975
.. _Terizan et al., 2021: https://doi.org/10.1093/nargab/lqab067
.. _Mistry et al. 2020: https://doi.org/10.1093/nar/gkaa913
.. _Haft et al. 2003: https://doi.org/10.1093/nar/gkg128
.. _Tatusova et al. 2016: https://doi.org/10.1093/nar/gkw569
.. _Feldgarden et al. 2021: https://doi.org/10.1038/s41598-021-91456-0
.. _Bellanger et al. 2024: https://doi.org/10.1101/2024.03.04.583350
.. _Aylward et al. 2021: https://doi.org/10.1371/journal.pbio.3001430
.. _Zhang et al. 2020: https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gkz916
.. _Zayed et al. 2021: https://doi.org/10.1093/bioinformatics/btab451
.. _Baltoumas et al. 2024: https://doi.org/10.1093/nar/gkad800
.. _Rawlings et al. 2018: https://academic.oup.com/nar/article/46/D1/D624/4626772
.. _Rodríguez del Río et al. 2024: https://www.nature.com/articles/s41586-023-06955-z

.. note:: 
   The KEGG database contains KOs related to Human disease. It is possible that these will show up in the results, even when analyzing microbes. eggNOG and FunGene database are coming soon. If you want a custom HMM build please let us know by email or leaving an issue.

Custom Database
-----------------

To run a custom database, you need a HMM containing the protein family of interest and a metadata sheet describing the HMM required for look-up tables and downstream analysis. For the metadata information you need an ID that matches the HMM and a function or hierarchy. See example below: 

Example Metadata sheet
~~~~~~~~~~~~~~~~~~~~~~~~
+------+----------+
| ID   | Function |
+------+----------+ 
| HMM1 | Sugarase |
+------+----------+ 
| HMM2 | Coffease | 
+------+----------+

Metacerberus Options
======================

.. important:: 
   If the Metacerberus environment is not used, make sure the dependencies are in PATH or specified in the config file.

- Run ``metacerberus.py`` with the options required for your project.

Usage of ``metacerberus.py``: 

.. Note::
   The following are different options/arguments to modify the execution of Metacerberus.


**Setup arguments:**
~~~~~~~~~~~~~~~~~~~~~~~~~
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+----------------------------+-----------------------------------------------+
|Argument/Option  | Function [Default]                                                                                                                        | Usage Format                   | Accepted format            |            Example (Type as one line)         |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+----------------------------+-----------------------------------------------+
| ``--setup``     |  Setup additional dependencies [False]                                                                                                    |  ``--setup``                   |  N/A                       | ``metacerberus.py --setup``                   |  
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+----------------------------+-----------------------------------------------+
| ``--update``    | Update downloaded databases [False]                                                                                                       | ``--update``                   | N/A                        | ``metacerberus.py --update``                  |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+----------------------------+-----------------------------------------------+
| ``--list-db``   | List available and downloaded databases [False]                                                                                           | ``--list-db``                  | N/A                        | ``metacerberus.py --list-db``                 | 
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+----------------------------+-----------------------------------------------+
| ``--download``  | Downloads selected HMMs. Use the option ``--list-db`` for a list of available databases, default is to download all available databases   | ``--download [DOWNLOAD ...]``  | ``--download [.HMM FILE]`` | ``--download path/to/example/directory.hmm``  |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+----------------------------+-----------------------------------------------+
| ``--uninstall`` | Remove downloaded databases and FragGeneScan+ [False]                                                                                     | ``--uninstall``                | N/A                        | ``metacerberus.py --uninstall``               |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+----------------------------+-----------------------------------------------+

**Input File Arguments:**
----------------------------

.. important:: 
  **At least one** sequence is required.

  **Accepted formats**: [.fastq, .fq, .fasta, .fa, .fna, .ffn, .faa]

   Example:
 
   - ``metacerberus.py --prodigal file1.fasta`` 
   - ``metacerberus.py --config file.config``

   If a sequence is given in [.fastq, .fq] format, one of ``--nanopore``, ``--illumina``, or ``--pacbio`` **is required.**:

   **Option format interpretation:**
   
   - ``--setup`` = accepts no additional options

   - ``--download DOWNLOAD`` = accepts one option, (represented by capitalized command 'DOWNLOAD')

   - ``--fraggenescan FRAGGENESCAN [FRAGGENESCAN...]`` = accepts one or greater options (represented by capitalized commands)

+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+              
|Argument/Option              | Function                                                                                                                                | Usage Format                                                            | Accepted format     | # Options Accepted | Example (Type as one line)                                                                |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``-c`` or ``--config``      | Path to config file, command line takes priority                                                                                        | ``-c CONFIG`` or ``--config CONFIG``                                    | Path to config file | 1                  | ``metacerberus.py -c path/to/config/file``                                                |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+ 
| ``--prodigal``              | Prokaryote nucleotide sequence (includes microbes, bacteriophage)                                                                       | ``--prodigal PRODIGAL [PRODIGAL ...]``                                  | Sequence file       | =>1                | ``metacerberus.py --prodigal FILE1 FILE2...``                                             |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--fraggenescan``          | Eukaryote nucleotide sequence (includes other viruses, works all around for everything)                                                 | ``--fraggenescan FRAGGENESCAN [FRAGGENESCAN ...]``                      | Sequence file       | =>1                | ``metacerberus.py --fraggenescan FILE1 FILE2...``                                         |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--super``                 | Runs sequence in **both** `--prodigal` and `--fraggenescan` modes                                                                        | ``--super SUPER [SUPER ...]``                                           | Sequence file       | =>1                | ``metacerberus.py --super FILE1 FILE2...``                                                |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--prodigalgv``            | Giant virus nucleotide sequence                                                                                                         | ``--prodigalgv PRODIGALGV [PRODIGALGV ...]``                            | Sequence file       | =>1                | ``metacerberus.py --prodigalgv FILE1 FILE2...``                                           |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--phanotate``             | Phage sequence                                                                                                                          | ``--phanotate PHANOTATE [PHANOTATE ...]``                               | Sequence file       | =>1                | ``metacerberus.py --phanotate  FILE1 FILE2...``                                           | 
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--protein`` or ``--amino``| Protein Amino Acid sequence                                                                                                             | ``--protein PROTEIN [PROTEIN ...]`` or ``--amino PROTEIN [PROTEIN ...]``| Sequence file       | =>1                | ``metacerberus.py --protein FILE1 FILE2...`` or ``metacerberus.py --amino FILE1 FILE2...``| 
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--hmmer-tsv``             | Annotations tsv file from HMMER (experimental)                                                                                          | ``--hmmer-tsv HMMER_TSV [HMMER_TSV ...]``                               | Sequence file       | =>1                | ``metacerberus.py --hmmer-tsv FILE1 FILE2...``                                            |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--class``                 | path to a tsv file which has class information for the samples. If this file is included, scripts will be included to run Pathview in R | ``--class CLASS``                                                       | Path to TSV file    | 1                  | ``metacerberus.py --class TSV_FILE1``                                                     |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--illumina``              | Specifies that the given FASTQ files are from Illumina                                                                                  | ``--illumina``                                                          | N/A                 | N/A                | ``metacerberus.py --illumina``                                                            |
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--nanopore``              | Specifies that the given FASTQ files are from Nanopore                                                                                  | ``--nanopore``                                                          | N/A                 | N/A                | ``metacerberus.py --nanopore``                                                            |  
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+
| ``--pacbio``                | Specifies that the given FASTQ files are from PacBio                                                                                    | ``--pacbio``                                                            | N/A                 | N/A                | ``metacerberus.py --pacbio``                                                              |  
+-----------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------+---------------------+--------------------+-------------------------------------------------------------------------------------------+

**Output options:**
------------------------
+-----------------+-------------------------------------------------------------------------------------------------------------+----------------------+----------------------------+--------------------+---------------------------------------+
| Argument/Option | Function [DEFAULT]                                                                                          | Usage Format         | Accepted format            | # Options Accepted | Example (Type as one line)            |
+-----------------+-------------------------------------------------------------------------------------------------------------+----------------------+----------------------------+--------------------+---------------------------------------+
| ``--dir-out``   | path to output directory, defaults to "results-metacerberus" in current directory. [./results-`]            | ``--dir-out DIR_OUT``| output file path           | 1                  | ``--dir-out path/to/output/file``     |
+-----------------+-------------------------------------------------------------------------------------------------------------+----------------------+----------------------------+--------------------+---------------------------------------+
| ``--replace``   | Flag to replace existing files. [False]                                                                     | ``--replace``        | ``metacerberus.py`` option | N/A                | ``metacerberus.py --replace``         |
+-----------------+-------------------------------------------------------------------------------------------------------------+----------------------+----------------------------+--------------------+---------------------------------------+
| ``--keep``      | Flag to keep temporary files. [False]                                                                       | ``--keep``           | ``metacerberus.py`` option | N/A                | ``metacerberus.py --keep``            | 
+-----------------+-------------------------------------------------------------------------------------------------------------+----------------------+----------------------------+--------------------+---------------------------------------+
| ``--tmpdir``    | Temp directory for RAY (experimental) [system tmp dir]                                                      | ``--tmpdir TMPDIR``  | ``metacerberus.py`` option | 1                  | ``metacerberus.py --tmpdir TEMPFILE1``|
+-----------------+-------------------------------------------------------------------------------------------------------------+----------------------+----------------------------+--------------------+---------------------------------------+

**Database options:**
-------------------------
+----------------+-----------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+------------------------------------------------------+
|Argument/Option | Function [DEFAULT]                                                                                        | Usage Format            | Accepted format            | # Options Accepted | Example (Type as one line)                           |
+----------------+-----------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+------------------------------------------------------+
| ``--hmm``      | A list of databases for HMMER. Use the option ``--list-db`` for a list of available databases [KOFam_all] | ``--hmm HMM [HMM ...]`` | ``metacerberus.py`` option | =>1                | ``metacerberus.py --hmm DATABASE1 DATABASE2...``     |
+----------------+-----------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+------------------------------------------------------+
| ``--db-path``  | Path to folder of databases [Default: under the library path of metacerberus]                             | ``--db-path DB_PATH``   | path to databases folder   | 1                  | ``--db-path path/to/databases/folder``               | 
+----------------+-----------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+------------------------------------------------------+

**Optional Arguments:** 
--------------------------- 
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
|Argument/Option          | Function [DEFAULT]                                                                                                        | Usage Format            | Accepted format            | # Options Accepted | Example (Type as one line)                         |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--meta``              | Metagenomic nucleotide sequences **(for prodigal)** [False]                                                               | ``--meta``              | ``metacerberus.py`` option | N/A                | ``metacerberus.py --meta``                         |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--scaffolds``         | Sequences are treated as scaffolds [False]                                                                                | ``--scaffolds``         | ``metacerberus.py`` option | N/A                | ``metacerberus.py --scaffolds``                    |  
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--minscore``          | Score cutoff for parsing HMMER results [60]                                                                               | ``--minscore MINSCORE`` | whole integer value        | 1                  | ``metacerberus.py --minscore 50``                  |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--evalue``            | E-value cutoff for parsing HMMER results [1e-09]                                                                          | ``--evalue EVALUE``     | E-value                    | 1                  | ``metacerberus.py --evalue [E-value]``             | 
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--skip-decon``        | Skip decontamination step. [False]                                                                                        | ``--skip-decon``        | ``metacerberus.py`` option | N/A                | ``metacerberus.py --skip-decon``                   |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--skip-pca``          | Skip PCA. [False]                                                                                                         | ``--skip-pca``          | ``metacerberus.py`` option | N/A                | ``metacerberus.py --skip-pca``                     | 
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--cpus``              | Number of CPUs to use per task. System will try to detect available CPUs if not specified [Auto Detect]                   | ``--cpus CPUS``         | whole integer value        | 1                  | ``metacerberus.py --cpus 16``                      |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--chunker``           | Split files into smaller chunks, in Megabytes [Disabled by default]                                                       | ``--chunker CHUNKER``   | whole integer value        | 1                  | ``metacerberus.py --chunker 300``                  |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--grouped``           | Group multiple fasta files into a single file before processing. When used with `--chunker` (see above) can improve speed | ``--grouped``           | ``metacerberus.py`` option | N/A                | ``metacerberus.py --grouped``                      | 
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--version`` or ``-v`` | show the version number and exit                                                                                          | ``--version`` or ``-v`` | ``metacerberus.py`` option | N/A                | ``metacerberus.py --version``                      |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``-h`` or ``--help``    | show this help message and exit                                                                                           | ``-h`` or ``--help``    | ``metacerberus.py`` option | N/A                | ``metacerberus.py -h``                             |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--adapters``          | FASTA File containing adapter sequences for trimming                                                                      | ``--adapters ADAPTERS`` | FASTA file                 | 1                  | ``metacerberus.py --adapters /path/to/FASTA/file`` |   
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+
| ``--qc_seq``            | FASTA File containing control sequences for decontamination                                                               | ``--qc_seq QC_SEQ``     | FASTA file                 | 1                  | ``metacerberus.py --qc_seq /path/to/FASTA/file``   |
+-------------------------+---------------------------------------------------------------------------------------------------------------------------+-------------------------+----------------------------+--------------------+----------------------------------------------------+

.. note::
   Arguments/options that start with ``--`` can also be set in a config file (specified via ``-c``). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see `syntax`_. In general, **command-line values override config file values which override defaults.**
.. _syntax: https://goo.gl/R74nmi

Outputs (/final folder)
==========================

+----------------+----------------------------------------------------------------------------------------+----------------------------+
| File extension | Description Summary                                                                    | MetaCerberus Update Version|
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| .gff	        | General Feature Format	                                                                | 1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| .gbk	        |  GenBank Format      	                                                                | 1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| .fna	        |   Nucleotide FASTA file of the input contig sequences.                                 |	1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| .faa	        | Protein FASTA file of the translated CDS/ORFs sequences.                               |	1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| .ffn	        |  FASTA Feature Nucleotide file, the Nucleotide sequence of translated CDS/ORFs.        |	1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| .html 	        |  Summary statistics and/or visualizations, in step 10 folder                           |	1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| .txt           |	Statistics relating to the annotated features found.                                 |	1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| level.tsv	     |  Various levels of hierachical steps that is tab-separated file from various databases |	1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| rollup.tsv     |  	All levels of hierachical steps that is tab-separated file from various databases    |	1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+
| .tsv           | 	Final Annotation summary, Tab-separated file of all features from various databases  |	1.3                        |
+----------------+----------------------------------------------------------------------------------------+----------------------------+



GAGE/Pathview
===============

- After processing the HMM files, MetaCerberus calculates a KO (KEGG Orthology) counts table from KEGG/FOAM for processing through GAGE and PathView.
- GAGE is recommended for pathway enrichment followed by PathView for visualizing the metabolic pathways. A "class" file is required through the ``--class`` option to run this analysis. 

.. :tip::
   As we are unsure which comparisons you want to make thus, you have to make a class.tsv so the code will know the comparisons you want to make. 

For example (class.tsv):
-------------------------------
+---------+--------------+
| Sample  |   Class      |
+---------+--------------+
| 1A      | rhizobium    |
+---------+--------------+
| 1B      | non-rhizobium|
+---------+--------------+

- The output is saved under the step_10-visualizeData/combined/pathview folder. Also, **at least 4 samples** need to be used for this type of analysis.  
- GAGE and PathView also **require internet access** to be able to download information from a database. 
- MetaCerberus will save a bash script 'run_pathview.sh' in the step_10-visualizeData/combined/pathview directory along with the KO Counts tsv files and the class file for running manually in case MetaCerberus was run on a cluster without access to the internet.

Multiprocessing MultiComputing with RAY
===========================================

- MetaCerberus uses Ray for distributed processing. This is compatible with both multiprocessing on a single node (computer) or multiple nodes in a cluster.  
MetaCerberus has been tested on a cluster using `Slurm`_.  

.. _Slurm: https://github.com/SchedMD/slurm

.. :important::
   A script has been included to facilitate running MetaCerberus on Slurm. To use MetaCerberus on a Slurm cluster, setup your slurm script and run it using ``sbatch``.  

Example command to run your slurm script:
-----------------------------------------
::

   sbatch example_script.sh


Example Script:  
-------------------
::

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

DESeq2 and Edge2 Type I errors
==================================

Both edgeR and DeSeq2 R have the highest sensitivity when compared to other algorithms that control type-I error when the FDR was at or below 0.1. EdgeR and DESeq2 all perform fairly well in simulation and via data splitting (so no parametric assumptions). Typical benchmarks will show limma having stronger FDR control across all types of datasets (it’s hard to beat the moderated t-test), and edgeR and DESeq2 having higher sensitivity for low counts (makes sense as limma has to filter these out / down-weight them to use the normal model on log counts). Further information about type I errors are present from Mike Love's vignette `here`_.

.. _here: https://bioconductor.org/packages/devel/bioc/vignettes/DESeq2/inst/doc/DESeq2.html#multi-factor-designs


Contributing to MetaCerberus and Fungene
===========================================

MetaCerberus as a community resource as recently acquired `FunGene`_, we welcome contributions of other experts expanding annotation of all domains of life (viruses, bacteria, archaea, eukaryotes).  Please send us an issue on our MetaCerberus GitHub `open an issue`_; or email us we will fully annotate your genome, add suggested pathways/metabolisms of interest, make custom HMMs to be added to MetaCerberus and FunGene. 

.. _FunGene: http://fungene.cme.msu.edu/
.. _open an issue: https://github.com/raw-lab/metacerberus/issues

Copyright
===========

This is copyrighted by University of North Carolina at Charlotte, Jose L Figueroa III, Eliza Dhungal, Madeline Bellanger, Cory R Brouwer and Richard Allen White III. All rights reserved. MetaCerberus is a bioinformatic tool that can be distributed freely for academic use only. Please contact us for commerical use. The software is provided “as is” and the copyright owners or contributors are not liable for any direct, indirect, incidental, special, or consequential damages including but not limited to, procurement of goods or services, loss of use, data or profits arising in any way out of the use of this software.

Citing MetaCerberus
======================

If you are publishing results obtained using MetaCerberus, please cite:

Publication
-------------
Figueroa III JL, Dhungel E, Bellanger M, Brouwer CR, White III RA. 2024.
MetaCerberus: distributed highly parallelized HMM-based processing for robust functional annotation across the tree of life. `Bioinformatics`_.

.. _Bioinformatics: https://doi.org/10.1093/bioinformatics/btae119

Pre-print
------------
Figueroa III JL, Dhungel E, Brouwer CR, White III RA. 2023.
MetaCerberus: distributed highly parallelized HMM-based processing for robust functional annotation across the tree of life. `bioRxiv`_.

.. _bioRxiv: https://www.biorxiv.org/content/10.1101/2023.08.10.552700v1

Contact Us
=============

The informatics point-of-contact for this project is `Dr. Richard Allen White III`_.  
If you have any questions or feedback, please feel free to get in touch by email.  

`Dr. Richard Allen White III <email_>`_ 

`Jose Luis Figueroa III`_

Or `open an issue`_.  

.. _Dr. Richard Allen White III: https://github.com/raw-lab
.. _email: mailto:rwhit101@charlotte.edu
.. _Jose Luis Figueroa III: mailto:jlfiguer@charlotte.edu
.. _open an issue: https://github.com/raw-lab/metacerberus/issues


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
