A Look at the Results folder - Tutorial
=========================================

Now that we've run the MetaCerberus pipeline, let's take a look at the results folder. Having ran the ``--super`` option on my data, the results folder looks like so:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/results_folder.jpg
    :width: 600
Now a closer look at each subdirectory of our results:

Step 5 - Format:
-------------------

.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/step_5_outputs.jpg
    :width: 600
Step 5 contents only consist of a ``complete`` file, which merely indicates Step 5 ran to completion.

Step 6 - MetaomeQC
-------------------
Here are the contents of ``step_06-metaomeQC``:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/S6_contents.jpg
    :width: 600
The file ``read-stats.txt`` contains statistics for your input file, like so:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/step6-read-stats-txt.jpg

.. note:: The file ``stderr.out`` is a log file where any error messages will be stored.

Step 7 - Gene Call
-------------------
Contents of the ``step_07-geneCall`` directory are:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/Step7_contents.jpg
    :width: 600
These are protein files in different formats. 

Step 8 - HMMER
------------------
Contents of the ``step_08-hmmer`` directory are:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/Step8_contents.jpg
    :width: 600

For your MetaCerberus run, you should get a subdirectory for the mode that MetaCerberus used (FragGeneScan, Prodigal, Prodigalgv, etc).
In this example run, we have several file outputs for FragGeneScan. This is what they look like:

.. note:: ``.tsv`` files can be opened with Excel. 

``KOFam_all_FOAM-FragGeneScan_Lambda_phage_sequences.tsv``:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/S8-KOFam_FOAM_FGS_tsv.jpg

``KOFam_all_KEGG-FragGeneScan_Lambda_phage_sequences.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S8-FGS-KOFam-KEGG_tsv.png

``filtered-KOFam_all_FOAM.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S8-filtered-KOFam-FOAM_tsv.png

``filtered-KOFam_all_KEGG.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S8-filtered-KOFam-allKEGG_tsv.png

``filtered.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S8-filtered_tsv.png

Step 9 - Parse
------------------
The contents of ``step_09-parse`` are:

.. image::  https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9_contents.png

Looking a little closer: 

``HMMER-KOFam_all_FOAM_top_5.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9-HMMR-KOFam_allFOAM_top5_tsv.png

``HMMER-KOFam_all_KEGG_top_5.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9-HMMR_KOFam_allKEGG_top5_tsv.png

``HMMER_BH_KOFam_all_FOAM_rollup2.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9-HMMR_BH_KOFam_FOAM_rollup2_tsv.png

``HMMER_BH_KOFam_all_KEGG_rollup2.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9-HMMR_BH_KOFam_all_KEGG_rollup2_tsv.png

``HMMER_top_5.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9_HMMR_top_5.tsv.png

``KOFam_all_FOAM-rollup_counts.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9_KOFam_all_FOAM_rollup_counts_tsv.png

``KOFam_all_KEGG-rollup_counts.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9-KOFam_allKEGG_rollup_counts_tsv.png

``counts_KOFam_all_FOAM.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9-counts_KOFam_allFOAM_tsv.png

``counts_KOFam_all_KEGG.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9-counts_KOFam_all_KEGG_tsv.png

``top_5-FragGeneScan_Lambda_phage_sequences.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S9-top5_FGS_tsv.png

Step 10 - Visualize data
--------------------------

The contents of ``step_10-visualizeData`` are:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10-contents.png

What's in the FragGeneScan and Prodigal subdirectories?

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10-FGS-Prod-contents.png

Files under FragGeneScan or Prodigal:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``KOFam_all_FOAM_level-1.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10-KOFam_all_FOAM_level-1_tsv.png

``KOFam_all_FOAM_level-2.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10-KOFam_all_FOAM_lvl2_tsv.png

``KOFam_all_FOAM_level-3.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10-KOFam_all_FOAM_lvl3_tsv.png

``KOFam_all_FOAM_level-4.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10-KOFam_all_FOAM_lvl4_tsv.png

``KOFam_all_FOAM_level-id.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/3e91770cd2d54b7c36e0c1d638a2a69f9c6a044e/img/MetaCerberus_tutorial_imgs/S10_KOFam_all_FOAM_lvl_id_tsv.png

``KOFam_all_KEGG_level-1.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10-KOFam_all_KEGG_lvl1_tsv.png

``KOFam_all_KEGG_level-2.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10-KOFam_all_KEGG_lvl2_tsv.png

``KOFam_all_KEGG_level-3.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10_KOFam_all_KEGG_lvl3_tsv.png

``KOFam_all_KEGG_level-id.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10_KOFam_all_KEGG_lvl-ID_tsv.png

``fasta_stats.txt``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10_fasta_stats_txt.png

``sunburst_KOFam_all_FOAM.html`` --- open in web browser

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10_Sunburst_KOFam_all_FOAM_html.png

``sunburst_KOFam_all_KEGG.html`` --- open in web browser

.. image:: https://github.com/raw-lab/MetaCerberus/blob/a9bf37c3c7b779f947ced69688edca7f6c7349ee/img/MetaCerberus_tutorial_imgs/S10_Sunburst_KOFam_all_KEGG_html.png

Contents under ``combined``:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
At a glance:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/3e91770cd2d54b7c36e0c1d638a2a69f9c6a044e/img/MetaCerberus_tutorial_imgs/S10_combined_contents.png

``counts_KOFam_all_FOAM.tsv``    

.. image:: https://github.com/raw-lab/MetaCerberus/blob/3e91770cd2d54b7c36e0c1d638a2a69f9c6a044e/img/MetaCerberus_tutorial_imgs/step10-combined-countsKOFamFOAM.png

``counts_KOFam_all_KEGG.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/3fced4c46750fac4aa1015e730b3be0c77022052/img/MetaCerberus_tutorial_imgs/S10_combined_counts_KOFam_all_KEGG_tsv.png

``stats.html`` --- open in web browser

.. image:: https://github.com/raw-lab/MetaCerberus/blob/3e91770cd2d54b7c36e0c1d638a2a69f9c6a044e/img/MetaCerberus_tutorial_imgs/S10_combined_stats_html.png

``stats.tsv``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/3e91770cd2d54b7c36e0c1d638a2a69f9c6a044e/img/MetaCerberus_tutorial_imgs/S10_Stats_tsv.png

``img`` --- contains the individual .png image files which are collectively located in ``stats.html``

.. image:: https://github.com/raw-lab/MetaCerberus/blob/3e91770cd2d54b7c36e0c1d638a2a69f9c6a044e/img/MetaCerberus_tutorial_imgs/S10_combined_img_contents.png

Final
-------------------
The contents of ``final`` are:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/3fced4c46750fac4aa1015e730b3be0c77022052/img/MetaCerberus_tutorial_imgs/Final_contents.png




````
    .. image::