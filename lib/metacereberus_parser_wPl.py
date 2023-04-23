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
import polars as pl
from pathlib import Path

def parseHmmer(hmm_tsv, config, subdir):
    path = os.path.join(config['DIR_OUT'], subdir)
    os.makedirs(path, exist_ok=True)

    minscore = config["MINSCORE"]

    top5File = os.path.join(path, "HMMER_top_5.tsv")

    # Calculate Best Hit
    BH_dict = {}
    BH_top5 = {}

    # read input file
    df = pl.read_csv(hmm_tsv, delimiter='\t', header=None, columns=["target", "query", "e-value", "score"])

    # skip scores less than minscore
    df = df[df['score'] >= minscore]

    # store top 5 per query
    groups = df.groupby('query')
    for group in groups:
        query = group['query'][0]
        group = group.sort('score', reverse=True)
        if len(group) < 5:
            BH_top5[query] = group.to_list()
        else:
            BH_top5[query] = group[:5].to_list()

    # Check for Best Score per query
    groups = df.groupby('query')
    for group in groups:
        query = group['query'][0]
        group = group.sort('score', reverse=True)
        if query not in BH_dict:
            BH_dict[query] = group[0].to_list()
        elif group['score'][0] > BH_dict[query][3]:
            BH_dict[query] = group[0].to_list()

    # Save Top 5 hits tsv rollup
    with open(top5File, 'w') as writer:
        print("Target Name", "KO ID", "EC value", "E-Value (sequence)", "Score (domain)", file=writer, sep='\t')
        for query in sorted(BH_top5.keys()):
            for line in BH_top5[query]:
                ko = []
                ec = []
                for id in line[1].split(','):
                    if "KO:" in id:
                        id = id.split(':')[1].split('_')
                        ko += [id[0]]
                        if len(id)>1:
                            ec += [id[1]]
                print(line[0], ','.join(ko), ','.join(ec), line[2], line[3], file=writer, sep='\t')

    # Create dictionary with found KO IDs and counts
    KO_ID_counts = {}
    for line in BH_dict.values():
        KO_IDs = [KO_ID.split(":")[1].split("_")[0] for KO_ID in line[1].split(",") if "KO:" in KO_ID]
        for KO_ID in KO_IDs:
            if KO_ID not in KO_ID_counts:
                KO_ID_counts[KO_ID] = 0
            KO_ID_counts[KO_ID] += 1

    # Write rollup files to disk
def write_rollup_files(KO_ID_counts, path, config):
    rollup_file = dict()
    dbPaths = [
        os.path.join(config['PATHDB'], "FOAM-onto_rel1.tsv"),
        os.path.join(config['PATHDB'], "KEGG-onto_rel1.tsv")]
    for dbPath in dbPaths:
        dfRollup = pl.read_csv(dbPath, sep='\t')
        dfRollup = rollup(KO_ID_counts, dfRollup, path)
        outfile = os.path.join(path, f"HMMER_BH_{os.path.basename(dbPath).split('-')[0]}_rollup.tsv")
        dfRollup.to_csv(outfile, delimiter='\t', header=True, index=False)
        rollup_file[os.path.basename(dbPath).split('-')[0]] = outfile

    return rollup_file

######### Roll-Up #########
def rollup(KO_COUNTS: dict, lookupFile: str, outpath: str):
    dfLookup = pl.read_csv(lookupFile, delimiter='\t')
    dfRollup = pl.DataFrame()

    errfile = os.path.join(outpath, os.path.basename(lookupFile) + '.err')
    with open(errfile, 'w') as errlog:
        for KO_ID, count in KO_COUNTS.items():
            rows = dfLookup[dfLookup['KO'] == KO_ID].fillna('')
            if rows.shape[0] == 0:
                print("WARNING:'", KO_ID, "'not found in the Lookup File", file=errlog)
                continue
            rows = rows.drop(rows[rows['Function'] == ''].index)
            if rows.shape[0] == 0:
                print("WARNING:'", KO_ID, "'Does not have a 'Function' in the Lookup File", file=errlog)
                continue
            rows['Count'] = count
            dfRollup = pl.concat([dfRollup, rows])

    dfRollup.to_csv(outpath, delimiter='\t', index=False)
    return dfRollup

########## Counts Table #########
def createCountTables(rollup_files: dict, config: dict, subdir: str):
    done = os.path.join(config['DIR_OUT'], subdir, "complete")
    dfCounts = dict()
    print("createCountTables:", subdir)
    for dbName, filepath in rollup_files.items():
        outpath = os.path.join(config['DIR_OUT'], subdir, f"{dbName}_counts.tsv")
        if not config['REPLACE'] and os.path.exists(done):
            dfCounts[dbName] = outpath
            continue

        print("Loading Count Tables:", dbName, filepath)
        try:
            df = pl.read_csv(filepath, delimiter='\t')
        except:
            continue
        dictCount = {}
        for i, row in df.iterrows():
            for colName, colData in row.items():
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
            'KO Id': [x[2] for x in dictCount.values()],
            'Name': list(dictCount.keys()),
            'Level': [x[0] for x in dictCount.values()],
            'Count': [x[1] for x in dictCount.values()]}

        df = pl.DataFrame(data=data)
        df.fill_null(0, inplace=True)
        df.to_csv(outpath, index=False, header=True, delimiter='\t')
        dfCounts[dbName] = outpath

    pl.Path(done).touch()
    return dfCounts
