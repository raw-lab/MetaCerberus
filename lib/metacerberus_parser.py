# -*- coding: utf-8 -*-
"""metacerberus_parser.py Parses HMMER output
1) Get best hits
2) Save rollup file
3) Convert rollup file to table
"""

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

import os
from pathlib import Path
import pandas as pd


def top5s(hmm_tsv:dict, outfile:Path):
    outfile.parent.mkdir(0o777, True, True)

    # Calculate Best Hit
    BH_top5 = {}
    for hmm,filename in hmm_tsv.items():
        with open(filename, "r") as reader:
            reader.readline()
            for line in reader:
                line = line.split('\t')
                target = line[0]
                query = line[1]
                e_value = line[2]
                score = float(line[3])
                ec = '' #TODO: Match query to EC

                # store top 5 per query
                match = [target, query, ec, e_value, score, hmm]
                if target not in BH_top5:
                    BH_top5[target] = [match]
                elif len(BH_top5[target]) < 5:
                    BH_top5[target].append(match)
                else:
                    BH_top5[target].sort(key = lambda x: x[3], reverse=False)
                    if score > float(BH_top5[target][0][3]):
                        BH_top5[target][0] = match

    # Save Top 5 hits tsv rollup
    with outfile.open('w') as writer:
        print("Target Name", "ID", "EC value", "E-Value (sequence)", "Score (domain)", "hmmDB", sep='\t', file=writer)
        for target in sorted(BH_top5.keys()):
            BH_top5[target].sort(key = lambda x: x[3], reverse=True)
            for line in BH_top5[target]:
                print(*line, sep='\t', file=writer)
    return outfile


def top5(hmm_tsv:Path, outfile:Path):
    outfile.parent.mkdir(0o777, True, True)

    # Calculate Best Hit
    BH_top5 = {}
    with open(hmm_tsv, "r") as reader:
        reader.readline()
        for line in reader:
            line = line.split('\t')
            target = line[0]
            query = line[1]
            e_value = line[2]
            score = float(line[3])
            ec = '' #TODO: Match query to EC

            # store top 5 per query
            match = [target, query, ec, e_value, score]
            if target not in BH_top5:
                BH_top5[target] = [match]
            elif len(BH_top5[target]) < 5:
                BH_top5[target].append(match)
            else:
                BH_top5[target].sort(key = lambda x: x[3], reverse=False)
                if score > float(BH_top5[target][0][3]):
                    BH_top5[target][0] = match

    # Save Top 5 hits tsv rollup
    with outfile.open('w') as writer:
        print("Target Name", "ID", "EC value", "E-Value (sequence)", "Score (domain)", sep='\t', file=writer)
        for target in sorted(BH_top5.keys()):
            BH_top5[target].sort(key = lambda x: x[3], reverse=True)
            for line in BH_top5[target]:
                print(*line, sep='\t', file=writer)
    return outfile


def parseHmmer(hmm_tsv, config, subdir, dbpath):
    path = Path(config['DIR_OUT'], subdir)
    path.mkdir(exist_ok=True, parents=True)

    #done = path / "complete"
    #if not config['REPLACE'] and done.exists():
    #    print("AH CRAP!!!")
    #    rollup_files = dict()
    #    for name in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
    #        outfile = Path(path, f"HMMER_BH_{name}_rollup.tsv")
    #        if outfile.exists():
    #            rollup_files[name] = outfile
    #    return rollup_files
    #done.unlink(missing_ok=True)


    minscore = config["MINSCORE"]

    for i in range(1, len(dbpath.suffixes)):
        dbpath = Path(dbpath.with_suffix(''))
    dbname = dbpath.name
    top5File = Path(path, f"HMMER-{dbname}_top_5.tsv")


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
                id = [i for i in line[1].split(',')]
                ec = []
                print(line[0], ','.join(id), ','.join(ec), line[2], line[3], file=writer, sep='\t')

    # Create dictionary with found IDs and counts
    ID_counts = {}
    for line in BH_query.values():
        IDs = [ID for ID in line[1].split(",")]
        for ID in IDs:
            if ID not in ID_counts:
                ID_counts[ID] = 0
            ID_counts[ID] += 1

    # Write rollup files to disk

    #dbPath = Path(config['PATHDB'])
    dfRollup = rollup(ID_counts, dbpath, path)
    rollup_files = dict()
    #for name,df in dfRollups.items():
    if len(dfRollup.index) > 1:
        outfile = Path(path, f"HMMER_BH_{dbname}_rollup.tsv")
        dfRollup.to_csv(outfile, index=False, header=True, sep='\t')
        rollup_files[dbname] = outfile

    #done.touch()
    return rollup_files

######### Roll-Up All #########
def rollup(COUNTS: dict, dbpath: str, outpath: str):
    for i in range(1, len(dbpath.suffixes)):
        dbpath = Path(dbpath.with_suffix(''))
    dbLookup = dbpath.with_suffix('.tsv')
    dbname = dbpath.name

    dfLookup = pd.read_csv(dbLookup, sep='\t').fillna('')
    dfRollup = pd.DataFrame()
    count_file = Path(outpath, f'counts_{dbname}.tsv')
    errfile = Path(outpath, 'lookup.err')

    with count_file.open('w') as count_writer, errfile.open('w') as errlog:
        print('ID', 'count', sep='\t', file=count_writer)
        for ID,count in sorted(COUNTS.items()):
            found = False
            rows = pd.DataFrame(dfLookup[dfLookup.ID==ID])
            if not rows.empty:
                found = True
                rows.drop(rows[rows['Function']==''].index, inplace=True)
                if rows.empty:
                    print("WARNING:'", ID, "'Does not have a 'Function' in the Lookup File:", dbname, file=errlog)
                    continue
                print(ID, count, sep='\t', file=count_writer)
                rows['Count'] = count
                dfRollup = pd.concat([dfRollup,rows])
            if not found:
                print("WARNING:'", ID, "'not found in any Lookup File", file=errlog)
                continue
    
    return dfRollup


########## Counts Table #########
def createCountTables(rollup_files:dict, config:dict, subdir: str):
    done = Path(config['DIR_OUT']) / subdir / "complete"
    dfCounts = dict()

    for dbName,filepath in rollup_files.items():
        outpath = Path(config['DIR_OUT'], subdir, f"{dbName}-rollup_counts.tsv")
        if not config['REPLACE'] and done.exists() and outpath.exists():
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
            name = f"{row.ID}: {name}"
            if name not in dictCount:
                dictCount[name] = ['Function', 0, row.ID]
            dictCount[name][1] += row['Count']
        data = {
        'Id':[x[2] for x in dictCount.values()],
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
    for name in names:
        file_list[name].close()
    return True
