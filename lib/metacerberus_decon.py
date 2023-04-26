# -*- coding: utf-8 -*-
"""metacerberus_decon.py: Module to clean trimmed .fastq files
Uses bbduk [https://sourceforge.net/projects/bbmap/]
"""

import os
from pathlib import Path
import subprocess


## deconSingleReads
#
def deconSingleReads(key_value, config, subdir):
    # TODO: Find good long read mapper
    path = Path(config['DIR_OUT'], subdir)

    key = key_value[0]
    value = key_value[1]

    deconReads = path / f"decon-{key}.fastq"
    matched = path / f"matched_{key}"
    stats = path / "stats.txt"

    done = path / "complete"
    if not config['REPLACE'] and done.exists() and deconReads.exists():
        return deconReads
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)


    refseq = "ref="+config['REFSEQ'] if config['REFSEQ'] else ""

    command = f"{config['EXE_BBDUK']} -Xmx1g in={value} out={deconReads} qin=33 qtrim=r minlen=50 outm={matched} {refseq} k=31 stats={stats}"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        print("ERROR: Failed to execute:\n", command)

    done.touch()
    return deconReads
