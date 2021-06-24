# -*- coding: utf-8 -*-


import os
import subprocess


## findORF
def findORF(contig, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')

    # Prodigal
    try:
        command = f"{config['EXE_PRODIGAL']} -i {contig} -o {path}/genes.gff -a {path}/proteins.faa -f gff"
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except:
        print("Error: failed to run: " + command)


    fout.close()
    ferr.close()
    return f"{path}/proteins.faa"
