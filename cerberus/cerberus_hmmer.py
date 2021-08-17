# -*- coding: utf-8 -*-

"""cerberusHMMER.py Script to find proteins using HMMER

$ hmmsearch --cpu 12 --domtblout fastaFile.FOAM.out databaseFile aminoAcids.faa
"""

import os
import subprocess


## HMMER Search
def searchHMM(aminoAcid, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    foamDB = f'{config["PATH"]}/cerberusDB/FOAM-hmm_rel1a.hmm.gz'
    name = os.path.basename(path)
    name = os.path.splitext(name)[0] + ".FOAM.out"
    foamOut = os.path.join(path, name)

    if not config['REPLACE'] and os.path.exists(foamOut):
        return foamOut
    
    # HMMER
    try:
        command = f"{config['EXE_HMMSEARCH']} --cpu {config['CPUS']} --domtblout {foamOut} {foamDB} {aminoAcid}"
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=ferr)
            #TODO: Add option to redirect output to file
    except Exception as e:
        print(e)
        print("Error: failed to run: " + command)

    return foamOut
