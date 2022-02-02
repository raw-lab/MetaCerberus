# -*- coding: utf-8 -*-
"""cerberus_decon.py: Module to clean trimmed .fastq files
Uses bbduk [https://sourceforge.net/projects/bbmap/]
"""

import os
import subprocess


## deconSingleReads
#
def deconSingleReads(key_value, config, subdir):
    # TODO: Find good long read mapper
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    key = key_value[0]
    value = key_value[1]

    deconReads = os.path.join(path, f"decon-{key}.fastq")
    matched = os.path.join(path, "matched_"+key)
    stats = os.path.join(path, "stats.txt")

    refseq = "ref="+config['REFSEQ'] if config['REFSEQ'] else ""

    command = f"{config['EXE_BBDUK']} -Xmx1g in={value} out={deconReads} qin=33 qtrim=r minlen=50 outm={matched} {refseq} k=31 stats={stats}"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        print("ERROR: Failed to execute:\n", command)

    return deconReads
