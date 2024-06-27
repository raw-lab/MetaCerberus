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
