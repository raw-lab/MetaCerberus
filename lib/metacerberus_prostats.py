# -*- coding: utf-8 -*-

"""metacerberus_prostats.py Calculates protein stats from HMMER and Amino Acid sequences

"""

import re
from pathlib import Path
import pandas as pd
import statistics as stat


def getStats(faa:str, hmm_tsv:dict, dfCount:dict, config:dict, dbhmms:dict, summary_out:Path, fasta_prefix:Path):
    minscore = config["MINSCORE"]

    # sum up proteins in FASTA file
    protein_index = dict()
    proteins = dict()
    if faa:
        with open(faa, "r") as reader:
            name = ""
            line = reader.readline()
            while line:
                if line.startswith('>'):
                    name = line[1:].rstrip().split(sep=None, maxsplit=1)[0]
                    protein_index[name] = reader.tell()
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
    for dbname,filename in hmm_tsv.items():
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
            hmmHits[target].append([query, evalue, score, length, start, end, dbname])

            # Count protein matches
            if target in proteins:
                proteins[target]['count'] += 1
                if score >= minscore:
                    proteins[target]['found'] += 1
            else:
                if faa:
                    print("WARNING: Target on line", i, "of HMMER target not in protein fasta:", hmm_tsv)
                    continue
                else: #TODO: There is probably a better way to do this.
                    proteins[target] = dict(count=1, found=0, length=length)
                    if score >= minscore:
                        proteins[target]['found'] += 1
        reader.close()

    # Annotate proteins
    #TODO: use evalue as well as score for best comparison
    # Load Lookup Tables, create header
    header = ["target", "product", "best_hit", "HMM", "evalue", "score", "EC", "gene", "product_start", "product_end", "product_length", "ORF_length"]
    empty = ["" for x in header][2:]
    dfLookup = dict()
    hmmFiles = dict()
    for dbname,dbpath in dbhmms.items():
        # Load .tsv of same name as hmm
        while Path(dbpath).suffixes:
            dbpath = Path(dbpath).with_suffix('')
        dbLookup = dbpath.with_suffix('.tsv')
        if dbname.startswith("KOFam"):
            dbLookup = re.search(r"KOFam_.*_([A-Z]+)", dbname).group(1)
            dbLookup = dbpath.with_name(f'{dbLookup}.tsv')
        dfLookup[dbname] = pd.read_csv(dbLookup, sep='\t').fillna('')
        # open outfile for hmm matches
        hmmFiles[dbname] = open(summary_out.with_stem(f"annotation_summary_{dbname}"), 'w')
        print("target", "product", "best_hit", "evalue", "score", "EC", "gene", "product_start", "product_end", "product_length", "ORF_length", sep='\t', file=hmmFiles[dbname])
    with open(summary_out, 'w') as writer, fasta_prefix.open('w') as faa_writer, open(faa) as faa_reader:
        print(*header, sep='\t', file=writer)
        for target in proteins.keys():
            if target in hmmHits:
                # sort by score
                hmmHits[target].sort(key = lambda x: x[1], reverse=False)
                # Best Match
                query,eval,score,length,start,end,dbname = hmmHits[target][0]
                name,EC,gene = ["", "", ""]
                rows = pd.DataFrame(dfLookup[dbname][dfLookup[dbname].ID==query])
                if not rows.empty:
                    name = rows.iloc[0].Function
                    try: EC = rows.iloc[0].EC
                    except: pass
                    try: gene = rows.iloc[0].Gene
                    except: pass
                annotate = [name, query, dbname, eval, score, EC, gene, start, end, end-start, length]
                print(target, *annotate, sep='\t', file=writer)

                # Write to FAA file
                faa_reader.seek(protein_index[target])
                print(f">{target}", name, file=faa_writer)
                for line in faa_reader:
                    if line.startswith('>'):
                        break
                    faa_writer.write(line)
                annotate = list()

                # Individual matches
                annotations = dict()
                for match in hmmHits[target]:
                    query,eval,score,length,start,end,dbname = match
                    rows = pd.DataFrame(dfLookup[dbname][dfLookup[dbname].ID==query])
                    name,EC, gene = ["", "", ""]
                    if not rows.empty:
                        name = rows.iloc[0].Function
                        try: EC = rows.iloc[0].EC
                        except: pass
                        try: gene = rows.iloc[0].Gene
                        except: pass
                    else:
                        print("WARNING, query not in lookup:", target, dbname, query)
                    # add match to corresponding file
                    annotation = [name, query, eval, score, EC, gene, start, end, end-start, length]
                    print(target, *annotation, sep='\t', file=hmmFiles[dbname])
                    # keep track of db names with matches
                    if dbname not in annotations:
                        annotations[dbname] = [name, query, eval, score, EC, gene, start, end, end-start, length]
                # if db name wasn't in a match, mark target as hypothetical for that db
                for dbname in dbhmms.keys():
                    if dbname not in annotations:
                        print(target, "Hypothetical", *empty[1:], sep='\t', file=hmmFiles[dbname])
            else:
                # no match found for target, mark in all files as hypothetical
                print(target, "Hypothetical", *empty, sep='\t', file=writer)
                for dbname in dbhmms.keys():
                    print(target, "Hypothetical", *empty[1:], sep='\t', file=hmmFiles[dbname])
                # Write to FAA file
                faa_reader.seek(protein_index[target])
                print(f">{target}", "Hypothetical", file=faa_writer)
                for line in faa_reader:
                    if line.startswith('>'):
                        break
                    faa_writer.write(line)
                annotate = list()
    del dfLookup
    for v in hmmFiles.values():
        v.close()

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
