import os
from os.path import isfile, join
import subprocess

def main():
    #ontology files
    script_dir = os.path.dirname(os.path.realpath(__file__))
    osf_dir = "osf_Files"
    path = os.path.join(script_dir, osf_dir)
    os.mkdir(path)
    os.chdir(path)

    osf_cmd = "wget https://osf.io/72p6g/download -O FOAM_readme.txt"
    subprocess.call(osf_cmd, shell=True)
    osf_cmd = "wget https://osf.io/muan4/download -O FOAM-onto_rel1.tsv"
    subprocess.call(osf_cmd, shell=True)
    osf_cmd = "wget https://osf.io/2hp7t/download -O KO_classification.txt"
    subprocess.call(osf_cmd, shell=True)
    osf_cmd = "wget https://osf.io/bdpv5/download -O FOAM-hmm_rel1a.hmm.gz"
    subprocess.call(osf_cmd, shell=True)

if __name__ == "__main__":
    main()
