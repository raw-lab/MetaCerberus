# -*- coding: utf-8 -*-
"""metacerberus_genecall.py: Module for finding Open Reading Frames (ORF) in FASTA nucleotide files
Uses Pyrodigal
Uses Pyrodigal-gv
Uses FGS+
Uses Phanotate
"""

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

    faaOut  = path / "proteins.faa"

    if not config['REPLACE'] and done.exists() and faaOut.exists():
            return faaOut
    done.unlink(missing_ok=True)
    path.mkdir(exist_ok=True, parents=True)

    command = [config['EXE_PHANOTATE'], '-f', 'faa', contig] #, '-o', faaOut, contig]
    try:
        with faaOut.open('w') as fout, Path(path,"stderr.txt").open('w') as ferr:
            subprocess.run(command, stdout=fout, stderr=ferr)
    except Exception as e:
        print(e)
        return None

    #command = [config['EXE_PHANOTATE'], '-f', 'genbank', contig] #, '-o', faaOut, contig]
    #genbank.py outfile.gbk -f gff -o outfile.gff
    #genbank.py outfile.gbk -f fna -o outfile.fna
    #genbank.py outfile.gbk -f faa -o outfile.faa

    done.touch()
    return faaOut
