MetaCerberus Tutorial - Installation
=======================================

STEP 0: Installation
--------------------------
Windows/Ubuntu
~~~~~~~~~~~~~~~

Installing MetaCerberus 1.3 manually due to Mamba/Conda issue (Newest Version)

These are the commands you will use to install MetaCerberus:
::

  git clone https://github.com/raw-lab/MetaCerberus.git 
  cd metacerberus
  bash install_metacerberus.sh
  conda activate MetaCerberus-1.3.0
  metacerberus.py --download

After the ``git clone http://github.com/raw-lab/MetaCerberus.git`` command, you will see:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/Gitclone_result_install.jpg
    :width: 600
    :loading: embed

Then proceed to next part of command:


.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/cd-MC-bash_install_metacerberus.jpg


This command will result in installation of MetaCerberus, which looks like this once completed:

.. figure:: ../img/install_MC_results.jpg
    :width: 600


.. image:: https://github.com/raw-lab/MetaCerberus/blob/1ce9498f026ccd44a68cd645103901f5a7542b48/readthedocs/img/install_MC_results.jpg
   :loading: embed

**Test image above**

Then we'll activate MetaCerberus, followed by downloaded the appropriate databases, like so:


.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/metacerberus.py%20--download.jpg
    :width: 600

Which will look like: 


.. image:: https://github.com/raw-lab/MetaCerberus/blob/main/readthedocs/img/metacerberus.py%20--download%20RESULT.jpg
    :width: 600


Now you're ready to run MetaCerberus!