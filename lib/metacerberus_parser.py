# -*- coding: utf-8 -*-
"""metacerberus_parser.py Parses HMMER output and identifies KOs with FOAM and KEGG DB info
1) Get best hits
2) Save rollup file
3) Convert rollup file to table
"""

def warn(*args, **kwargs):
    #print("args", str(args))
    pass
import warnings
warnings.warn = warn

import os
import re
from pathlib import Path
import pandas as pd


def parseHmmer(hmm_tsv, config, subdir):
    path = Path(config['DIR_OUT'], subdir)
    path.mkdir(exist_ok=True, parents=True)

    done = path / "complete"
    if not config['REPLACE'] and done.exists():
        rollup_files = dict()
        for name in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
            outfile = Path(path, f"HMMER_BH_{name}_rollup.tsv")
            if outfile.exists():
                rollup_files[name] = outfile
        return rollup_files
    done.unlink(missing_ok=True)


    minscore = config["MINSCORE"]

    top5File = Path(path, "HMMER_top_5.tsv")


    # Calculate Best Hit
    BH_query = {}
    BH_top5 = {}
    #"target", "query", "e-value", "score", "length", "start", "end"
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
            if score < minscore:            # Skip scores less than minscore
                print("DEBUG: MINSCORE DETECTED")
                continue

            # store top 5 per query
            if query not in BH_top5:
                BH_top5[query] = [line]
            elif len(BH_top5[query]) < 5:
                BH_top5[query].append(line)
            else:
                BH_top5[query].sort(key = lambda x: x[3], reverse=False)
                if score > float(BH_top5[query][0][3]):
                    BH_top5[query][0] = line

            # Check for Best Score per query
            if query not in BH_query:
                BH_query[query] = line
            elif score > float(BH_query[query][3]):
                BH_query[query] = line

    # Save Top 5 hits tsv rollup
    with top5File.open('w') as writer:
        print("Target Name", "ID", "EC value", "E-Value (sequence)", "Score (domain)", file=writer, sep='\t')
        for query in sorted(BH_top5.keys()):
            BH_top5[query].sort(key = lambda x: x[3], reverse=True)
            for line in BH_top5[query]:
                ko = []
                ec = []
                for id in line[1].split(','):
                    if "KO:" in id:
                        #TODO: Remove this path once custom databases properly identified and formated.
                        print("TODO: Fix DB And remove conditional path (Parser)")
                        id = id.split(':')[1].split('_')
                        ko += [id[0]]
                        if len(id)>1:
                            ec += [id[1]]
                    else:
                        ko += [id]
                print(line[0], ','.join(ko), ','.join(ec), line[2], line[3], file=writer, sep='\t')

    # Create dictionary with found KO IDs and counts
    KO_ID_counts = {}
    #for line in BH_dict.values():
    #    KO_IDs = [KO_ID.split(":")[1].split("_")[0] for KO_ID in line[1].split(",") if "KO:" in KO_ID]
    #    for KO_ID in KO_IDs:
    #        if KO_ID not in KO_ID_counts:
    #            KO_ID_counts[KO_ID] = 0
    #        KO_ID_counts[KO_ID] += 1
    for line in BH_query.values():
        KO_IDs = [ID for ID in line[1].split(",")]
        for KO_ID in KO_IDs:
            if KO_ID not in KO_ID_counts:
                KO_ID_counts[KO_ID] = 0
            KO_ID_counts[KO_ID] += 1

    # Write rollup files to disk

    #rollup_file = dict()
    #for name in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
    #    dbPath = Path(config['PATHDB'], f"{name}-onto_rel1.tsv")
    #    outfile = Path(path, f"HMMER_BH_{name}_rollup.tsv")
    #    #df = rollupKegg(KO_ID_counts, dbPath, path, outfile)
    #    df = rollup(KO_ID_counts, dbPath, path)
    #    if len(df.index) > 1:
    #        df.to_csv(outfile, index=False, header=True, sep='\t')
    #        rollup_file[name] = outfile

    dbPath = Path(config['PATHDB'])
    dfRollups = rollupAll(KO_ID_counts, dbPath, path)
    rollup_files = dict()
    for name,df in dfRollups.items():
        if len(df.index) > 1:
            outfile = Path(path, f"HMMER_BH_{name}_rollup.tsv")
            df.to_csv(outfile, index=False, header=True, sep='\t')
            rollup_files[name] = outfile

    done.touch()
    return rollup_files

