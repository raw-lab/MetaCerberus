# -*- coding: utf-8 -*-
"""rheaQC.py: Module for checking quality of .fastq files
Uses FastQC [https://www.bioinformatics.babraham.ac.uk/projects/fastqc/]
$ fastqc file.fastq
$ fastqc file_R1.fastq fastqc file_R2.fastq
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

    print(__name__)

    command = f"{config['EXE_FASTQC']} -o {path} {singleRead}"
    with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)

    return


## checkPairedQuality
#
def checkPairedRead(pairedRead, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    
    command = f"{config['EXE_FASTQC']} -o {path} {pairedRead[0]} {pairedRead[1]}"
    with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)

    return


## End of script
