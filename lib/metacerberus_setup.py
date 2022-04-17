# -*- coding: utf-8 -*-

"""metacerberus_setup.py: Module for seting up dependencies
"""

import os
import shutil
import subprocess
import urllib.request as url
from git import Repo


# Download Database
def Download(pathDB):
    os.makedirs(pathDB, exist_ok=True)
    print(f"Downloading Database files to {pathDB}")
    print("This will take a few minutes...")
    url.urlretrieve("https://osf.io/72p6g/download", os.path.join(pathDB, "FOAM_readme.txt"))
    url.urlretrieve("https://osf.io/muan4/download", os.path.join(pathDB, "FOAM-onto_rel1.tsv"))
    url.urlretrieve("https://osf.io/2hp7t/download", os.path.join(pathDB, "KEGG-onto_rel1.tsv"))
    url.urlretrieve("https://osf.io/bdpv5/download", os.path.join(pathDB, "FOAM-hmm_rel1a.hmm.gz"))
    return


# Clone Frag Gene Scan Plus
def FGS(pathFGS):
    os.makedirs(pathFGS, exist_ok=True)
    print(f"Cloning FGS+ to {pathFGS}")
    try:
        Repo.clone_from("https://github.com/hallamlab/FragGeneScanPlus", pathFGS)
    except:
        print("Cloning repo failed, possibly already exists")
    #rm -rf "$fgspath/.git*"
    subprocess.run(f'make CFLAG="-fcommon -w" -C "{pathFGS}"', shell=True)
    return


# Remove Database and FGS+
def Remove(pathDB, pathFGS):
    shutil.rmtree(pathDB, ignore_errors=True)
    shutil.rmtree(pathFGS, ignore_errors=True)
    return
