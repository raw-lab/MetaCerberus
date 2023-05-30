# -*- coding: utf-8 -*-
"""metacerberus_genecall.py: Module for finding Open Reading Frames (ORF) in FASTA nucleotide files
Uses prodigal
Uses FGS+
"""

import os
from pathlib import Path
import subprocess
import pkg_resources as pkg


# Eukaryotic option
def findORF_fgs(contig, config, subdir):
    path = Path(config['DIR_OUT'], subdir)
    done = path / "complete"

    baseOut = path / "proteins"
    faaOut  = path / "proteins.faa"

    if not config['REPLACE'] and done.exists() and faaOut.exists():
            return faaOut
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    command = f"{config['EXE_FGS']} -p {config['CPUS']} -s {contig} -o {baseOut} -w 1 -t complete"
    try:
        with Path(path,"stdout.txt").open('w') as fout, Path(path,"stderr.txt").open('w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        return None

    done.touch()
    return faaOut


# Microbial option
def findORF_prod(contig, config, subdir):
    path = Path(config['DIR_OUT'], subdir)
    done = path / "complete"

    faaOut = path / "proteins.faa"

    if not config['REPLACE'] and done.exists() and faaOut.exists():
        return faaOut
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    command = f"{config['EXE_PRODIGAL']} -i {contig} -o {path}/genes.gff -a {faaOut} -f gff"
    try:
        with Path(path, 'stdout.txt').open('w') as fout, Path(path, 'stderr.txt').open('w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)

    done.touch()    
    return faaOut


# Metagenome option
def findORF_meta(contig, config, subdir):
    path = Path(config['DIR_OUT'], subdir)
    done = path / "complete"

    faaOut = path / "proteins.faa"

    if not config['REPLACE'] and done.exists() and faaOut.exists():
        return faaOut
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    command = f"{config['EXE_PRODIGAL']} -i {contig} -o {path}/genes.gff -a {faaOut} -f gff -p meta"
    try:
        with Path(path, "stdout.txt").open('w') as fout, Path(path, "stderr.txt").open('w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)

    done.touch()
    return faaOut
