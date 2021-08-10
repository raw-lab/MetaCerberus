#!/usr/bin/env python3

import json

# read file
f = open('../data/ko00001_2021-07.json')
data = json.load(f)
f.close()

outFile = f"cerberusDB/KO_classification.txt"
open(outFile, 'w').close()
def parse_json(dicData, level):
    if level > 0:
        with open(outFile, 'a') as dbOut:
            name = dicData['name'].split(maxsplit=1)
            if level < 3:
               name = name[1]
            else:
                name = f"{name[0]}\t{name[1]}"
            print('\t'*(level-1), name, sep='', file=dbOut)
    for key,value in dicData.items():
        if type(value) is list:
            for item in value:
                parse_json(item, level+1)

parse_json(data, 0)
