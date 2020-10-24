import os
from os.path import isfile, join
import sys
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

def main(path, file):
    mercat_cmd = "mercat %s" %(' '.join(sys.argv[1:]))
    subprocess.call(mercat_cmd, shell=True)

    faa_path = path + "/mercat_results/" + file[:-3] + "_protein_run/" + file[:-3] + "_protein_pro.faa"
    hmm_cmd = "hmmsearch --domtblout %s.FOAM.out /home/alexander/Desktop/Robomax/Test_Files/FOAM-hmm_rel1a.hmm.gz %s" %(faa_path, faa_path)
    subprocess.call(hmm_cmd, shell=True)

    sort_cmd = "sort %s.FOAM.out > %s.FOAM.out.sort" %(faa_path, faa_path)
    subprocess.call(sort_cmd, shell=True)

    HHMerBH_cmd = "python2 bmn-HMMerBestHit.py %s.FOAM.out.sort > %s.FOAM.out.sort.BH" %(faa_path, faa_path)
    subprocess.call(HHMerBH_cmd, shell=True)

    awk_cmd = "awk '{print $4}' %s.FOAM.out.sort.BH > %s.FOAM.out.sort.BH.tmp1" %(faa_path, faa_path)
    subprocess.call(awk_cmd, shell=True)

    CEE_cmd = "python2 bmn-CountEachElement.py %s.FOAM.out.sort.BH.tmp1 > %s.FOAM.out.sort.BH.tmp2" %(faa_path, faa_path)
    subprocess.call(CEE_cmd, shell=True)

    KOC_cmd = "python2 bmn-KOoneCount.py %s.FOAM.out.sort.BH.tmp2 | sed s/KO://g | sort -k 1 > %s.FOAM.out.sort.BH.KO" %(faa_path, faa_path)
    subprocess.call(KOC_cmd, shell=True)

    pass

path, file_list = get_file_list()
for f in file_list:
    main(path, f)
