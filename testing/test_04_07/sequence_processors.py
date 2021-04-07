import os
from os.path import isfile, join
import sys
import subprocess
import csv
def fastq_processing(fq_path, path, f_name,file):
    trim_path=path+'/'+f_name+"_trim.fastq"
    cmd1="fastp -i "+fq_path+" -o " + trim_path
    cmd2="fastqc "+trim_path
    trim_fna=path+'/'+f_name+"_trim.fna"
    cmd3="sed -n '1~4s/^@/>/p;2~4p' "+trim_path+"  > "+trim_fna
    subprocess.call(cmd1,shell=True)
    subprocess.call(cmd2,shell=True)
    subprocess.call(cmd3,shell=True)
    return trim_fna

def fna_processing(fna_path, path, f_name,file,virus):
    # name="/prokka_results_"+f_name
    # prokka_outdir = path + name+"/"
    # print(path,234567)
    # prokka_cmd = "prokka %s --outdir %s --prefix %s --centre clean --compliant --metagenome" %(fna_path, prokka_outdir, f_name)
    # subprocess.call(prokka_cmd, shell=True)
    path_to_faa=path+"/"+f_name+'_pro.faa'
    if not virus:
        cmd="prodigal -i %s -a %s"%(fna_path, path_to_faa)
    else:
        print('here')
        cmd="%s/FGSpp -s %s -o %s -w 0 -r %s/train -t 454_5 -p 16"%(virus,fna_path, path_to_faa[:-4],virus)
    subprocess.call(cmd, shell=True)
    # faa_path = prokka_outdir + f_name + ".faa"
    # return faa_path,path+name
    return path_to_faa,path

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
    return rollup_file

def faa_processing(faa_path,path,f_name):
    output_path=path+os.sep+f_name+"_output"
    os.makedirs(output_path)
    output_path=os.path.join(output_path + os.sep, f_name)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    hmm_file = os.path.join(script_dir, "osf_Files/FOAM-hmm_rel1a.hmm.gz")
    hmm_cmd = "hmmsearch --cpu 28 --domtblout %s.FOAM.out %s %s" %(output_path, hmm_file, faa_path)
    subprocess.call(hmm_cmd, shell=True)

    BH_dict = {}
    BS_dict = {}
    minscore = 25
    reader = open(output_path + ".FOAM.out", "r").readlines()
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
    
    rollup_file = "%s.FOAM.out.sort.BH.KO.rollup" %(output_path)
    return roll_up(KO_ID_dict, rollup_file)