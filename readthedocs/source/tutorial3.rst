A Look at the Results folder - Tutorial
===================================

Now that we've run the MetaCerberus pipeline, let's take a look at the results folder. Having ran the `--super` option on my data, the results folder looks like so:
.. image:: https://github.com/raw-lab/MetaCerberus/blob/b9e782247b187a6bf0436a7776e32ce07193b322/img/MetaCerberus_tutorial_imgs/results_folder.png
    :width: 600
Now a closer look at each subdirectory of our results:

Step 5 - Format:
-------------------
.. image:: https://github.com/raw-lab/MetaCerberus/blob/e05bd6a59da4daed62ae39b4638471312db87d6e/img/MetaCerberus_tutorial_imgs/step_5_outputs.png
    :width: 600
Step 5 contents only consist of a `complete` file, which merely indicates Step 5 ran to completion.

Step 6 - MetaomeQC
-------------------
Here are the contents of `step_06-metaomeQC`:
.. image:: https://github.com/raw-lab/MetaCerberus/blob/5d2b110d0c50ef45920a85fdf60fc12389eccf31/img/MetaCerberus_tutorial_imgs/S6_contents.png
    :width: 600
The file `read-stats.txt` contains statistics for your input file, like so:
.. image:: https://github.com/raw-lab/MetaCerberus/blob/5d2b110d0c50ef45920a85fdf60fc12389eccf31/img/MetaCerberus_tutorial_imgs/step6-read-stats-txt.png

.. note:: The file ``stderr.out`` is a log file where any errors will be stored.

Step 7 - Gene Call
-------------------
Contents of the `step_07-geneCall` directory are:
.. image:: https://github.com/raw-lab/MetaCerberus/blob/31546be7ec23f8c86b6e431ad0d7e13ae00f3207/img/MetaCerberus_tutorial_imgs/Step7_contents.png
    :width: 600


Step 8 - HMMER
------------------


Step 9 - Parse
------------------

Step 10 - Visualize data
--------------------------

Final
-------------------
