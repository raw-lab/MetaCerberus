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
