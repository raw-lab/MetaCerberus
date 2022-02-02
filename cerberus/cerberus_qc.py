# -*- coding: utf-8 -*-
"""cerberus_qc.py: Module for checking quality of .fastq files
Uses FastQC [https://www.bioinformatics.babraham.ac.uk/projects/fastqc/]
"""

import os
import subprocess


## checkQuality
#
def checkQuality(rawRead, config, subdir):
    if type(rawRead) is str:
        return checkSingleRead(rawRead, config, subdir)
    else:
        return checkPairedRead(rawRead, config, subdir)


## checkSingleQuality
#
def checkSingleRead(singleRead, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    
    command = f"{config['EXE_FASTQC']} -o {path} {singleRead}"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
        return os.path.join(path, os.path.splitext(os.path.basename(singleRead))[0]+'_fastqc.html')
    except Exception as e:
        print(e)

    return None


## checkPairedQuality
#
def checkPairedRead(pairedRead, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    
    command = f"{config['EXE_FASTQC']} -o {path} {pairedRead[0]} {pairedRead[1]}"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)

    return path


## End of script
