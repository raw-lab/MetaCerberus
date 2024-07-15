MetaCerberus Tutorial - Installation
===================================

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

.. image:: https://github.com/raw-lab/MetaCerberus/blob/b9e782247b187a6bf0436a7776e32ce07193b322/img/MetaCerberus_tutorial_images/Gitclone_result_install.png
    :width: 600

Then proceed to next part of command:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/b9e782247b187a6bf0436a7776e32ce07193b322/img/MetaCerberus_tutorial_images/cd-MC-bash%20install_metacerberus.png
    :width: 600
This command will result in installation of MetaCerberus, which looks like this once completed:

.. image::https://github.com/raw-lab/MetaCerberus/blob/b9e782247b187a6bf0436a7776e32ce07193b322/img/MetaCerberus_tutorial_images/install_MC%20results.png
    :width: 600

Then we'll activate MetaCerberus, followed by downloaded the appropriate databases, like so:

.. image:: https://github.com/raw-lab/MetaCerberus/blob/b9e782247b187a6bf0436a7776e32ce07193b322/img/MetaCerberus_tutorial_images/metacerberus.py%20--download.png
    :width: 600

Which will look like: 

.. image:: https://github.com/raw-lab/MetaCerberus/blob/b9e782247b187a6bf0436a7776e32ce07193b322/img/MetaCerberus_tutorial_images/metacerberus.py%20--download%20RESULT.png
    :width: 600
Now you're ready to run MetaCerberus!