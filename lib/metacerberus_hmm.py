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
    evalue = config['EVALUE']

    hmmKey,hmmDB = hmmDB

    hmmOut = dict()
    for key,amino in aminoAcids.items():
        path = Path(config['DIR_OUT'], subdir, key)
        os.makedirs(path, exist_ok=True)

        name_dom = f"{key}_tmp.hmm"
        hmmOut[os.path.join(path, name_dom)] = amino

    jobs = dict()
    outlist = list()
    for domtbl_out,amino in hmmOut.items():
        pathname = os.path.dirname(domtbl_out)
        basename = os.path.basename(domtbl_out)
        outname = os.path.splitext(basename)[0] + ".tsv"
        outfile = os.path.join(pathname, f"{hmmKey}-{outname}")

        # HMMER
        errfile=Path(outfile).with_suffix('.err').open('w')
        try:
            reduce_awk = f"""grep -Ev '^#' | awk '$7 < {evalue} && $14 > {minscore} {{ print $1 "\t" $4 "\t" $7 "\t" $14 "\t" $3 "\t" $18 "\t" $19 }}' >> {outfile}"""
            command = f"{config['EXE_HMMSEARCH']} -o /dev/null --cpu {CPUs} --domtblout /dev/stdout {hmmDB} {amino} | {reduce_awk}"
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


# Filter HMM results
def filterHMM(hmm_tsv:Path, outfile:Path, dbpath:Path):
    outfile.parent.mkdir(parents=True, exist_ok=True)

    hmm,key = hmm_tsv.stem.split(sep='-', maxsplit=1)
    if hmm in ['COG', 'CAZy', 'PHROG', 'VOG']:
        lookup_list = [hmm]
    else:
        lookup_list = ['KEGG']

    with outfile.open('w') as writer, outfile.with_suffix('.log').open('w') as logger:
        for name in lookup_list:
            dbLookup = Path(dbpath, f"{name}-onto_rel1.tsv").read_text()
            BH_target = dict()
            with open(hmm_tsv, "r") as reader:
                for i,line in enumerate(reader, 1):
                    line = line.split('\t')
                    try:
                        target = line[0]
                        query = line[1]
                        e_value = float(line[2])
                        score = float(line[3])
                        length = int(line[4])
                        start = int(line[5])
                        end = int(line[6])
                    except:
                        print("Failed to read line:", i, hmm_tsv, file=logger)
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
                        add = False
                        overlap = False
                        for c,match in enumerate(BH_target[target]):
                            # Check for overlap
                            if start <= match[5] and end >= match[4]:
                                overlap_len = min(end, match[5]) - max(start, match[4])
                                if overlap_len > 10:
                                    # Winner takes all
                                    overlap = True
                                    if score == match[2]:
                                        add = True
                                    elif score > match[2]:
                                        BH_target[target][c] = item
                                else:
                                    #print("NO OVERLAP:", overlap_len, file=logger)
                                    pass
                        if add or not overlap:
                            # Equal score OR Dual domain
                            BH_target[target] += [item]
                    # next line
                    continue
            # Write filtered overlaps to file
            for target in sorted(BH_target):
                for match in set(BH_target[target]):
                    query, e_value, score, length, start, end = match
                    print(target, query, e_value, score, length, start, end, sep='\t', file=writer)

    return outfile
