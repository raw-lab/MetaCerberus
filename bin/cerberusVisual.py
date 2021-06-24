# -*- coding: utf-8 -*-


import os
import subprocess


## findORF
def createReport(contig, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')



    fout.close()
    ferr.close()
    return None
