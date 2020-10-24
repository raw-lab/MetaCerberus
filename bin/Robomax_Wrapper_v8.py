import os
from os.path import isfile, join
import sys
import csv
import subprocess

import argparse

def get_args():
    parser = argparse.ArgumentParser(description='RoboMax is used for versatile functional ontology assignments for metagenomes via HMM searching with environmental focus of shotgun meta-omics data')
    parser.add_argument('-i', type=str, required=True, help='path to file or directory')
    args = parser.parse_args()

    return parser, args

def get_file_list(args):
    in_file_path = args.i
    if os.path.isfile(in_file_path):
        if isfile(join(os.getcwd(), in_file_path)):
            path, file = os.path.split(join(os.getcwd(), in_file_path))
        else:
            path, file = os.path.split(in_file_path)
        file_list = [file]
    if os.path.isdir(in_file_path):
        if os.path.isdir(join(os.getcwd(), in_file_path)):
            path = join(os.getcwd(), in_file_path)
            file_list = [f for f in os.listdir(path) if isfile(join(path, f))]
        else:
            path = in_file_path
            file_list = [f for f in os.listdir(in_file_path) if isfile(join(in_file_path, f))]
    return path, file_list

def fq_processing(fq_path, path, f_name):
    fna_name = path + f_name + ".fna"
    fna_path = open(fna_name, "w")
    reader = csv.reader(open(fq_path, "r"), delimiter="\t")
    for line in reader:
        if line[0][0] != "@": continue
        label = line[0]
        try:
            seq = next(reader)[0]
        except IndexError:
            continue
        fna_path.write(label + "\n")
        fna_path.write(seq + "\n")
    return fna_path

def fna_processing(fna_path, path, f_name):
    prokka_outdir = path + "/prokka_results/"
    prokka_cmd = "prokka %s --outdir %s --prefix %s" %(fna_path, prokka_outdir, f_name)
    subprocess.call(prokka_cmd, shell=True)

    faa_path = prokka_outdir + f_name + ".faa"
    return faa_path

def roll_up(KO_ID_dict, rollup_file):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    FOAM_file = os.path.join(script_dir, "osf_Files/FOAM-onto_rel1.tsv")
    FOAM_dict = {}
    reader = csv.reader(open(FOAM_file, "r"), delimiter="\t")
    header = next(reader)
    for line in reader:
        KO_ID = line[4]
        FOAM_info = line[0:4]
        FOAM_dict[KO_ID] = FOAM_info

    KEGG_file = os.path.join(script_dir, "osf_Files/KO_classification.txt")
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

def faa_processing(faa_path):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    hmm_file = os.path.join(script_dir, "osf_Files/FOAM-hmm_rel1a.hmm.gz")
    hmm_cmd = "hmmsearch --domtblout %s.FOAM.out %s %s" %(faa_path, hmm_file, faa_path)
    subprocess.call(hmm_cmd, shell=True)

    BH_dict = {}
    BS_dict = {}
    minscore = 25
    reader = open(faa_path + ".FOAM.out", "r").readlines()
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

    rollup_file = "%s.FOAM.out.sort.BH.KO.rollup" %(faa_path)
    roll_up(KO_ID_dict, rollup_file)

def main(path, file):
    f_name, f_ext = os.path.splitext(file)

    fq_list = [".fq", ".fastq"]
    fna_list = [".fa",".fna", ".fasta", ".ffn"]
    if f_ext in fq_list:
        fq_path = os.path.join(path + os.sep, file)
        fna_path = fq_processing(fq_path, path, f_name)
        faa_path = fna_processing(fna_path, path, f_name)
        faa_processing(faa_path)
    elif f_ext in fna_list:
        fna_path = os.path.join(path + os.sep, file)
        faa_path = fna_processing(fna_path, path, f_name)
        faa_processing(faa_path)
    elif f_ext == ".faa":
        faa_path = os.path.join(path + os.sep, file)
        faa_processing(faa_path)
    else:
        print("File extension \" %s \" not recognized. Please name file(s) appropriately." %(f_ext))

if __name__ == "__main__":
    parser, args = get_args()
    path, file_list = get_file_list(args)

    for f in file_list:
        main(path, f)
