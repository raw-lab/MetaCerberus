# -*- coding: utf-8 -*-

"""cerberus_prostats.py Calculates protein stats from HMMER and Amino Acid sequences

"""

import statistics as stat


def getStats(faa: str, fileHmmer: str, dfCount: dict, config: dict):
    #path = os.path.join(config['DIR_OUT'], subdir)
    #os.makedirs(path, exist_ok=True)

    minscore = config["MINSCORE"]

    # sum up proteins in FASTA file
    proteins = {}
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

    # sum up proteins in HMMER file
    with open(fileHmmer, "r") as reader:
        for i,line in enumerate(reader,1):
            "target", "score", "e-value" "query"
            line = line.split('\t')
            try:
                target = line[0]
                score = float(line[1])
            except:
                continue

            if target not in proteins:
                print("WARNING: Possible bug on line", i, "of HMMER file:", fileHmmer)
                return None
            else:
                proteins[target]['count'] += 1
                if score >= minscore:
                    proteins[target]['found'] += 1
    
    # calculate stats
    lengths = [ item['length'] for item in proteins.values() ]
    found = [ v['found'] for k,v in proteins.items() if v['found']>1 ]

    stats = {
        "Protein Count (Total)": len(proteins),
        f"Protein Count (>Min Score)": len(found),
        "% Proteins > Min Score": round(100.0*len(found)/len(proteins), 2),
        "Average Protein Length": round(stat.mean(lengths), 2)
    }
    for dbName,df in dfCount.items():
        stats[dbName+' KO Count'] = df[df['Level']=='Function']['Count'].sum()

    return stats
