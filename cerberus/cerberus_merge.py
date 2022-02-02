# -*- coding: utf-8 -*-
"""cerberus_merge.py: Module to merge paired end .fastq files
Uses flash [https://github.com/dstreett/FLASH2]
"""

import os
import subprocess


## mergePairedEnd
#
def mergePairedEnd(pairedFastq, config, subdir):
    # TODO: Find good long read mapper
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    R1 = pairedFastq[0]
    R2 = pairedFastq[1]

    prefix = os.path.basename(R1)

    command = f"{config['EXE_FLASH']} {R1} {R2} -d {path} -o {prefix} -M 150"
    with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)

    merged = os.path.join(path, prefix.replace('_R1', '_merged'))
    if os.path.exists(merged):
        os.remove(merged)
    command = f"cat {path}/*.fastq > {merged}"
    subprocess.run(command, shell=True, check=True)

    return merged
