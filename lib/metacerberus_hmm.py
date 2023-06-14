# -*- coding: utf-8 -*-

"""metacerberus_hmm.py Module to find FOAM annotations using Hidden Markov Models
Uses HMMER hmmsearch
"""

import os
import re
from pathlib import Path
import subprocess
import time


## HMMER Search
def searchHMM(aminoAcids:dict, config:dict, subdir:str, hmmDB:tuple, CPUs:int=4):
    minscore = config['MINSCORE']

    hmmKey,hmmDB = hmmDB

    hmmOut = dict()
    for key,amino in aminoAcids.items():
        path = Path(config['DIR_OUT'], subdir, key)
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
        errfile=Path(outfile).with_suffix('.err').open('w')
        try:
            #TODO: Add --keep option to save the HMMER output file
            #print("target", "query", "e-value", "score", "length", "start", "end", sep='\t', file=open(outfile, 'w'))
            reduce_grep = """grep -Ev '^#' | awk '{ print $1 "\t" $4 "\t" $7 "\t" $14 "\t" $3 "\t" $18 "\t" $19 }'""" + f" >> {outfile}"
            command = f"{config['EXE_HMMSEARCH']} -o /dev/null --cpu {CPUs} --domT {minscore} --domtblout /dev/stdout {hmmDB} {amino} | {reduce_grep}"
            if not Path(outfile).exists():
                jobs[domtbl_out] = subprocess.Popen(command, shell=True, stderr=errfile)
            outlist.append(outfile)
        except Exception as e:
            print(e, file=errfile)
            print("Error: failed to run: " + command, file=errfile)
        errfile.close
    
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

def filterHMM(hmm_tsv:Path, outfile:Path, dbpath:Path):
    with outfile.open('w') as writer:
        print("target", "query", "e-value", "score", "length", "start", "end", file=writer, sep='\t')
        for name in ['KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
            dbLookup = Path(dbpath, f"{name}-onto_rel1.tsv").read_text()
            BH_target = dict()
            with open(hmm_tsv, "r") as reader:
                for line in reader:
                    line = line.split('\t')
                    try:
                        target = line[0]
                        query = line[1]
                        e_value = line[2]
                        line[3] = float(line[3])
                        score = line[3]
                        length = int(line[4])
                        start = int(line[5])
                        end = int(line[6])
                    except:
                        continue
                    # Check if Query is in the Database
                    if not re.search(query, dbLookup, re.MULTILINE):
                        continue

                    # Count Proper Hits
                    # 1) Overlapping: Count best score
                    # 2) Unique: Count both
                    if target not in BH_target:
                        BH_target[target] = [(query, e_value, score, length, start, end)]
                    else: # More than one match/target
                        #keys = list(BH_target[target].keys())
                        item = (query, e_value, score, length, start, end)
                        overlap = False
                        for i,match in enumerate(BH_target[target]):
                            # Check for overlap
                            if start <= match[5] and end >= match[4]:
                                #overlap = end - match[4]
                                overlap = True
                                if score > match[2]:
                                    BH_target[target][i] = item
                        if not overlap: # Did not overlap
                            BH_target[target] += [item]
            # Write filtered overlaps to file
            for target in BH_target:
                for match in set(BH_target[target]):
                    query, e_value, score, length, start, end = match
                    print(target, query, e_value, score, length, start, end, sep='\t', file=writer)

    return outfile
