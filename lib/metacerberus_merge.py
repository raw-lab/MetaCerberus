# -*- coding: utf-8 -*-
"""metacerberus_merge.py: Module to merge paired end .fastq files
Uses flash [https://github.com/dstreett/FLASH2]
"""

import sys
import os
import re
from pathlib import Path
import subprocess


# Merge paired end reads
def mergePairedEnd(pairedFastq, config, subdir):
    outpath = Path(config['DIR_OUT'], subdir)

    R1 = pairedFastq[0]
    R2 = pairedFastq[1]
    prefix = os.path.basename(R1)
    merged = os.path.join(outpath, prefix.replace('_R1', '_merged'))
    merged = outpath / prefix.replace('_R1', '_merged')

    done = outpath / "complete"
    if not config['REPLACE'] and done.exists() and merged.exists():
        return merged
    done.unlink(missing_ok=True)
    outpath.mkdir(exist_ok=True, parents=True)

    #read stats
    lengths = list()
    for seq in [R1,R2]:
        with open(seq) as reader:
            line = reader.readline()
            while line:
                if re.search(r'^[+]$', line):
                    line = reader.readline().rstrip()
                    lengths += [len(line)]
                else:
                    seq = line.rstrip()
                    line = reader.readline()
    mu = round(sum(lengths) / len(lengths))
    var = sum([((x - mu)**2) for x in lengths]) / len(lengths)
    std = var**0.5
    _99th = round(mu + (3*std))
    print(R1, mu, var, std, _99th, max(lengths), file=sys.stderr)

    command = f"{config['EXE_FLASH']} {R1} {R2} -d {outpath} -o {prefix} -M {_99th} --interleaved-output"
    with open(f"{outpath}/stdout.txt", 'w') as fout, open(f"{outpath}/stderr.txt", 'w') as ferr:
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)

    command = f"cat {outpath}/*.fastq > {merged}"
    subprocess.run(command, shell=True, check=True)

    done.touch()
    return merged
