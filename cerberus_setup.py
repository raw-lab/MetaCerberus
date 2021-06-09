#!/usr/bin/env python3

import os
import subprocess
import shutil


############################Set paths for file interactions###################################

home = os.path.expanduser("~")
path = os.path.join(home, "bin/cerberus")
pathOSF = os.path.join(path, "osf_Files")
access_rights = 0o755

############################Creates the cerberus folder########################################

def cerberus_dir():
    try:
        os.makedirs(path, access_rights, exist_ok=True)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s" % path)
        osf_Files_dir()

if __name__ == "__cerberus_dir__":
    cerberus_dir()

####Creates osf file directory and initiates OSF file download cmd create_osf_Files()#########

def osf_Files_dir():
    try:
        os.makedirs(pathOSF, access_rights)
    except OSError:
        print ("Creation of the directory %s failed" % pathOSF)
    else:
        print("Successfully created the directory %s" % pathOSF)
        create_osf_Files()

if __name__ == "__osf_Files_dir__":
    osf_Files_dir()

##Downloads OSF files to osf_File directory

def create_osf_Files():
    osf_cmd = "wget https://osf.io/72p6g/download -v -O "+pathOSF+"/FOAM_readme.txt"
    subprocess.call(['bash', '-c', osf_cmd])
    osf_cmd = "wget https://osf.io/muan4/download -v -O "+pathOSF+"/FOAM-onto_rel1.tsv"
    subprocess.call(['bash', '-c', osf_cmd])
    osf_cmd = "wget https://osf.io/2hp7t/download -v -O "+pathOSF+"/KO_classification.txt"
    subprocess.call(['bash', '-c', osf_cmd])
    osf_cmd = "wget https://osf.io/bdpv5/download -v -O "+pathOSF+"/FOAM-hmm_rel1a.hmm.gz"
    subprocess.call(['bash', '-c', osf_cmd])

if __name__ == "__create_osf_Files__":
    create_osf_Files()

cerberus_dir()

######################################Install dependencies#####################################

def install_dependencies():
    conda_cmd = "conda create -n cerberus_env -c conda-forge -c bioconda hmmer pandas numpy plotly dash openpyxl matplotlib scikit-learn fastqc"
    subprocess.call(conda_cmd, shell=True)

if __name__ == "__install_dependencies__":
    install_dependencies()

install_dependencies()

#############################get current wrapper from github###################################

def install():
    for file_name in os.listdir('bin/'):
        shutil.copy(os.path.join('bin/', file_name), path)
    par = 'src/FragGeneScanPlusPlus-master.zip'
    cmd_unzip = "unzip "+par
    subprocess.call(cmd_unzip, shell=True)
    os.rename('FragGeneScanPlusPlus-master', 'FGSpp')
    shutil.move('FGSpp', path)
    make = os.path.join(path, 'FGSpp')
    subprocess.call(['make', '-C', make])
    print("Files copied to '"+ path +"'")
    print("Add this to your PATH or .bashrc for easier use:")
    print('export PATH="$HOME/bin/cerberus:$PATH"')

if __name__ == "__wrapper_download__":
    install()

install()
