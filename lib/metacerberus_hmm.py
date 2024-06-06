# -*- coding: utf-8 -*-

"""metacerberus_hmm.py Module to find FOAM annotations using Hidden Markov Models
Uses HMMER hmmsearch
"""

import os
import re
from pathlib import Path
import subprocess
import time
import pyhmmer


## HMMER Search
def searchHMM(aminoAcids:dict, config:dict, subdir:str, hmm:tuple, CPUs:int=4):
    minscore = config['MINSCORE']
    evalue = config['EVALUE']

    hmmKey,hmm = hmm

    hmmOut = dict()
    for key,amino in aminoAcids.items():
        path = Path(config['DIR_OUT'], subdir, key)
        os.makedirs(path, exist_ok=True)

        name_dom = f"{key}_tmp.hmm"
        hmmOut[os.path.join(path, name_dom)] = amino

    outlist = list()
    for domtbl_out,amino in hmmOut.items():
        pathname = os.path.dirname(domtbl_out)
        basename = os.path.basename(domtbl_out)
        outname = os.path.splitext(basename)[0] + ".tsv"
        outfile = os.path.join(pathname, f"{hmmKey}-{outname}")

        # HMMER
        errfile=Path(outfile).with_suffix('.err').open('w')
        with open(outfile, 'wt') as hmm_writer, pyhmmer.plan7.HMMFile(hmm) as hmm_reader, pyhmmer.easel.SequenceFile(amino, digital=True) as seq_reader:
            for hit in pyhmmer.hmmer.hmmsearch(hmm_reader, seq_reader, E=evalue, cpus=CPUs):
                for h in hit:
                    for domain in h.domains.included:
                        if domain.score < minscore:
                            continue
                        align = domain.alignment
                        print(h.name.decode(), hit.query_name.decode(), f'{h.evalue:.1E}', f"{domain.score:.1f}", h.length,
                            align.target_from, align.target_to,
                            sep='\t', file=hmm_writer)
        outlist += [outfile]
        errfile.close

    return outlist


# Filter HMM results
def filterHMM(hmm_tsv:Path, outfile:Path, dbpath:Path):
    outfile.parent.mkdir(parents=True, exist_ok=True)

    for i in range(1, len(dbpath.suffixes)):
        dbpath = Path(dbpath.with_suffix(''))
    dbLookup = dbpath.with_suffix('.tsv')
    match = re.search(r"^KOFam_[a-z]+_([A-Z]+)", hmm_tsv.name)
    if match:
        dbLookup = dbpath.with_name(f'{match.group(1)}.tsv')
    dbLookup = dbLookup.read_text()

    BH_target = dict()
    logfile = outfile.with_suffix('.log')
    with hmm_tsv.open() as reader, logfile.open('w') as logger:
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
                            overlap = True
                            # Equal Score
                            if e_value == match[1] and score == match[2]:
                                add = True
                            # Winner takes all
                            elif e_value < match[1]:
                                BH_target[target][c] = item
                            elif e_value == match[1]:
                                if score > match[2]:
                                    BH_target[target][c] = item
                if add or not overlap:
                    # Equal score OR Dual domain
                    BH_target[target] += [item]
            # next line
            continue
    # Write filtered overlaps to file
    with outfile.open('w') as writer:
        print("target", "query", "e-value", "score", "length", "start", "end", sep='\t', file=writer)
        for target in sorted(BH_target):
            for match in set(BH_target[target]):
                query, e_value, score, length, start, end = match
                print(target, query, e_value, score, length, start, end, sep='\t', file=writer)

    return outfile
