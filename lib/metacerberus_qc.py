# -*- coding: utf-8 -*-
"""metacerberus_qc.py: Module for checking quality of .fastq files
Uses FastQC [https://www.bioinformatics.babraham.ac.uk/projects/fastqc/]
"""

import os
import subprocess
import hydraMPP


## Check quality
@hydraMPP.remote
def checkQuality(rawRead, fastq_path, outpath):
    if type(rawRead) is list or type(rawRead) is tuple:
        return checkPairedRead(rawRead, fastq_path, outpath)
    else:
        return checkSingleRead(rawRead, fastq_path, outpath)


# Check single end quality
def checkSingleRead(singleRead, fastq_path, outpath):
    
    os.makedirs(outpath, exist_ok=True)
    
    if not fastq_path:
        return None

    command = f"{fastq_path} -o {outpath} {singleRead}"
    try:
        with open(f"{outpath}/stdout.txt", 'w') as fout, open(f"{outpath}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
        return os.path.join(outpath, os.path.splitext(os.path.basename(singleRead))[0]+'_fastqc.html')
    except Exception as e:
        print(e)

    return None


# Check paired end quality
def checkPairedRead(pairedRead, fastq_path, outpath):
    
    os.makedirs(outpath, exist_ok=True)

    if not fastq_path:
        return None

    command = f"{fastq_path} -o {outpath} {pairedRead[0]} {pairedRead[1]}"
    try:
        with open(f"{outpath}/stdout.txt", 'w') as fout, open(f"{outpath}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)

    return outpath


## End of script
