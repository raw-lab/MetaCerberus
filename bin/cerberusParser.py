# -*- coding: utf-8 -*-


import os
import subprocess
import csv
from collections import Counter
import math


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
    print("Getting top hit.")
    #bestHit = f'{sorted}.BH'
    #command = f'python {config["PATH"]}/bmn-HMMerBestHit_p3.py {sorted} > {bestHit}'
    #subprocess.run(command, shell=True)

    col = 13
    minscore = 25
    with open(sorted, 'r') as Hits:
        while True:
            bestHits = Hits.readline()
            if not bestHits.startswith("#"):
                maxscore = float(bestHits.split()[col])
                query = bestHits.split()[0]
                break

        bestHitList = []
        for hit in Hits:
            if hit.startswith("#"):
                continue
            hitSplit = hit.split()
            curScore = float(hitSplit[col])
            if curScore >= minscore:
                if query != hitSplit[0]:
                    if float(bestHits.split()[col]) >= minscore :
                        bestHitList.append(bestHits.strip())
                    query = hitSplit[0]
                    maxscore = float(0)
                    bestHits = hit
                elif maxscore <= float(hitSplit[col]):
                    bestHits = hit
                    maxscore = float(hitSplit[col])
        if bestHits is not None:
            bestHits = bestHits.strip()

    # Get fourth column
    print("Getting fourth column. (KO IDs)")
    #fourth = f'{bestHit}.tmp1'
    #command = "awk '{print $4}' " + f"{bestHit} > {fourth}"
    #subprocess.run(command, shell=True)

    koID = [x.split()[3] for x in bestHitList]

    #count Elements
    print("Counting elements.")
    #elementCounts = f'{bestHit}.tmp2'
    #command = f"python {config['PATH']}/bmn-CountEachElement_p3.py {fourth} > {elementCounts}"
    #subprocess.run(command, shell=True)

    elements = []
    #with open(fourth, 'r') as lines:
    mytids=[]
    #for line in lines:
    for line in koID:
        mytids.append(line.rstrip())
    cnt = Counter()
    for word in mytids:
        cnt[word] += 1
    for i in cnt.keys():
        elements.append(str(i)+"\t"+str(cnt[i]))

    #KO
    print("KO")
    #KO = f'{bestHit}.KO'
    #command = f"python {config['PATH']}/bmn-KOoneCount_p3.py {elementCounts} | sed s/KO://g | sort -k 1 > {KO}"
    #subprocess.run(command, shell=True)

    nmap = dict()
    for line in elements:
        if line[0:2] != "KO":
            continue
        [KO,n1] = line.split()
        Ksplit = KO.split(',')
        n2 = math.ceil(float(n1) / len(Ksplit))
        for K in Ksplit:
            if K in nmap:
                nmap[K] = nmap[K] + n2
            else: nmap[K] = n2

    ko = {}
    for [KO,nb] in nmap.items():
        KO = KO.split(':')[1].split('_')[0]
        ko[KO] = nb

    rollup_file = f"{path}/FOAM.out.sort.BH.KO.rollupB"
    return roll_up(ko, rollup_file, f'{config["PATH"]}/cerberusDB')


########## PARSE HMMER ##########
def parseHmmer(hmmer, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    BH_dict = {}
    BS_dict = {}
    minscore = 25 #TODO: Move to config file, user specifies this
    with open(hmmer, "r") as reader:
        for line in reader:
            if line.startswith("#"):
                continue
            line = line.split()
            score = float(line[13])
            if score < minscore:
                continue
            query = line[0]
            try:
                best_score = BS_dict[query]
            except KeyError:
                BS_dict[query] = score
                BH_dict[query] = line
                continue
            if score > best_score:
                BS_dict[query] = score
                BH_dict[query] = line

    KO_ID_dict = {}
    for BH in BH_dict:
        line = BH_dict[BH]
        KO_IDs = [KO_ID.split(":")[1].split("_")[0] for KO_ID in line[3].split(",") if "KO:" in KO_ID]
        for KO_ID in KO_IDs:
            try:
                KO_ID_dict[KO_ID] += 1
            except KeyError:
                KO_ID_dict[KO_ID] = 1

    rollup_file = f"{path}/FOAM.BH.KO.rollup"    
    return roll_up(KO_ID_dict, rollup_file, f'{config["PATH"]}/cerberusDB')


######### Roll-Up #########
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
