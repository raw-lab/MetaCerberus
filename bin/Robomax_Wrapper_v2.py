import os
from os.path import isfile, join
import sys
import csv
import subprocess

def get_file_list():
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-i" or sys.argv[i] == "-f":
            in_file_path = sys.argv[i+1]
            break
        i += 1
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

def faa_processing(faa_path):
    hmm_cmd = "hmmsearch --domtblout %s.FOAM.out /home/alexander/Desktop/Robomax/Test_Files/FOAM-hmm_rel1a.hmm.gz %s" %(faa_path, faa_path)
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

path, file_list = get_file_list()
for f in file_list:
    main(path, f)
