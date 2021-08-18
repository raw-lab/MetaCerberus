# -*- coding: utf-8 -*-
"""rheaFormat.py: Module for reformating FASTQ files to FASTA files
Also removes N's

"""

import os
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


def splitSequence(name, sequence):
    sequences = sequence.split("N")
    sequences = [seq for seq in sequences if len(seq)>0]
    name = name.split()
    basename = name[0]
    info = ' '.join(name[1:])
    seqs = []
    for i, seq in enumerate(sequences, 1):
        n = f">{basename}_{i} {info}"
        seqs.append(n)
        seqs += textwrap.wrap(seq, 80)
    return seqs


# Remove N's
def removeN(fasta, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)    

    outFasta, ext = os.path.splitext(fasta)
    outFasta = os.path.basename(outFasta) + "_clean"+ ext
    outFasta = os.path.join(path, outFasta)

    if not config['REPLACE'] and os.path.exists(outFasta):
        return outFasta

    with open(fasta) as reader, open(outFasta, 'w') as writer:
        name = ""
        line = reader.readline().strip()
        while line:
            if line.startswith('>'):
                name = line[1:]
                sequence = ""
                line = reader.readline().strip()
                while line:
                    if line.startswith('>'):
                        break
                    sequence += line.strip()
                    line = reader.readline().strip()
                if 'N' in sequence:
                    sequences = splitSequence(name, sequence)
                    print('\n'.join(sequences), file=writer)
                else:
                    print('>', name, sep='', file=writer)
                    print('\n'.join(textwrap.wrap(sequence, 80)), file=writer)
            line = reader.readline().strip()

    return outFasta


    proteins = {}
    with open(fasta) as fileIn, open(outFasta, 'w') as reader:
        name = ""
        line = reader.readline()
        while line:
            if line.startswith('>'):
                name = line[1:].rstrip().split(sep=None, maxsplit=1)[0]
                length = 0
                line = reader.readline()
                while line:
                    if line.startswith('>'):
                        break
                    length += len(line.strip())
                    line = reader.readline()
                proteins[name] = dict(count=0, found=0, length=length)
                continue
            line = reader.readline()
    return outFasta
