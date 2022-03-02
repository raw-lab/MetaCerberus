# -*- coding: utf-8 -*-
"""cerberus_genecall.py: Module for finding Open Reading Frames (ORF) in FASTA nucleotide files
Uses prodigal
Uses FGS+
"""

import os
import subprocess


# Eukaryotic option
def findORF_fgs(contig, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    FGStrain = f"{os.path.dirname(config['EXE_FGS+'])}/train"

    baseOut = f"{path}/proteins"
    faaOut = f"{baseOut}.faa"

    if not config['REPLACE'] and os.path.exists(faaOut):
        return faaOut

    # TODO: FGS+ freezes when using too many CPUs, try to find way around this or force to 1 CPU
    command = f"{config['EXE_FGS+']} -s {contig} -o {baseOut} -w 1 -r {FGStrain} -t complete"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        return None

    return faaOut


# Microbial option
def findORF_prod(contig, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')

    faaOut = f"{path}/proteins.faa"

    if not config['REPLACE'] and os.path.exists(faaOut):
        return faaOut

    command = f"{config['EXE_PRODIGAL']} -i {contig} -o {path}/genes.gff -a {faaOut} -f gff"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
    
    return faaOut


# Metagenome option
def findORF_meta(contig, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')

    faaOut = f"{path}/proteins.faa"

    if not config['REPLACE'] and os.path.exists(faaOut):
        return faaOut

    command = f"{config['EXE_PRODIGAL']} -i {contig} -o {path}/genes.gff -a {faaOut} -f gff -p meta"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)

    return faaOut
