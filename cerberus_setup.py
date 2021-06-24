#!/usr/bin/env python3

import os
import subprocess
import shutil
import argparse


# Global Variables
access_rights = 0o755
pathDB = "cerberusDB"


# Install Program Files
def install(path):
    try:
        os.makedirs(path, access_rights, exist_ok=True)
    except:
        print ("Creation of the directory %s failed" % path)
        return False

    for file_name in os.listdir('bin/'):
        file = os.path.join('bin', file_name)
        if os.path.isfile(file):
            shutil.copy(file, path)
    par = 'src/FragGeneScanPlus-master.zip'
    cmd_unzip = "unzip "+par
    subprocess.call(cmd_unzip, shell=True)
    os.rename('FragGeneScanPlus-master', 'FGS+')
    shutil.move('FGS+', path)
    make = os.path.join(path, 'FGS+')
    subprocess.call(['make', '-C', make])
    print("\nProgram files copied to '"+ path +"'")
    print("Add this to your PATH or .bashrc for easier use:")
    print(f'export PATH="{path}:$PATH"')
    return True


# Download FOAM and KO from OSF
def download_db(path):
    dbdir = os.path.join(path, pathDB)
    try:
        os.makedirs(dbdir, access_rights, exist_ok=True)
    except:
        print ("Creation of the directory %s failed" % pathDB)
        return False

    osf_cmd = "wget https://osf.io/72p6g/download -v -O "+dbdir+"/FOAM_readme.txt -c"
    subprocess.call(['bash', '-c', osf_cmd])
    osf_cmd = "wget https://osf.io/muan4/download -v -O "+dbdir+"/FOAM-onto_rel1.tsv -c"
    subprocess.call(['bash', '-c', osf_cmd])
    osf_cmd = "wget https://osf.io/2hp7t/download -v -O "+dbdir+"/KO_classification.txt -c"
    subprocess.call(['bash', '-c', osf_cmd])
    osf_cmd = "wget https://osf.io/bdpv5/download -v -O "+dbdir+"/FOAM-hmm_rel1a.hmm.gz -c"
    subprocess.call(['bash', '-c', osf_cmd])

    return


######################################Install dependencies#####################################
def install_dependencies():
    conda_cmd = "conda create -n cerberus -c conda-forge -c bioconda hmmer prodigal fastqc fastp bbmap pandas numpy plotly openpyxl matplotlib scikit-learn python=3.7 -y"
    subprocess.call(conda_cmd, shell=True)
    # TODO: 'conda activate' command not working through script, manually install ray for now.
    #pip_cmd = "conda activate cerberus ; pip install ray[default]"
    #subprocess.call(pip_cmd, shell=True)
    print("WARNING")
    print("Please manually install 'ray' by issuing the following commands:")
    print("> conda activate cerberus")
    print("> pip install ray[default]")
    return


def main():
    ## Parse the command line
    parser = argparse.ArgumentParser(add_help=False)
    required = parser.add_argument_group('required arguments')
    required.add_argument('-p', "--path", type=str, help='path to install directory. Default is to install in downloaded path', required=True)
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-i', '--install', action='store_true', help='Only copy the scripts to "path"')
    optional.add_argument('-d', '--download', action='store_true', help='Only download FOAM and KO database')
    optional.add_argument('-e', '--environment', action='store_true', help='Only create the cerberus conda environment with dependencies installed')
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
    args = parser.parse_args()

    if any([args.install, args.download, args.environment]):
        if args.install:
            install(args.path)
        if args.download:
            download_db(args.path)
        if args.environment:
            install_dependencies()
    else:
        install(args.path)
        download_db(args.path)
        install_dependencies()

if __name__ == "__main__":
    main()
