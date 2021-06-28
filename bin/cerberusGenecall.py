# -*- coding: utf-8 -*-


import os
import subprocess


# Microbial option
def findORF_mic(contig, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')

    
    try:
        command = f"{config['EXE_PRODIGAL']} -i {contig} -o {path}/genes.gff -a {path}/proteins.faa -f gff"
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except:
        print("Error: failed to run: " + command)
    
    fout.close()
    ferr.close()
    return f"{path}/proteins.faa"


# Eukaryotic option
def findORF_euk(contig, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')

    FGStrain = f"{os.path.dirname(config['EXE_FGS+'])}/train"

    command = f"{config['EXE_FGS+']} -s {contig} -o {path}/proteins -w 0 -r {FGStrain} -t 454_5"
    subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)

    fout.close()
    ferr.close()
    return f"{path}/proteins.faa"