######### Roll-Up All #########
def rollupAll(KO_COUNTS: dict, lookupPath: str, outpath: str):
    dfLookup = dict()
    dfRollup = dict()
    count_file = dict()
    for name in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
        count_file[name] = Path(outpath, f'counts_{name}.tsv').open('w')
        print('ID', 'count', sep='\t', file=count_file[name])
        dbPath = Path(lookupPath, f"{name}-onto_rel1.tsv")
        dfLookup[name] = pd.read_csv(dbPath, sep='\t').fillna('')
        dfRollup[name] = pd.DataFrame()

    errfile = os.path.join(outpath, 'lookup.err')
    with open(errfile, 'w') as errlog:
        for KO_ID,count in sorted(KO_COUNTS.items()):
            found = False
            for name in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
                rows = pd.DataFrame(dfLookup[name][dfLookup[name].KO==KO_ID])
                if not rows.empty:
                    found = True
                    rows.drop(rows[rows['Function']==''].index, inplace=True)
                    if rows.empty:
                        print("WARNING:'", KO_ID, "'Does not have a 'Function' in the Lookup File:", name, file=errlog)
                        continue
                    print(KO_ID, count, sep='\t', file=count_file[name])
                    rows['Count'] = count
                    dfRollup[name] = pd.concat([dfRollup[name],rows])
            if not found:
                print("WARNING:'", KO_ID, "'not found in any Lookup File", file=errlog)
                continue
    
    return dfRollup


########## Counts Table #########
def createCountTables(rollup_files:dict, config:dict, subdir: str):
    done = Path(config['DIR_OUT']) / subdir / "complete"
    dfCounts = dict()

    for dbName,filepath in rollup_files.items():
        outpath = os.path.join(config['DIR_OUT'], subdir, f"{dbName}-rollup_counts.tsv")
        if not config['REPLACE'] and done.exists():
            dfCounts[dbName] = outpath
            continue
        done.unlink(missing_ok=True)

        try:
            df = pd.read_csv(filepath, sep='\t')
        except:
            continue
        dictCount = {}
        for i,row in df.iterrows():
            for colName,colData in row.items():
                if not colName.startswith('L'):
                    continue
                level = colName[1]
                name = colData
                if name:
                    name = f"lvl{level}: {name}"
                    if name not in dictCount:
                        dictCount[name] = [level, 0, ""]
                    dictCount[name][1] += row['Count']
            name = row.Function
            if not name:
                continue
            name = f"{row.KO}: {name}"
            if name not in dictCount:
                dictCount[name] = ['Function', 0, row.KO]
            dictCount[name][1] += row['Count']
        data = {
        'KO Id':[x[2] for x in dictCount.values()],
        'Name':list(dictCount.keys()),
        'Level':[x[0] for x in dictCount.values()],
        'Count':[x[1] for x in dictCount.values()]}

        df = pd.DataFrame(data=data)
        df.fillna(0, inplace=True)
        df.to_csv(outpath, index=False, header=True, sep='\t')
        dfCounts[dbName] = outpath

    done.touch()
    return dfCounts


# Merge TSV Files
def merge_tsv(tsv_list:dict, out_file:Path):
    names = sorted(list(tsv_list.keys()))
    file_list = dict()
    lines = dict()
    IDS = set()
    for name in names:
        file_list[name] = open(tsv_list[name])
        file_list[name].readline() # skip header
        lines[name] = file_list[name].readline().split()
        if lines[name]:
            IDS.add(lines[name][0])
    if len(IDS) == 0: # Fail if nothing to merge
        return False
    with open(out_file, 'w') as writer:
        print("ID", '\t'.join(names), sep='\t', file=writer)
        while IDS:
            ID = sorted(IDS)[0]
            IDS.remove(ID)
            line = [ID]
            #IDS = set()
            for name in names:
                if not lines[name]: # End of file
                    line.append('0')
                elif lines[name][0] > ID: # File ID comes after current
                    line.append('0')
                else:
                    line.append(lines[name][1])
                    lines[name] = file_list[name].readline().split()
                    if lines[name]:
                        IDS.add(lines[name][0])
            print('\t'.join(line), file=writer)
            #if not IDS:
            #    break
    for name in names:
        file_list[name].close()
    return True
