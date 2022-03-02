# -*- coding: utf-8 -*-
"""cerberus_formatFasta.py: Module for reformating FASTQ files to FASTA files
Also removes N's from scaffolds
"""

import os
import re
import subprocess
import textwrap


## format_fastq
def reformat(fastq, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)    

    fasta, ext = os.path.splitext(fastq)
    fasta = os.path.basename(fasta) + ".fna"
    fasta = os.path.join(path, fasta)

    if not config['REPLACE'] and os.path.exists(fasta):
        return fasta

    command = "sed -n '1~4s/^@/>/p;2~4p' " +fastq+ " > " +fasta
    subprocess.call(command, shell=True)
    return fasta


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
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)    

    outFasta, ext = os.path.splitext(fasta)
    outFasta = os.path.basename(outFasta) + "_clean"+ ext
    outFasta = os.path.join(path, outFasta)

    proc = subprocess.run(['grep', '-cE', '^[^>].*N', fasta], stdout=subprocess.PIPE, text=True)
    res = int(proc.stdout.strip())
    if res == 0:
        return fasta, None

    with open(fasta) as reader, open(outFasta, 'w') as writer:
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

    return outFasta, NStats
