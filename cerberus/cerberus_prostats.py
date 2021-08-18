# -*- coding: utf-8 -*-

"""prot_stats.py Calculate protein stats from HMMER and Amino Acid sequences

"""

import os
import statistics as stat


def getStats(faa_fileHmmer: list, config: dict, subdir: str):
    #path = os.path.join(config['DIR_OUT'], subdir)
    #os.makedirs(path, exist_ok=True)

    faa = faa_fileHmmer[0]
    fileHmmer = faa_fileHmmer[1]

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
            line = line.strip()
            if line.startswith("#"):        # Skip commented lines
                continue
            line = line.split()
            try:
                query = line[0]             # Column 0 is our query
                tlen = line[2]              # Column 2 is length of protein
                score = float(line[13])     # Column 14 is the score, convert to float
            except:
                continue

            if query not in proteins:
                print("WARNING: Possible bug on line", i, "of HMMER file:", fileHmmer)
                print(line, '\n')
                exit()
            else:
                proteins[query]['count'] += 1
                if score >= minscore:
                    proteins[query]['found'] += 1
    
    # calculate stats
    lengths = [ item['length'] for item in proteins.values() ]
    found = [ v['found'] for k,v in proteins.items() if v['found']>1 ]

    stats = {
        "Total Protein Count": len(proteins),
        f"Proteins Above Min Score ({minscore})": len(found),
        "% Proteins > Min Score": round(100.0*len(found)/len(proteins), 2),
        "Average Protein Length": round(stat.mean(lengths), 2),
    }

    return stats
