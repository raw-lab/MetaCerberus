import os
from os.path import isfile, join
import subprocess

def main():
    #dependencies

    #Need to first install Anaconda3 to make conda installer available
    #"pip install conda" is not sufficient
    
    prokka_cmd = "conda install -c conda-forge -c bioconda -c defaults prokka"
    subprocess.call(prokka_cmd, shell=True)
    
    hmmer_cmd = "conda install -c bioconda hmmer"
    subprocess.call(hmmer_cmd, shell=True)

if __name__ == "__main__":
    main()
