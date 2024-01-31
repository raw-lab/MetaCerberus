# -*- coding: utf-8 -*-
"""metacerberus_genecall.py: Module for finding Open Reading Frames (ORF) in FASTA nucleotide files
Uses prodigal
Uses FGS+
"""

from pathlib import Path
import re
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

# Giant Virus
def findORF_prodgv(contig, config, subdir, meta=False):
    path = Path(config['DIR_OUT'], subdir)
    done = path / "complete"

    faaOut  = path / "proteins.faa"

    if not config['REPLACE'] and done.exists() and faaOut.exists():
            return faaOut
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    command = f"{config['EXE_PRODIGAL-GV']} -i {contig} -a {faaOut} -o {path / 'proteins.gbk'} {'-p meta' if meta else ''}"
    print(command)
    try:
        with Path(path,"stdout.txt").open('w') as fout, Path(path,"stderr.txt").open('w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        return None

    done.touch()
    return faaOut

# Phage
def findORF_phanotate(contig, config, subdir, meta=False):
    path = Path(config['DIR_OUT'], subdir)
    done = path / "complete"

    faaOut  = path / "proteins.faa"

    if not config['REPLACE'] and done.exists() and faaOut.exists():
            return faaOut
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    command = [config['EXE_PHANOTATE'], '-f', 'faa', contig] #, '-o', faaOut, contig]
        #awk '{ if (substr($1,1,1) != ">") gsub(/#|\+|\*/, ""); print $1 }'
    try:
        with faaOut.open('r') as fout, Path(path,"stderr.txt").open('w') as ferr:
            pout = subprocess.run(command, stdout=faaOut, stderr=ferr)
    except Exception as e:
         print(e)
    #    for line in pout:
    #        line=line.strip()
    #        if line.startswith('>'):
    #            print(line, file=fout)
    #        else:
    #            re.sub(r'[^A-Za-z]', '', line, file=fout)

    #try:
    #    subprocess.run(['sed', '-i', 's/#//g', faaOut])
    #except Exception as e:
    #    with Path(path,"stderr.txt").open('a') as ferr:
    #        print(e, file=ferr)

    done.touch()
    return faaOut
