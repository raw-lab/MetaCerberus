# -*- coding: utf-8 -*-

""" Script to find proteins using HMMER

$ hmmsearch --cpu 12 --domtblout fastaFile.FOAM.out databaseFile aminoAcids.faa
"""

import os
import subprocess


## HMMER Search
def search(aminoAcid, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    foamDB = f'{config["PATH"]}/cerberusDB/FOAM-hmm_rel1a.hmm.gz'
    name = os.path.basename(path)
    name = os.path.splitext(name)[0] + ".FOAM.out"
    foamOut = os.path.join(path, name)

    # HMMER
    with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
        try:
            command = f'hmmsearch --cpu {config["CPUS"]} --domtblout {foamOut} {foamDB} {aminoAcid}'
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
        except:
            print("Error: failed to run: " + command)

    return foamOut
