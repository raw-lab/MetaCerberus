# -*- coding: utf-8 -*-

"""
hmm_cmd = "hmmsearch --cpu %s --domtblout %s.FOAM.out %s %s" %(nCPU, output_path, hmm_file, faa_path)
"""

import os
import subprocess
import csv


## HMMER Search
def search(aminoAcid, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')

    foam = f'{config["PATH"]}/cerberusDB/FOAM-hmm_rel1a.hmm.gz'

    # HMMER
    try:
        command = f'hmmsearch --cpu {config["CPUS"]} --domtblout {path}.FOAM.out {foam} {aminoAcid}'
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except:
        print("Error: failed to run: " + command)

    fout.close()
    ferr.close()


    BH_dict = {}
    BS_dict = {}
    minscore = 25 #TODO: Move to config file, user specifies this
    reader = open(f'{path}.FOAM.out', "r").readlines()
    for line in reader:
        if line[0] == "#": continue
        line = line.split()
        score = float(line[13])
        if score < minscore: continue
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

    rollup_file = f"{path}.FOAM.out.sort.BH.KO.rollup"
    with open(f"{path}/KO_ID_dict.txt", 'w') as fileOut:
        for key,value in KO_ID_dict.items():
            print(f"{key}: {value}", file=fileOut)
    
    rollup = roll_up(KO_ID_dict, rollup_file, f'{config["PATH"]}/cerberusDB')
    return (f'{path}.FOAM.out', rollup)


# Roll-Up
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
