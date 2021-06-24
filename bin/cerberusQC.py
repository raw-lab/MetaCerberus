# -*- coding: utf-8 -*-
"""rheaQC.py: Module for checking quality of .fastq files
Uses FastQC [https://www.bioinformatics.babraham.ac.uk/projects/fastqc/]
$ fastqc file.fastq
$ fastqc file_R1.fastq fastqc file_R2.fastq
"""

import os
import subprocess


## checkQuality
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
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')
    command = f"{config['EXE_FASTQC']} -o {path} {singleRead}"
    subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    fout.close()
    ferr.close()
    return


## checkPairedQuality
#
def checkPairedRead(pairedRead, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')
    command = f"{config['EXE_FASTQC']} -o {path} {pairedRead[0]} {pairedRead[1]}"
    subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    fout.close()
    ferr.close()
    return


## End of script
