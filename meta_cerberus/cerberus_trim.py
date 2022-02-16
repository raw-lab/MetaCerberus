# -*- coding: utf-8 -*-
"""cerberus_trim.py: Module for trimming .fastq files
Uses fastp [https://github.com/OpenGene/fastp#quality-filter]
Uses porechop
"""

import os
import subprocess


## trimSingleRead
#
def trimSingleRead(key_value, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    key = key_value[0]
    value = key_value[1]

    trimmedRead = f'{path}/trimmed_{key}.fastq'

    adapters = "" if not config['ADAPTERS'] else f"--adapter_fasta {config['ADAPTERS']}"

    if config['NANOPORE']:
        command = f"{config['EXE_PORECHOP']} -i {value} -o {trimmedRead} --threads {config['CPUS']}"
    else:
        command = f"{config['EXE_FASTP']} -i {value} -o {trimmedRead} -p 20 -M 30 -q 30 --low_complexity_filter {adapters} -h {path}/fastp.{key}.html -j {path}/fastp.{key}.json"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        print("Error: Failed to execute trimSingleRead: " + command)

    return trimmedRead


## trimPairedRead
#
def trimPairedRead(key_value, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    key = key_value[0]
    value = key_value[1]
    outR1 = f"trimmed_{os.path.basename(value[0])}"
    outR2 = f"trimmed_{os.path.basename(value[1])}"

    trimmedReads = (os.path.join(path, outR1), os.path.join(path, outR2))

    adapters = "" if not config['ADAPTERS'] else f"--adapter_fasta {config['ADAPTERS']}"

    command = f"{config['EXE_FASTP']} -i {value[0]} -I {value[1]} -o {trimmedReads[0]} -O {trimmedReads[1]} -p 20 -M 30 -q 30 --low_complexity_filter {adapters} -h {path}/fastp.{key}.html -j {path}/fastp.{key}.json"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=False, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        print("Error: Failed to execute trimPairedRead: " + key_value)

    return trimmedReads


## End of script
