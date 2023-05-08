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
    path = os.path.join(config['DIR_OUT'], subdir)
    os.makedirs(path, exist_ok=True)

    minscore = config["MINSCORE"]

    top5File = Path(path, "HMMER_top_5.tsv")
    filteredFile = Path(path, "HMMER_filtered.tsv")


    # Calculate Best Hit
    BH_dict = {}
    BH_top5 = {}
    BH_target = {}
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
            if query not in BH_dict:
                BH_dict[query] = line
            elif score > float(BH_dict[query][3]):
                BH_dict[query] = line

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
    for line in BH_dict.values():
        KO_IDs = [ID for ID in line[1].split(",")]
        for KO_ID in KO_IDs:
            if KO_ID not in KO_ID_counts:
                KO_ID_counts[KO_ID] = 0
            KO_ID_counts[KO_ID] += 1

    # Write rollup files to disk

    rollup_file = dict()
    for name in ['FOAM', 'KEGG', 'COG']:
        dbPath = Path(config['PATHDB'], f"{name}-onto_rel1.tsv")
        outfile = Path(path, f"HMMER_BH_{name}_rollup.tsv")
        #df = rollupKegg(KO_ID_counts, dbPath, path, outfile)
        df = rollup(KO_ID_counts, dbPath, path)
        df.to_csv(outfile, index=False, header=True, sep='\t')
        rollup_file[name] = outfile

    return rollup_file

######## Roll-Up KEGG #########
def rollupKegg(KO_COUNTS: dict, lookupFile: Path, outpath: str, outfile: Path):
    dfLookup = dict()
    with Path(lookupFile).open() as reader:
        for line in reader:
            line = line.strip('\n').split('\t')
            dfLookup[line[4]] = line[0:4] + line[5:]

    errfile = Path(outpath, Path(lookupFile).name+".err")
    with errfile.open('w') as errlog, Path(outfile).open('w') as writer:
        #L1 | L2 | L3 | KO | Function | EC
        print("L1", "L2", "L3", "KO", "Function", "EC", "Count", sep='\t', file=writer)
        for KO_ID,count in KO_COUNTS.items():
            if KO_ID in dfLookup:
                L1, L2, L3, Func, EC, _ = dfLookup[KO_ID]
                print(L1, L2, L3, KO_ID, Func, EC, count, sep='\t')
                if Func:
                    print(L1, L2, L3, KO_ID, Func, EC, count, sep='\t', file=writer)
                else:
                    print("WARNING:'", KO_ID, "'Does not have a 'Function' in the Lookup File", file=errlog)
            else:
                print("WARNING:'", KO_ID, "'not found in the Lookup File", file=errlog)

    return outfile

######### Roll-Up #########
def rollup(KO_COUNTS: dict, lookupFile: str, outpath: str):
    dfLookup = pd.read_csv(lookupFile, sep='\t')
    dfRollup = pd.DataFrame()

    errfile = os.path.join( outpath, os.path.basename(lookupFile)+'.err' )
    with open(errfile, 'w') as errlog:
        for KO_ID,count in KO_COUNTS.items():
            rows = pd.DataFrame(dfLookup[dfLookup.KO==KO_ID]).fillna('')
            if rows.empty:
                print("WARNING:'", KO_ID, "'not found in the Lookup File", file=errlog)
                continue
            rows.drop(rows[rows['Function']==''].index, inplace=True)
            if rows.empty:
                print("WARNING:'", KO_ID, "'Does not have a 'Function' in the Lookup File", file=errlog)
                continue
            rows['Count'] = count
            dfRollup = pd.concat([dfRollup,rows])

    return dfRollup


########## Counts Table #########
def createCountTables(rollup_files:dict, config:dict, subdir: str):
    done = Path(config['DIR_OUT']) / subdir / "complete"
    dfCounts = dict()
    print("createCountTables:", subdir)
    for dbName,filepath in rollup_files.items():
        outpath = os.path.join(config['DIR_OUT'], subdir, f"{dbName}_counts.tsv")
        if not config['REPLACE'] and done.exists():
            dfCounts[dbName] = outpath
            continue
        done.unlink(missing_ok=True)

        print("Loading Count Tables:", dbName, filepath)
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
def merge_tsv(tsv_list:dict, out_file:os.PathLike):
    names = sorted(list(tsv_list.keys()))
    file_list = dict()
    for name in names:
        file_list[name] = open(tsv_list[name])
        file_list[name].readline() # skip header
    with open(out_file, 'w') as writer:
        print("kmer", '\t'.join(names), sep='\t', file=writer)
        lines = dict()
        kmers = set()
        for name in names:
            lines[name] = file_list[name].readline().split()
            kmers.add(lines[name][0])
        kmer = sorted(kmers)[0]
        while True:
            line = [kmer]
            kmers = set()
            for name in names:
                if not lines[name]:
                    line.append('0')
                elif lines[name][0] > kmer:
                    line.append('0')
                else:
                    line.append(lines[name][1])
                    lines[name] = file_list[name].readline().split()
                    if lines[name]:
                        kmers.add(lines[name][0])
            print('\t'.join(line), file=writer)
            if not kmers:
                break
            kmer = sorted(kmers)[0]
    for name in names:
        file_list[name].close()
    return


# Merge TSV Files, Transposed
def merge_tsv_T(tsv_list:dict, out_file:os.PathLike):
    names = sorted(list(tsv_list.keys()))#, key=lambda x: x.lower())
    header = set()
    file_list = dict()
    for name in names:
        file_list[name] = open(tsv_list[name], 'r')
        file_list[name].readline() # skip header
        for line in file_list[name]:
            kmer = line.split()[0]
            header.add(kmer)
    
    header = list(header)
    with open(out_file, 'w') as writer:
        print('sample', '\t'.join(header), sep='\t', file=writer)
        for name in names:
            file_list[name].seek(0)
            file_list[name].readline() # skip header
            counts = dict()
            for line in file_list[name]:
                kmer,count = line.split()
                counts[kmer] = count
            file_list[name].close()
            writer.write(name)
            for kmer in header:
                if kmer in counts:
                    writer.write(f'\t{counts[kmer]}')
                else:
                    writer.write(f'\t0')
            writer.write('\n')
    return
