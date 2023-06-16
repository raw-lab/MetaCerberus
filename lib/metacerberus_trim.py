# -*- coding: utf-8 -*-
"""metacerberus_trim.py: Module for trimming .fastq files
Uses fastp [https://github.com/OpenGene/fastp#quality-filter]
Uses porechop
"""

import os
from pathlib import Path
import subprocess


# Trim single end reads
def trimSingleRead(key_value, config, subdir):
    path = Path(config['DIR_OUT'], subdir)

    key = key_value[0]
    value = key_value[1]

    trimmedRead = path / f'trimmed_{key}.fastq'

    done = path / "complete"
    if not config['REPLACE'] and done.exists() and trimmedRead.exists():
        return trimmedRead
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

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

    done.touch()
    return trimmedRead


# Trim paired end reads
def trimPairedRead(key_value, config, subdir):
    path = Path(config['DIR_OUT'], subdir)

    key = key_value[0]
    value = key_value[1]
    outR1 = f"trimmed_{os.path.basename(value[0])}"
    outR2 = f"trimmed_{os.path.basename(value[1])}"

    trimmedReads = (Path(path, outR1), Path(path, outR2))

    done = path / "complete"
    if not config['REPLACE'] and done.exists() and trimmedReads.exists():
        return trimmedReads
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    adapters = "" if not config['ADAPTERS'] else f"--adapter_fasta {config['ADAPTERS']}"

    command = f"{config['EXE_FASTP']} -i {value[0]} -I {value[1]} -o {trimmedReads[0]} -O {trimmedReads[1]} -p 20 -M 30 -q 30 --low_complexity_filter {adapters} -h {path}/fastp.{key}.html -j {path}/fastp.{key}.json"
    try:
        with open(f"{path}/stdout.txt", 'w') as fout, open(f"{path}/stderr.txt", 'w') as ferr:
            subprocess.run(command, shell=True, check=False, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        print("Error: Failed to execute trimPairedRead: " + key_value)

    done.touch()
    return trimmedReads
