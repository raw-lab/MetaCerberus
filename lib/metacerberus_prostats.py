# -*- coding: utf-8 -*-

"""metacerberus_prostats.py Calculates protein stats from HMMER and Amino Acid sequences

"""

from pathlib import Path
import pandas as pd
import statistics as stat


def getStats(faa:str, hmm_tsv:dict, dfCount:dict, config:dict, dbhmms:dict, summary_out:str):
    minscore = config["MINSCORE"]

    # sum up proteins in FASTA file
    proteins = {}
    if faa:
        with open(faa, "r") as reader:
            name = ""
            line = reader.readline()
            while line:
                if line.startswith('>'):
                    name = line[1:].rstrip().split(sep=None, maxsplit=1)[0]
                    length = 0
                    line = reader.readline()
                    while line:
                        if line.startswith('>'):
                            break
                        length += len(line.strip())
                        line = reader.readline()
                    proteins[name] = dict(count=0, found=0, length=length)
                    continue
                line = reader.readline()
    #else:

    # sum up proteins in HMMER file
    hmmHits = dict()
    for hmm,filename in hmm_tsv.items():
    #with open(hmm_tsv, "r") as reader:
        reader = open(filename, "r")
        for i,line in enumerate(reader,1):
            #"target", "query", "e-value", "score", "length", "start", "end"
            line = line.split('\t')
            try:
                target = line[0]
                query = line[1]
                evalue = float(line[2])
                score = float(line[3])
                length = int(line[4])
                start = int(line[5])
                end = int(line[6])
            except:
                continue

            # Add to hmm tsv dict
            if target not in hmmHits:
                hmmHits[target] = list()
            hmmHits[target].append([query, evalue, score, length, start, end, hmm])

            # Count protein matches
            if target in proteins:
                proteins[target]['count'] += 1
                if score >= minscore:
                    proteins[target]['found'] += 1
            else:
                if faa:
                    print("ERROR: Target on line", i, "of HMMER target not in protein fasta:", hmm_tsv)
                    return None
                else: #TODO: There is probably a better way to do this.
                    proteins[target] = dict(count=1, found=0, length=length)
                    if score >= minscore:
                        proteins[target]['found'] += 1
        reader.close()

    # Annotate proteins
    #TODO: use evalue as well as score for best comparison
    # Load Lookup Tables, create header
    header = ["target", "best_hit", "HMM", "product", "evalue", "score", "EC"]
    empty = ["", "", "Hypothetical", "", "", ""]
    dfLookup = dict()
    for hmm,dbpath in dbhmms.items():
        # Load .tsv of same name as hmm
        for i in range(1, len(dbpath.suffixes)):
            dbpath = Path(dbpath.with_suffix(''))
        dbLookup = dbpath.with_suffix('.tsv')
        dfLookup[hmm] = pd.read_csv(dbLookup, sep='\t').fillna('')
        # Add hmm to header
        header += [hmm, f"{hmm}_name", f"{hmm}_evalue", f"{hmm}_score", "EC", f"{hmm}_length"]
        empty += ["", "", "", "", "", ""]
    with open(summary_out, 'w') as writer:
        print(*header, sep='\t', file=writer)
        for target in proteins.keys():
            if target in hmmHits:
                # sort by score
                hmmHits[target].sort(key = lambda x: x[1], reverse=False)
                # Best Match
                query,eval,score,length,start,end,dbname = hmmHits[target][0]
                rows = pd.DataFrame(dfLookup[dbname][dfLookup[dbname].ID==query])
                name,EC = ["", ""]
                if not rows.empty:
                    name = rows.iloc[0].Function
                    EC = rows.iloc[0].EC
                annotate = [query, dbname, name, eval, score, EC]
                # Individual matches
                annotations = dict()
                for match in hmmHits[target]:
                    query,eval,score,length,start,end,dbname = match
                    rows = pd.DataFrame(dfLookup[dbname][dfLookup[dbname].ID==query])
                    name,EC = ["", ""]
                    if not rows.empty:
                        name = rows.iloc[0].Function
                        EC = rows.iloc[0].EC
                    if dbname in annotations:
                        print("WARNING, db already in annotations (better score ? merge):", dbname)
                    annotations[dbname] = [query,name,eval,score,EC,length]
                for hmm in dbhmms.keys():
                    if hmm in annotations:
                        annotate += annotations[hmm]
                    else:
                        annotate += ['', '', '', '', '', '']
                print(target, *annotate, sep='\t', file=writer)
            else:
                print(target, *empty, sep='\t', file=writer)
    del dfLookup

    # calculate stats
    lengths = [ item['length'] for item in proteins.values() ]
    found = [ v['found'] for k,v in proteins.items() if v['found']>1 ]

    stats = {
        "Protein Count (Total)": len(proteins),
        f"Protein Count (>Min Score)": len(found),
        "% Proteins > Min Score": 0 if not len(proteins) else round(100.0*len(found)/len(proteins), 2),
        "Average Protein Length": 0 if not len(lengths) else round(stat.mean(lengths), 2)
    }
    for dbName,filepath in dfCount.items():
        if Path(filepath).exists():
            df = pd.read_csv(filepath, sep='\t')
            stats[dbName+' ID Count'] = df[df['Level']=='Function']['Count'].sum()

    return stats
