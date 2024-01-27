# -*- coding: utf-8 -*-
"""metacerberus_formatFasta.py: Module for reformating FASTQ files to FASTA files
Also removes N's from scaffolds
"""

import os
from pathlib import Path
import re
import subprocess
import textwrap


# Remove quality from fastq
def reformat(fastq:Path, config:dict, subdir:Path):
    path = Path(config['DIR_OUT'], subdir)

    fasta = Path(path, fastq.name).with_suffix(".fna")

    done = Path(path, 'complete')
    if not config['REPLACE'] and done.exists() and fasta.exists():
        return fasta
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    if not config['REPLACE'] and os.path.exists(fasta):
        return fasta

    command = "sed -n '1~4s/^@/>/p;2~4p' " +fastq.as_posix()+ " > " +fasta.as_posix()
    subprocess.call(command, shell=True)

    done.touch()
    return fasta


# Helper for removeN
def split_sequenceN(name, sequence):
    N_lengths = []
    regex = re.compile(r"(N+)")
    for match in regex.finditer(sequence):
        N_lengths.append(len(match.group(1)))
    sequences = regex.sub('\n', sequence).split('\n')
    name = name.split()
    basename = name[0]
    info = ' '.join(name[1:])
    seqs = []
    for i, seq in enumerate(sequences, 1):
        header = f">{basename}_{i} {info}"
        seqs.append(header)
        seqs += textwrap.wrap(seq, 80)
    
    return seqs, N_lengths


# Remove N's
def removeN(fasta:str, config:dict, subdir:os.PathLike):
    path = Path(config['DIR_OUT'], subdir)

    outFasta, ext = os.path.splitext(fasta)
    outFasta = os.path.basename(outFasta) + "_clean"+ ext
    outFasta = Path(path, outFasta)

    done = Path(path, 'complete')
    if not config['REPLACE'] and done.exists() and outFasta.exists():
        return outFasta, None
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    proc = subprocess.run(['grep', '-cE', '^[^>].*N', fasta], stdout=subprocess.PIPE, text=True)
    res = int(proc.stdout.strip())
    if res == 0:
        done.touch()
        return fasta, None

    with open(fasta) as reader, outFasta.open('w') as writer:
        NStats = dict()
        line = reader.readline()
        while line:
            line = line.strip()
            if line.startswith('>'):
                name = line[1:]
                sequence = ""
                line = reader.readline()
                while line:
                    line = line.strip()
                    if line.startswith('>'):
                        break
                    sequence += line
                    line = reader.readline()
                if 'N' in sequence:
                    sequences, stats = split_sequenceN(name, sequence)
                    NStats[name] = stats
                    print('\n'.join(sequences), file=writer)
                else:
                    print('>', name, sep='', file=writer)
                    print('\n'.join(textwrap.wrap(sequence, 80)), file=writer)
                continue #already got next line, next item in loop
            line = reader.readline()

    done.touch()
    return outFasta, NStats
