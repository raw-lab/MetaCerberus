# -*- coding: utf-8 -*-
"""metacerberus_decon.py: Module to clean trimmed .fastq files
Uses bbduk [https://sourceforge.net/projects/bbmap/]
"""

import os
from pathlib import Path
import subprocess


# Decontaminate single end reads
def deconSingleReads(key_value, config, subdir):
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

    qc_seq = "ref="+config['QC_SEQ'] if config['QC_SEQ'] else ""

    command = [config['EXE_BBDUK'], "-Xmx1g", f"in={value}", f"out={deconReads}", "qin=30", "qtrim=r", "minlen=50", "k=31", qc_seq, "hdist=1", f"stats={stats}"]
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        print("ERROR: Failed to execute:\n", command)

    done.touch()
    return deconReads
