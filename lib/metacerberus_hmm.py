# -*- coding: utf-8 -*-

"""metacerberus_hmm.py Module to find FOAM annotations using Hidden Markov Models
Uses HMMER hmmsearch
"""

import os
import subprocess
import time


## HMMER Search
def searchHMM(aminoAcids:dict, config:dict, subdir:str, hmmDB:tuple, CPUs:int=4):
    minscore = config['MINSCORE']

    hmmKey,hmmDB = hmmDB

    hmmOut = dict()
    for key,amino in aminoAcids.items():
        path = f"{config['DIR_OUT']}/{subdir}/{key}"
        os.makedirs(path, exist_ok=True)

        name = os.path.basename(amino)
        name_dom = os.path.splitext(name)[0] + "_tmp.hmm"
        hmmOut[os.path.join(path, name_dom)] = amino

    jobs = dict()
    outlist = list()
    for domtbl_out,amino in hmmOut.items():
        pathname = os.path.dirname(domtbl_out)
        basename = os.path.basename(domtbl_out)
        outname = os.path.splitext(basename)[0] + ".tsv"
        outfile = os.path.join(pathname, f"{hmmKey}_{outname}")

        # HMMER
        try:
            #TODO: Add --keep option to save the HMMER output file
            print("target", "query", "e-value", "score", "length", "start", "end", sep='\t', file=open(outfile, 'w'))
            reduce_grep = """grep -Ev '^#' | awk '{ print $1 "\t" $4 "\t" $7 "\t" $14 "\t" $3 "\t" $18 "\t" $19 }'""" + f" >> {outfile}"
            command = f"{config['EXE_HMMSEARCH']} -o /dev/null --cpu {CPUs} --domT {minscore} --domtblout /dev/stdout {hmmDB} {amino} | {reduce_grep}"
            with open(f"{path}/stderr.txt", 'w') as ferr:
                jobs[domtbl_out] = subprocess.Popen(command, shell=True, stderr=ferr)
            outlist.append(outfile)
        except Exception as e:
            print(e)
            print("Error: failed to run: " + command)
    
    # Wait for jobs
    done = False
    while not done:
        done = True
        keys = list(jobs.keys())
        for domtbl_out in keys:
            if jobs[domtbl_out].poll() is None: # no return code yet, still running
                done = False # At least one job still running
        time.sleep(1)

    return outlist
