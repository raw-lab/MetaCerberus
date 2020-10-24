import os
from os.path import isfile, join
import sys
import csv
import subprocess

import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help='path to file or directory')
    args = parser.parse_args()

    return parser, args

def get_file_list(args):
    in_file_path = args.i
    if os.path.isfile(in_file_path):
        path, file = os.path.split(in_file_path)
        file_list = [file]
    if os.path.isdir(in_file_path):
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

def roll_up(file):
    FOAM_file = r"/home/alexander/Desktop/Robomax/osf_Files/FOAM-onto_rel1.tsv"
    FOAM_dict = {}
    reader = csv.reader(open(FOAM_file, "r"), delimiter="\t")
    header = next(reader)
    for line in reader:
        KO_ID = line[4]
        FOAM_info = line[0:4]
        FOAM_dict[KO_ID] = FOAM_info

    KEGG_file = r"/home/alexander/Desktop/Robomax/osf_Files/KO_classification.txt"
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
    
    reader = csv.reader(open(file, "r"), delimiter=" ")
    outfile = open(file + ".rollup", "w")
    for line in reader:
        if line[0][0] != "K": continue
        KO_ID = line[0].split(":")[1].split("_")[0]
        try:
            FOAM_info = FOAM_dict[KO_ID]
        except KeyError:
            FOAM_info = ["NA"]
        try:
            KEGG_info = KEGG_dict[KO_ID]
        except KeyError:
            KEGG_info = ["NA"]
        outline = "\t".join([str(s) for s in [line[0], line[1], FOAM_info, KEGG_info]])
        outfile.write(outline + "\n")

def faa_processing(faa_path):
    hmm_cmd = "hmmsearch --domtblout %s.FOAM.out /home/alexander/Desktop/Robomax/osf_Files/FOAM-hmm_rel1a.hmm.gz %s" %(faa_path, faa_path)
    subprocess.call(hmm_cmd, shell=True)

    sort_cmd = "sort %s.FOAM.out > %s.FOAM.out.sort" %(faa_path, faa_path)
    subprocess.call(sort_cmd, shell=True)

    HHMerBH_cmd = "python3 bmn-HMMerBestHit_p3.py %s.FOAM.out.sort > %s.FOAM.out.sort.BH" %(faa_path, faa_path)
    subprocess.call(HHMerBH_cmd, shell=True)

    awk_cmd = "awk '{print $4}' %s.FOAM.out.sort.BH > %s.FOAM.out.sort.BH.tmp1" %(faa_path, faa_path)
    subprocess.call(awk_cmd, shell=True)

    CEE_cmd = "python3 bmn-CountEachElement_p3.py %s.FOAM.out.sort.BH.tmp1 > %s.FOAM.out.sort.BH.tmp2" %(faa_path, faa_path)
    subprocess.call(CEE_cmd, shell=True)

    KOC_cmd = "python3 bmn-KOoneCount_p3.py %s.FOAM.out.sort.BH.tmp2 | sed s/KO://g | sort -k 1 > %s.FOAM.out.sort.BH.KO" %(faa_path, faa_path)
    subprocess.call(KOC_cmd, shell=True)

    KO_file = "%s.FOAM.out.sort.BH.KO" %(faa_path)
    roll_up(KO_file)

def main(path, file):
    f_name, f_ext = os.path.splitext(file)

    fq_list = [".fq", ".fastq"]
    if f_ext in fq_list:
        fq_path = path + file
        fna_path = fq_processing(fq_path, path, f_name)
        faa_path = fna_processing(fna_path, path, f_name)
        faa_processing(faa_path)

    fna_list = [".fa",".fna", ".fasta", ".ffn"]
    if f_ext in fna_list:
        fna_path = path + file
        faa_path = fna_processing(fna_path, path, f_name)
        faa_processing(faa_path)

    if f_ext == ".faa":
        faa_path = path + file
        faa_processing(faa_path)

if __name__ == "__main__":
    parser, args = get_args()
    path, file_list = get_file_list(args)
    for f in file_list:
        main(path, f)
