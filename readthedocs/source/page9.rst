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
