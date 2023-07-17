# -*- coding: utf-8 -*-
"""metacerberus_merge.py: Module to merge paired end .fastq files
Uses flash [https://github.com/dstreett/FLASH2]
"""

import os
from pathlib import Path
import subprocess


# Merge paired end reads
def mergePairedEnd(pairedFastq, config, subdir):
    path = Path(config['DIR_OUT'], subdir)

    R1 = pairedFastq[0]
    R2 = pairedFastq[1]
    prefix = os.path.basename(R1)
    merged = os.path.join(path, prefix.replace('_R1', '_merged'))
    merged = path / prefix.replace('_R1', '_merged')

    done = path / "complete"
    if not config['REPLACE'] and done.exists() and merged.exists():
        return merged
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    command = f"{config['EXE_FLASH']} {R1} {R2} -d {path} -o {prefix} -M 150"
    with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)

    command = f"cat {path}/*.fastq > {merged}"
    subprocess.run(command, shell=True, check=True)

    done.touch()
    return merged
