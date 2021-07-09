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

    with open(fasta) as fileIn, open(outFasta, 'w') as fileOut:
        name = ""
        sequence = ""
        for line in fileIn:
            line = line.strip()
            if line.startswith('>'):
                if len(name) > 0:
                    sequences = splitSequence(name, sequence)
                    fileOut.write('\n'.join(sequences))
                name = line[1:]
                sequence = ""
            else:
                sequence += line
        sequences = splitSequence(name, sequence)
        fileOut.write('\n'.join(sequences))
    return outFasta