# -*- coding: utf-8 -*-

"""metacerberus_prostats.py Calculates protein stats from HMMER and Amino Acid sequences

"""

from pathlib import Path
import pandas as pd
import statistics as stat


def getStats(faa: str, fileHmmer: str, dfCount: dict, config: dict, summary_out:str):
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
    with open(fileHmmer, "r") as reader:
        for i,line in enumerate(reader,1):
            #"target", "query", "e-value", "score", "length", "start", "end"
            line = line.split('\t')
            try:
                target = line[0]
                query = line[1]
                evalue = line[2]
                score = float(line[3])
                length = int(line[4])
            except:
                continue

            if target in proteins:
                proteins[target]['count'] += 1
                if score >= minscore:
                    proteins[target]['found'] += 1
                if target not in hmmHits:
                    hmmHits[target] = list()
                hmmHits[target].append([query, score, evalue, length])
            else:
                if faa:
                    print("ERROR: Target on line", i, "of HMMER file not in protein fasta:", fileHmmer)
                    return None
                else: #TODO: There is probably a better way to do this.
                    proteins[target] = dict(count=1, found=0, length=length)
                    if score >= minscore:
                        proteins[target]['found'] += 1
                    if target not in hmmHits:
                        hmmHits[target] = list()
                    hmmHits[target].append([query, score, evalue, length])
    
    # Annotate proteins
    dfLookup = dict()
    for dbname in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
        dbPath = Path(config['PATHDB'], f"{dbname}-onto_rel1.tsv")
        dfLookup[dbname] = pd.read_csv(dbPath, sep='\t').fillna('')
    with open(summary_out, 'w') as writer:
        print("locus_tag", 'FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG', "Best hit", "length_bp", "e-value", "score", "EC_number", "product", sep='\t', file=writer)
        for target in proteins.keys():
            if target in hmmHits:
                hmmHits[target].sort(key = lambda x: x[1], reverse=True)
                annotations = dict()
                for match in hmmHits[target]:
                    q,s,e,l = match
                    for dbname in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
                        if dbname not in annotations:
                            annotations[dbname] = []
                        rows = pd.DataFrame(dfLookup[dbname][dfLookup[dbname].ID==q])
                        if not rows.empty:
                            name = f"{dbname}:{rows.iloc[0].Function}"
                            EC = rows.iloc[0].EC
                            annotations[dbname] += [q]
                annotations = [", ".join(annotations[k]) for k in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']]
                query,score,evalue,length = hmmHits[target][0]
                name = ""
                EC = ""
                for dbname in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
                    rows = pd.DataFrame(dfLookup[dbname][dfLookup[dbname].ID==query])
                    if not rows.empty:
                        name = rows.iloc[0].Function
                        EC = rows.iloc[0].EC
                        break
                if name:
                    print(target, *annotations, f"{dbname}:{query}", length, evalue, score, EC, name, sep='\t', file=writer)
                else:
                    print(target, '', '', '', '', '', '', "", "", "", "", "", "Hypothetical", sep='\t', file=writer)
            else:
                print(target, '', '', '', '', '', '', "", "", "", "", "", "Hypothetical", sep='\t', file=writer)
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
