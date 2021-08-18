#!/usr/bin/env python3

import json
import re
import pandas as pd


in_FOAM = "../bin/cerberusDB/FOAM-onto_rel1.tsv"
out_FOAM = "FOAM-onto_rel1.tsv"
in_KO = "ko00001_2021-07.json"
out_KO = "KO_classification.txt"


#### Recursive Method to load nested json file ####
def parse_json(dicData, writer, level=0):
    table = {}
    if level > 0: #first level contains no writable data
        name = dicData['name'].split(maxsplit=1)
        if level < 3:
            name = name[1]
        else:
            name = f"{name[0]}\t{name[1]}"
            if level == 4:
                table[ name.split('\t')[0] ] = name.split('\t')[1]
        print('\t'*(level-1), name, sep='', file=writer)
    for value in dicData.values():
        if type(value) is list:
            for item in value:
                table.update( parse_json(item, writer, level+1) )
    return table


#### START ####

# read file
with open(in_KO) as reader:
    data = json.load(reader)

# parse json
table = parse_json(data, open(out_KO, 'w'))

# add functions from KEGG to FOAM
koNames = {}
koEC = {}
regex = re.compile(" \[EC:([^;]*)\]")
for key,val in table.items(): # split the names and the EC
    koNames[key] = regex.sub("", val)
    match = regex.search(val)
    if match:
        koEC[key] = match.group(1)

df = pd.read_csv(in_FOAM, sep='\t')
df['Function'] = df['KO'].map(koNames)
df['EC'] = df['KO'].map(koEC)

df.to_csv(out_FOAM, sep='\t', index=False)
