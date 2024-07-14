# -*- coding: utf-8 -*-
"""metacerberus_genecall.py: Module for finding Open Reading Frames (ORF) in FASTA nucleotide files
Uses Pyrodigal
Uses Pyrodigal-gv
Uses FGS+
Uses Phanotate
"""

import re
from pathlib import Path
import subprocess
import pyrodigal
import pyrodigal_gv


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

    train = "complete"
    if config['ILLUMINA']:
         train = "illumina_10"
    elif config['NANOPORE'] or config['PACBIO']:
         train = "454_30"

    command = f"{config['EXE_FGS']} -p {config['CPUS']} -s {contig} -o {baseOut} -w 1 -t {train}"
    try:
        with Path(path,"stdout.txt").open('w') as fout, Path(path,"stderr.txt").open('w') as ferr:
            subprocess.run(command, shell=True, check=True, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        return None

    done.touch()
    return faaOut


# Microbial option
def findORF_prod(contig, config, subdir, meta=False, viral=False):
    path = Path(config['DIR_OUT'], subdir)
    path.mkdir(exist_ok=True, parents=True)
    done = path / "complete"

    faa = path / "proteins.faa"
    fna = faa.with_suffix(".fna")
    gff = faa.with_suffix(".gff")
    gbk = faa.with_suffix(".gbk")

    if not config['REPLACE'] and done.exists() and faa.exists():
        return faa
    done.unlink(missing_ok=True)

    if viral:
        orf_finder = pyrodigal_gv.ViralGeneFinder(meta=True, viral_only=True)
    elif not meta:
        train = pyrodigal.GeneFinder(meta=False).train(open(contig).read())
        orf_finder = pyrodigal.GeneFinder(training_info=train, meta=meta)
    else:
        orf_finder = pyrodigal.GeneFinder(meta=True)
    with open(contig, 'rt') as reader, open(faa, 'wt') as w_faa, open(fna, 'wt') as w_fna, open(gff, 'wt') as w_gff, open(gbk, 'wt') as w_gbk:
        line = reader.readline()
        while line:
            if line.startswith(">"):
                seq_id = line[1:].split()[0]
                seq = list()
                line = reader.readline()
                while line:
                    if line.startswith(">"):
                        break
                    seq += [line.strip()]
                    line = reader.readline()
                genes = orf_finder.find_genes("".join(seq))
                genes.write_translations(w_faa, seq_id)
                genes.write_genes(w_fna, seq_id)
                genes.write_gff(w_gff, seq_id)
                genes.write_genbank(w_gbk, seq_id)
                continue
            line = reader.readline()

    done.touch()
    return faa


# Phage
def findORF_phanotate(contig, config, subdir, meta=False):
    path = Path(config['DIR_OUT'], subdir)
    done = path / "complete"

    faa = path / "proteins.faa"
    fna = faa.with_suffix(".fna")
    gff = faa.with_suffix(".gff")
    gbk = faa.with_suffix(".gbk")

    if not config['REPLACE'] and done.exists() and faa.exists():
            return faa
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    ferr = Path(path, "stderr.txt").open('w')

    # Phanotate > genbank file
    command = [config['EXE_PHANOTATE'], '-f', 'genbank', contig]
    try:
        with gbk.open('w') as fout:
            subprocess.run(command, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e, file=ferr)
        return None

    re_fix = re.compile(r'\[(\d+)\.\.(\d+)\] \[(.+)\]')
    re_clean = re.compile(r'[+*#]')
    # Genbank > faa
    fout = Path(path, "stdout.txt").open('w')
    try:
        command = ["genbank.py", "-f", "faa", gbk]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=ferr, text=True)
        with faa.open('w') as faa_writer:
            for line in p.stdout:
                if line.startswith(">"):
                    faa_writer.write(re_fix.sub(r'\1_\2 \3', line))
                else:
                    faa_writer.write(re_clean.sub('', line))
    except Exception as e:
        print(e, file=ferr)
        return None
    # Genbank > GFF, FNA
    try:
        command = ["genbank.py", "-f", "gff", "-o", gff, gbk]
        p = subprocess.run(command, stdout=subprocess.PIPE, stderr=ferr, text=True)
        #TODO: Filtering out tRNA from GFF until figuring out how to put them in the FAA file. Causes report to fail if they don't match.
        with gff.open('w') as gff_writer:
            for line in p.stdout:
                if line.split('\t')[2] != "tRNA":
                    gff_writer.write(line)

        command = ["genbank.py", "-f", "fna", "-o", fna, gbk]
        subprocess.run(command, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e, file=ferr)

    ferr.close()
    fout.close()

    done.touch()
    return faa
