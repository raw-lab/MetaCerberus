# -*- coding: utf-8 -*-


import os
import subprocess
import csv


# Parse HMMER output
def parse(hmmFoam, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    # Sort hmmer output
    sorted = os.path.basename(hmmFoam)
    sorted = os.path.join(path, sorted+'.sort')
    command = f'sort {hmmFoam} > {sorted}'
    subprocess.run(command, shell=True)

    # Get top hit
    bestHit = f'{sorted}.BH'
    command = f'python {config["PATH"]}/bmn-HMMerBestHit_p3.py {sorted} > {bestHit}'
    subprocess.run(command, shell=True)

    # Get fourth column
    fourth = f'{bestHit}.tmp1'
    command = "awk '{print $4}' " + f"{bestHit} > {fourth}"
    subprocess.run(command, shell=True)

    #count Elements
    elementCounts = f'{bestHit}.tmp2'
    command = f"python {config['PATH']}/bmn-CountEachElement_p3.py {fourth} > {elementCounts}"
    subprocess.run(command, shell=True)

    #KO
    KO = f'{bestHit}.KO'
    command = f"python {config['PATH']}/bmn-KOoneCount_p3.py {elementCounts} | sed s/KO://g | sort -k 1 > {KO}"
    subprocess.run(command, shell=True)

    

    return


#Rollup
def roll_up(KO_ID_dict, rollup_file, dbPath):
    FOAM_file = f"{dbPath}/FOAM-onto_rel1.tsv"
    FOAM_dict = {}
    reader = csv.reader(open(FOAM_file, "r"), delimiter="\t")
    header = next(reader)
    for line in reader:
        KO_ID = line[4]
        FOAM_info = line[0:4]
        FOAM_dict[KO_ID] = FOAM_info

    KEGG_file = f"{dbPath}/KO_classification.txt"
    KEGG_dict = {}
    reader = csv.reader(open(KEGG_file, "r"), delimiter="\t")
    for line in reader:
        if line[0] != "":
            tier_1 = line[0]
            continue
        if line[1] != "":
            tier_2 = line[1]
            continue
        if line[2] != "":
            pathway = line[3]
            continue
    KO_ID = line[3]
    KEGG_info = [tier_1, tier_2, pathway] + line[4:]
    KEGG_dict[KO_ID] = KEGG_info

    KO_ID_list = [key for key in KO_ID_dict]
    KO_ID_list.sort()

    outfile = open(rollup_file, "w")
    for KO_ID in KO_ID_list:
        try:
            FOAM_info = FOAM_dict[KO_ID]
        except KeyError:
            FOAM_info = ["NA"]
        try:
            KEGG_info = KEGG_dict[KO_ID]
        except KeyError:
            KEGG_info = ["NA"]
        outline = "\t".join([str(s) for s in [KO_ID, KO_ID_dict[KO_ID], FOAM_info, KEGG_info]])
        outfile.write(outline + "\n")
    return rollup_file
