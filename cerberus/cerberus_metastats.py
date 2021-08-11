# -*- coding: utf-8 -*-

"""cerberusQCcontigs.py: Module for checking quality of .fastq files
Uses checkm [https://www.bioinformatics.babraham.ac.uk/projects/fastqc/]
Uses countfasta.pl

$ checkm lineage_wf -t 28 -x fasta -f out.tab --tab_table /data/path/ /data/path/out/
$ countfasta.pl contigs.fasta >assembly-stats.txt
"""

import os
import subprocess


## checkContigs
def checkContigs(contig, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    
    contigPath = os.path.dirname(contig)
    ext = os.path.splitext(contig)[1][1:]
    
    # checkm
    try:
        command = f"{config['EXE_CHECKM']} lineage_wf -t {config['CPUS']} -x {ext} -f {path}/out.tab --tab_table {contigPath} {path}"
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            print(f"\nCheckM: {contigPath}\n", file=fout, flush=True)
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except:
        print(f"Error: checkm processing{contigPath}")
    # countAssembly.py
    try:
        command = f"countAssembly.py -f {contigPath} -i 100 > {path}/stats.txt"
        with open(f"{path}/stdout.txt", 'a') as fout, open(f"{path}/stderr.txt", 'a') as ferr:
            print(f"\ncoutAssembly: {contigPath}\n", file=fout, flush=True)
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except:
        print("Error: countAssembly.py failed: " + contigPath)
    # magpurify
    for filename in os.listdir(contigPath):
        if filename.endswith(tuple(config['EXT_FASTA'])):
            filepath = f"{contigPath}/{filename}"
            command = f"{config['EXE_MAGPURIFY']} clean-bin {filepath} {path}/mag {path}/mag-{filename}"
            with open(f"{path}/stdout.txt", 'a') as fout, open(f"{path}/stderr.txt", 'a') as ferr:
                print(f"\nMag Purify: {contig}\n", file=fout, flush=True)
                subprocess.run(command, shell=True, stdout=fout, stderr=ferr)


    return
