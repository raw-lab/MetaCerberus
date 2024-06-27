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
