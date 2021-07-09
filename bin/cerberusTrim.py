# -*- coding: utf-8 -*-
"""rheaTrim.py: Module for trimming .fastq files
Uses fastp [https://github.com/OpenGene/fastp#quality-filter]

$ fastp -i in.fq.gz -o trim.fq.gz
$ fastp -i in.R1.fq.gz -I in.R2.fq.gz -o trim.R1.fq.gz -O trim.R2.fq.gz
"""

import os
import subprocess


# trimReads
def trimReads(rawRead, config, subdir):
    if type(rawRead[1]) is str:
        return trimSingleRead(rawRead, config, subdir)
    else:
        return trimPairedRead(rawRead, config, subdir)


## trimSingleRead
#
def trimSingleRead(fileFQ, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')
    key = fileFQ[0]
    value = fileFQ[1]
    trimmedRead = f'{path}/trim-{key}.fastq'

    try:
        # Fastp
        command = f"{config['EXE_FASTP']} -i {value} -o {trimmedRead} -p 20 -M 30 -q 30 --low_complexity_filter -h {path}/fastp.{key}.html -j {path}/fastp.{key}.json"
        subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
        # Porechop TODO: install Porechop in Cerberus Environment
        #command = f"{config['EXE_PORECHOP']} -i {value} -o {path}/porechop-{key}"
        #subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
        #trimmedRead = f"{path}/porechop-{key}"
    except:
        print("Error: Failed to execute trimSingleRead: " + command)
    fout.close()
    ferr.close()
    return trimmedRead


## trimPairedRead
#
def trimPairedRead(fileFQ, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')
    key = fileFQ[0]
    value = fileFQ[1]
    outR1 = f"trimmed_{os.path.basename(value[0])}"
    outR2 = f"trimmed_{os.path.basename(value[1])}"
    command = f"{config['EXE_FASTP']} -i {value[0]} -I {value[1]} -o {path}/{outR1} -O {path}/{outR2} -p 20 -M 30 -q 30 --low_complexity_filter --adapter_fasta {config['ADAPTER']} -h {path}/fastp.{key}.html -j {path}/fastp.{key}.json"
    trimmedRead = None
    try:
        subprocess.run(command, shell=True, check=False, stdout=fout, stderr=ferr)
        trimmedRead = (f"{path}/{outR1}", f"{path}/{outR2}")
    except:
        print("Error: Failed to execute trimSingleRead: " + fileFQ)
    fout.close()
    ferr.close()
    return trimmedRead


## End of script
