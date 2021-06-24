# -*- coding: utf-8 -*-
"""rheaFormat.py: Module for reformating FASTQ files to FASTA files
Also removes N's

"""

import os
import subprocess
import textwrap


# trimReads
def reformat(fastq, config, subdir):
    return format_fastq(fastq, config, subdir)
    

## format_fastq
def format_fastq(fastq, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)    

    fasta, ext = os.path.splitext(fastq)
    fasta = os.path.basename(fasta) + ".fna"
    fasta = os.path.join(path, fasta)

    command = "sed -n '1~4s/^@/>/p;2~4p' " +fastq+ " > " +fasta
    subprocess.call(command, shell=True)
    return fasta


# Remove N's
def removeN(fasta, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)    

    outFasta, ext = os.path.splitext(fasta)
    outFasta = os.path.basename(outFasta) + "_clean"+ ext
    outFasta = os.path.join(path, outFasta)

    with open(fasta) as fileIn, open(outFasta, 'w') as fileOut:
        counter = 0
        sequence = ""
        for line in fileIn:
            line = line.strip()
            if line.startswith('>'):
                if counter == 0:
                    counter = 1
                else:
                    sequences = sequence.split("N")
                    sequences = [s for s in sequences if len(s)>0]
                    for seq in sequences:
                        fileOut.write(f">seq{counter}\n")
                        fileOut.write('\n'.join(textwrap.wrap(seq, 80)))
                        fileOut.write('\n')
                        counter += 1
                sequence = ""
            else:
                sequence += line
        sequences = sequence.split("N")
        sequences = [s for s in sequences if len(s)>0]
        for seq in sequences:
            fileOut.write(f">seq{counter}\n")
            fileOut.write('\n'.join(textwrap.wrap(seq, 80)))
            fileOut.write('\n')
            counter += 1
    return outFasta
