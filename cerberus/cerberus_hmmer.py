# -*- coding: utf-8 -*-

"""cerberusHMMER.py Script to find proteins using HMMER

$ hmmsearch --cpu 4 --domtblout fastaFile.FOAM.out databaseFile aminoAcids.faa
"""

import os
import subprocess
import time


## HMMER Search
def searchHMM(aminoAcids:dict, config:dict, subdir:str):
    hmmOut = []
    jobs = []
    for key,amino in aminoAcids.items():
        path = f"{config['DIR_OUT']}/{subdir}/{key}"
        os.makedirs(path, exist_ok=True)

        if config['HMM']:
            hmmDB = config['HMM']
        else:
            hmmDB = f'{config["PATH"]}/cerberusDB/FOAM-hmm_rel1a.hmm.gz'
        name = os.path.basename(amino)
        name = os.path.splitext(name)[0] + ".hmm"
        hmmOut.append(os.path.join(path, name))

        if not config['REPLACE'] and os.path.exists(hmmOut[-1]):
            continue
        
        # HMMER
        try:
            command = f"{config['EXE_HMMSEARCH']} -o /dev/null --cpu 4 --domtblout {hmmOut[-1]} {hmmDB} {amino}"
            with open(f"{path}/stderr.txt", 'w') as ferr:
                jobs.append(subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=ferr))
                #TODO: Add option to redirect output to file
        except Exception as e:
            print(e)
            print("Error: failed to run: " + command)

    # Wait for jobs
    done = False
    while not done:
        done = True
        for j in jobs:
            if j.poll() is None:
                done = False
        time.sleep(1)

    return hmmOut
