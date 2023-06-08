#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""metacerberus.py: Versatile Functional Ontology Assignments for Metagenomes

Uses Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data.
"""


__version__     = "1.1"
__author__      = "Jose L. Figueroa III, Richard A. White III"
__copyright__   = "Copyright 2022"
__date__        = "July 2022"

def warn(*args, **kwargs):
    #print("args", str(args))
    pass
import warnings
warnings.warn = warn

import sys
import os
import re
from pathlib import Path
import psutil
import shutil
import subprocess
import configargparse as argparse #replace argparse with: https://pypi.org/project/ConfigArgParse/
import pkg_resources as pkg #to import package data files
import time
import datetime
from urllib import request
import socket
import ray #parallel-processing
import pandas as pd


# our package import
from meta_cerberus import (
    metacerberus_setup,
    metacerberus_qc, metacerberus_merge, metacerberus_trim, metacerberus_decon, metacerberus_formatFasta, metacerberus_metastats,
    metacerberus_genecall, metacerberus_hmm, metacerberus_parser,
    metacerberus_prostats, metacerberus_visual, metacerberus_report, Chunker
)


##### Global Variables #####

# known file extensions
FILES_FASTQ = ['.fastq', '.fastq.gz']
FILES_FASTA = [".fasta", ".fa", ".fna", ".ffn"]
FILES_AMINO = [".faa"]

# External file downloads
pathDB = pkg.resource_filename("meta_cerberus", "cerberusDB")
pathFGS = pkg.resource_filename("meta_cerberus", "FGS")

# refseq default locations (for decontamination)
REFSEQ = {
    "adapters": pkg.resource_filename("meta_cerberus", "dependency_files/adapters.fna"),
    "illumina": pkg.resource_filename("meta_cerberus", "dependency_files/phix174_ill.ref.fna"),
    "lambda": pkg.resource_filename("meta_cerberus", "dependency_files/lambda-phage.fna"),
    "pacbio": pkg.resource_filename("meta_cerberus", "dependency_files/PacBio_quality-control.fna")
}

# external dependencies
DEPENDENCIES = {
    'EXE_FASTQC': 'fastqc',
    'EXE_FLASH' : 'flash2',
    'EXE_FASTP': 'fastp',
    'EXE_PORECHOP': 'porechop',
    'EXE_BBDUK': 'bbduk.sh',
    'EXE_FGS': 'FragGeneScanRs',
    'EXE_PRODIGAL': 'prodigal',
    'EXE_HMMSEARCH': 'hmmsearch',
    'EXE_COUNT_ASSEMBLY': 'countAssembly.py'
    }

# Databases
DB_HMM = dict(
    KOFam_all=Path(pathDB, 'KOFam_all.hmm.gz'),
    KOFam_prokaryote=Path(pathDB, 'KOFam_prokaryote.hmm.gz'),
    KOFam_eukaryote=Path(pathDB, 'KOFam_eukaryote.hmm.gz'),
    COG=Path(pathDB, 'COG-noIter.hmm.gz'),
    CAZy=Path(pathDB, 'CAZy.hmm.gz'),
    PHROG=Path(pathDB, 'PHROG.hmm.gz'),
    VOG=Path(pathDB, 'VOG.hmm.gz'),
    )

# step names
STEP = {
    1:"step_01-loadFiles",
    2:"step_02-QC",
    3:"step_03-trim",
    4:"step_04-decontaminate",    
    5:"step_05-format",
    6:"step_06-metaomeQC",
    7:"step_07-geneCall",
    8:"step_08-hmmer",
    9:"step_09-parse",
    10:"step_10-visualizeData"}



## PRINT to stderr ##
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    return

def set_add(to_set:set, item, msg:str):
    if item not in to_set:
        to_set.add(item)
        print('\n', msg, '\n', sep='')
    return to_set

def logTime(dirout, host, funcName, path, time):
    with open(f'{dirout}/time.tsv', 'a+') as outTime:
        print(host, funcName, time, path, file=outTime, sep='\t')
    return


## RAY WORKER THREADS ##
@ray.remote
def rayWorker(func, key, value, config, path):
    start = time.time()
    ret = func(value, config, path)
    end = str(datetime.timedelta(seconds=time.time()-start))
    logTime(config["DIR_OUT"], socket.gethostname(), func.__name__, path, end)
    return key, ret

## Ray Worker Threads ##
@ray.remote
def rayWorkerThread(func, key, dir_log, params:list):
    start = time.time()
    ret = func(*params)
    end = str(datetime.timedelta(seconds=time.time()-start)) #time.strftime("%H:%M:%S", time.gmtime(time.time()-start))
    logTime(dir_log, socket.gethostname(), func.__name__, key, end)
    return key, ret, func.__name__


## MAIN
def main():
    ## Parse the command line
    parser = argparse.ArgumentParser(add_help=False)
    parser.set_defaults()
    # At least one of these options are required
    required = parser.add_argument_group('''Required arguments
At least one sequence is required.
<accepted formats {.fastq .fasta .faa .fna .ffn .rollup}>
Example:
> metaerberus.py --prodigal file1.fasta
> metacerberus.py --config file.config
*Note: If a sequence is given in .fastq format, one of --nanopore, --illumina, or --pacbio is required.''')
    required.add_argument('-c', '--config', help = 'Path to config file, command line takes priority', is_config_file=True)
    required.add_argument('--prodigal', action='append', default=[], help='Prokaryote nucleotide sequence (includes microbes, bacteriophage)')
    required.add_argument('--fraggenescan', action='append', default=[], help='Eukaryote nucleotide sequence (includes other viruses, works all around for everything)')
    required.add_argument('--super', action='append', default=[], help='Run sequence in both --prodigal and --fraggenescan modes')
    required.add_argument('--protein', '--amino', action='append', default=[], help='Protein Amino Acid sequence')
    # Raw-read identification
    readtype = parser.add_mutually_exclusive_group(required=False)
    readtype.add_argument('--illumina', action="store_true", help="Specifies that the given FASTQ files are from Illumina")
    readtype.add_argument('--nanopore', action="store_true", help="Specifies that the given FASTQ files are from Nanopore")
    readtype.add_argument('--pacbio', action="store_true", help="Specifies that the given FASTQ files are from PacBio")
    # optional flags
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--setup', action="store_true", help="Set this flag to ensure dependencies are setup [False]")
    optional.add_argument('--uninstall', action="store_true", help="Set this flag to remove downloaded databases and FragGeneScan+ [False]")
    optional.add_argument('--dir_out', type=str, default='./results-metacerberus', help='path to output directory, creates "pipeline" folder. Defaults to current directory. [./results-metacerberus]')
    optional.add_argument('--meta', action="store_true", help="Metagenomic nucleotide sequences (for prodigal) [False]")
    optional.add_argument('--scaffolds', action="store_true", help="Sequences are treated as scaffolds [False]")
    optional.add_argument('--minscore', type=float, default=25, help="Filter for parsing HMMER results [25]")
    optional.add_argument('--cpus', type=int, help="Number of CPUs to use per task. System will try to detect available CPUs if not specified [Auto Detect]")
    optional.add_argument('--chunker', type=int, default=0, help="Split files into smaller chunks, in Megabytes [Disabled by default]")
    optional.add_argument('--replace', action="store_true", help="Flag to replace existing files. [False]")
    optional.add_argument('--keep', action="store_true", help="Flag to keep temporary files. [False]")
    optional.add_argument('--hmm', type=str, default='KOFam_all', help="Specify a custom HMM file for HMMER. Default uses downloaded FOAM HMM Database")
    optional.add_argument('--class', type=str, default='', help='path to a tsv file which has class information for the samples. If this file is included scripts will be included to run Pathview in R')
    optional.add_argument('--slurm_nodes', type=str, default="", help=argparse.SUPPRESS)# help='list of node hostnames from SLURM, i.e. $SLURM_JOB_NODELIST.')
    optional.add_argument('--tmpdir', type=str, default="", help='temp directory for RAY [system tmp dir]')
    optional.add_argument('--version', '-v', action='version',
                        version=f'MetaCerberus: \n version: {__version__} {__date__}',
                        help='show the version number and exit')
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
    # Hidden from help, expected to load from config file
    dependencies = parser.add_argument_group()
    for key in DEPENDENCIES:
        dependencies.add_argument(f"--{key}", help=argparse.SUPPRESS)
    dependencies.add_argument('--adapters', type=str, default=REFSEQ['adapters'], help="FASTA File containing adapter sequences for trimming")
    dependencies.add_argument('--control_seq', type=str, default="default", help="FASTA File containing control sequences for decontamination")

    args = parser.parse_args()

    if args.uninstall:
        metacerberus_setup.Remove(pathDB, pathFGS)

    if args.setup:
        metacerberus_setup.FGS(pathFGS)
        metacerberus_setup.Download(pathDB)

    if args.setup or args.uninstall:
        return 0


    dbHMM = dict()
    for i,hmm in enumerate([x.strip() for x in args.hmm.split(',')], 1):
        print(f"HMM: '{hmm}'")
        if hmm in DB_HMM:
            if DB_HMM[hmm].exists():
                dbHMM[hmm] = DB_HMM[hmm]
            else:
                print(f"ERROR: Cannot use '{hmm}', please download it using 'metacerberus.py --setup")
        else:
            print(f"ERROR: Cannot use '{hmm}', custom databases not supported yet. Please use one of:", *list(DB_HMM.keys()))
    if not len(dbHMM):
        print("ERROR: No HMM DB Loaded")
        return 1

    print("\nStarting MetaCerberus Pipeline\n")

    # Merge related arguments
    if args.super:
        args.prodigal += args.super
        args.fraggenescan += args.super

    # Check if required flags are set
    if not any([args.prodigal, args.fraggenescan, args.protein]):
        parser.error('At least one sequence must be declared either in the command line or through the config file')
    # Check sequence type
    for file in args.prodigal + args.fraggenescan:
        if '.fastq' in file:
            if not any([args.illumina, args.nanopore, args.pacbio]):
                parser.error('A .fastq file was given, but no flag specified as to the type.\nPlease use one of --illumina, --nanopore, or --pacbio')
            elif args.control_seq =="default":
                if args.illumina:
                    args.control_seq = REFSEQ["illumina"]
                if args.nanopore:
                    args.control_seq = REFSEQ["lambda"]
                if args.pacbio:
                    args.control_seq = REFSEQ["pacbio"]

    # Initialize Config Dictionary
    config = {}
    #config['PATH'] = os.path.dirname(os.path.abspath(__file__))
    config['STEP'] = STEP
    config['PATHDB'] = pathDB

    # Get FGS+ Folder from Library Path
    config['EXE_FGS'] = os.path.join(pathFGS, DEPENDENCIES["EXE_FGS"])

    # load all args into config
    for arg,value in args.__dict__.items():
        if value is not None:
            if arg == "control_seq": arg = "refseq"
            arg = arg.upper()
            if type(value) is str and os.path.isfile(value):
                value = os.path.abspath(os.path.expanduser(value))
            config[arg] = value
    config['HMM'] = dbHMM
    

    # Create output directory
    config['DIR_OUT'] = os.path.abspath(os.path.expanduser(args.dir_out))
    os.makedirs(config['DIR_OUT'], exist_ok=True)

    # Sequence File extensions
    config['EXT_FASTA'] = FILES_FASTA
    config['EXT_FASTQ'] = FILES_FASTQ
    config['EXT_AMINO'] = FILES_AMINO

    # search dependency paths TODO: Check versions as well
    print("Checking for external dependencies:")
    for key,value in DEPENDENCIES.items():
        # skip environment check if declared in config
        if key in config:
            print(f"{value:20} {config[key]}")
            continue
        # search environment for executable
        try:
            proc = subprocess.run(["which", value], stdout=subprocess.PIPE, text=True)
            path = proc.stdout.strip()
            if proc.returncode == 0:
                print(f"{value:20} {path}")
                config[key] = path
            else:
                print(f"{value:20} NOT FOUND, must be defined in config file as {key}:<path>")
        except:
            print(f"ERROR executing 'which {value}'")

    # Check for dependencies
    for key,value in config.items():
        if key.startswith("EXE_") and not os.path.isfile(value):
            parser.error(f"Unable to find file: {value}")


    # Initialize RAY for Multithreading
    print("Initializing RAY")
    #if config['TMPDIR']:
    #    tmpdir = os.path.abspath(os.path.expanduser(config['TMPDIR']))
    #    os.environ['RAY_TMPDIR'] = tmpdir
    #    os.makedirs(tmpdir, exist_ok=True)
    # First try if ray is setup for a cluster
    if config['SLURM_NODES']:
        metacerberus_setup.slurm(config['SLURM_NODES'])
    
    # Get CPU Count
    if 'CPUS' not in config:
        config['CPUS'] = psutil.cpu_count()
    try:
        ray.init(address='auto')#, log_to_driver=False)
        print("Started RAY on cluster")
    except:
        ray.init(num_cpus=config['CPUS'])#log_to_driver=False)
        print("Started RAY single node")
    print(f"Running RAY on {len(ray.nodes())} node(s)")
    print(f"Using {config['CPUS']} CPUs per node")


    startTime = time.time()
    # Step 1 - Load Input Files
    print("\nSTEP 1: Loading sequence files:")
    fastq = {}
    fasta = {}
    amino = {}
    # Load protein input
    for item in args.protein:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_AMINO:
                amino['Protein_'+name] = item
            else:
                print(f'{item} is not a valid protein sequence')
        elif os.path.isdir(item):
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1]
                if ext in FILES_AMINO:
                    args.protein.append(os.path.join(item, file))
    # Load prodigal input
    for item in args.prodigal:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_FASTQ:
                fastq['prodigal_'+name] = item
            elif ext in FILES_FASTA:
                fasta['prodigal_'+name] = item
            elif ext in FILES_AMINO:
                print(f"WARNING: Ignoring protein sequence '{item}', please use --protein option for these.")
        elif os.path.isdir(item):
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1]
                if ext in FILES_FASTQ + FILES_FASTA:
                    args.prodigal.append(os.path.join(item, file))
        else:
            print(f'{item} is not a valid sequence')
    # Load FGS+ input
    for item in args.fraggenescan:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_FASTQ:
                fastq['FragGeneScan_'+name] = item
            elif ext in FILES_FASTA:
                fasta['FragGeneScan_'+name] = item
            elif ext in FILES_AMINO:
                print(f"WARNING: Ignoring protein sequence '{item}', please use --protein option for these.")
        elif os.path.isdir(item):
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1]
                if ext in FILES_FASTQ + FILES_FASTA:
                    args.fraggenescan.append(os.path.join(item, file))
        else:
            print(f'{item} is not a valid sequence')
    
    print(f"Processing {len(fastq)} fastq sequences")
    print(f"Processing {len(fasta)} fasta sequences")
    print(f"Processing {len(amino)} protein Sequences")

    # Main Pipeline
    pipeline = list()

    jobsQC = []
    
    # Entry Point: Fastq
    if fastq:
        # Step 2 (check quality of fastq files)
        print("\nSTEP 2: Checking quality of fastq files")
        for key,value in fastq.items():
            pipeline.append(rayWorkerThread.remote(metacerberus_qc.checkQuality, key, config['DIR_OUT'], [value, config, f"{STEP[2]}/{key}"]))
        print("\nSTEP 3: Trimming fastq files")
        # Merge Paired End Reads
        fastqPaired = {k:v for k,v in fastq.items() if "R1.fastq" in v and v.replace("R1.fastq", "R2.fastq") in fastq.values() }
        for key,value in fastqPaired.items():
            reverse = fastq.pop(key.replace("R1", "R2"))
            fastq[key] = metacerberus_merge.mergePairedEnd([value,reverse], config, f"{STEP[3]}/{key}/merged")
        del fastqPaired # memory cleanup
        # Trim
        for key,value in fastq.items():
            pipeline.append(rayWorkerThread.remote(metacerberus_trim.trimSingleRead, key, config['DIR_OUT'], [[key, value], config, Path(STEP[3], key)]))

    # Step 5 Contig Entry Point
    #TODO: Add config flag for contigs/scaffolds/raw reads
    # Only do this if a fasta file was given, not if fastq
    if fasta:# and "scaffold" in config:
        print("\nSTEP 5a: Removing N's from contig files")
        for key,value in fasta.items():
            pipeline.append(rayWorkerThread.remote(metacerberus_formatFasta.removeN, key, config['DIR_OUT'], [value, config, Path(STEP[5], key)]))

    step_curr = set()
    NStats = dict()
    readStats = dict()
    report_path = os.path.join(config['DIR_OUT'], STEP[10])
    amino_queue = dict()

    while pipeline:
        ready,pipeline = ray.wait(pipeline, timeout=1)
        if not ready:
            continue
        key,value,func = ray.get(ready[0])

        if func == "checkQuality":
            name = key
            key = key.rstrip('_decon').rstrip('_trim')
            os.makedirs(os.path.join(report_path, key), exist_ok=True)
            shutil.copy(value, os.path.join(report_path, key, f"qc_{name}.html"))
        if func == "trimSingleRead":
            # Wait for Trimmed Reads
            fastq[key] = value
            pipeline.append(rayWorkerThread.remote(metacerberus_qc.checkQuality, key+'_trim', config['DIR_OUT'], [value, config, f"{STEP[3]}/{key}/quality"]))
            if fastq and config['ILLUMINA']:
                set_add(step_curr, 4, "STEP 4: Decontaminating trimmed files")
                #if 4 not in step_curr:
                #    step_curr.add(4)
                #    print("\nSTEP 4: Decontaminating trimmed files")
                pipeline.append(rayWorkerThread.remote(metacerberus_decon.deconSingleReads, config['DIR_OUT'], key, [[key, value], config, f"{STEP[4]}/{key}"]))
            else:
                set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
                #if 5.2 not in step_curr:
                #    step_curr.add(5.2)
                #    print("\nSTEP 5b: Reformating FASTQ files to FASTA format")
                pipeline.append(rayWorkerThread.remote(metacerberus_formatFasta.reformat, config['DIR_OUT'], key, [value, config, f"{STEP[5]}/{key}"]))
        if func == "deconSingleReads":
            fastq[key] = value
            pipeline.append(rayWorkerThread.remote(metacerberus_qc.checkQuality, key+'_decon', config['DIR_OUT'], [value, config, f"{STEP[4]}/{key}/quality"]))
        if func == "removeN":
            fasta[key] = value[0]
            if value[1]:
                NStats[key] = value[1]
            set_add(step_curr, 6, "STEP 6: Metaome Stats")
            #if 6 not in step_curr:
            #    step_curr.add(6)
            #    print("\nSTEP 6: Metaome Stats\n")
            readStats[key] = metacerberus_metastats.getReadStats(value[0], config, os.path.join(STEP[6], key))
            if 7 not in step_curr:
                step_curr.add(7)
                print("\nSTEP 7: ORF Finder")
            if key.startswith("FragGeneScan_"):
                pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_fgs, key, config['DIR_OUT'], [value[0], config, f"{STEP[7]}/{key}"]))
            else:
                if config['META']:
                    pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_meta, key, config['DIR_OUT'], [value[0], config, f"{STEP[7]}/{key}"]))
                else:
                    pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_prod, key, config['DIR_OUT'], [value[0], config, f"{STEP[7]}/{key}"]))
        if func == "reformat":
            fasta[key] = value
            if 6 not in step_curr:
                step_curr.add(6)
                print("\nSTEP 6: Metaome Stats\n")
            readStats[key] = metacerberus_metastats.getReadStats(value, config, os.path.join(STEP[6], key))
            if 7 not in step_curr:
                step_curr.add(7)
                print("\nSTEP 7: ORF Finder")
            if key.startswith("FragGeneScan_"):
                pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_fgs, key, config['DIR_OUT'], [value, config, f"{STEP[7]}/{key}"]))
            else:
                if config['META']:
                    pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_meta, key, config['DIR_OUT'], [value, config, f"{STEP[7]}/{key}"]))
                else:
                    pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_prod, key, config['DIR_OUT'], [value, config, f"{STEP[7]}/{key}"]))
        if func.startswith("findORF_"):
            if 8 not in step_curr:
                step_curr.add(8)
                print("\nSTEP 8: HMMER Search")
            if value:
                amino[key] = value
                amino_queue[key] = value
                if len(amino_queue) >= 4:
                    #for hmm in dbHMM.items():
                    #    pipeline.append(rayWorkerThread.remote(metacerberus_hmm.searchHMM, amino_queue.keys(), config['DIR_OUT'],
                    #                                           [amino_queue.values(), config, Path(STEP[8], key), hmm]))
                    amino_queue = dict()

    # End Phase 1
    

    # step 8 (HMMER)
    set_add(step_curr, 8, "STEP 8: HMMER Search")
    jobHMM = list()
    chunker = dict()
    hmm_tsv = dict()
    dictChunks = dict()
    limit = int(config["CPUS"]/4)
    iter_amino = iter(amino)
    for key in iter_amino:
        #tsv_file = os.path.join(config['DIR_OUT'], STEP[8], key, f"{key}.tsv")
        #if not config['REPLACE'] and os.path.exists(tsv_file):
        #    dictChunks[key] = tsv_file
        #    continue
        tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, "filtered.tsv")
        if not config['REPLACE'] and os.path.exists(tsv_filtered):
            hmm_tsv[key] = tsv_filtered
            continue

        # Split files into chunks
        if config['CHUNKER'] > 0:
            chunker[key] = Chunker.Chunker(amino[key], os.path.join(config['DIR_OUT'], 'chunks', key), f"{config['CHUNKER']}M", '>')
            c = 0
            for i in range(0, len(chunker[key].files), limit):
                files = chunker[key].files[i:i+limit]
                aminoAcids = {}
                for chunk in files:
                    aminoAcids[f'chunk_{c}'] = chunk
                    c += 1
                for hmm in dbHMM.items():
                    jobHMM.append(rayWorkerThread.remote(metacerberus_hmm.searchHMM, key, config['DIR_OUT'], [aminoAcids, config, f"{STEP[8]}/{key}", hmm]))
        else:
            aminoAcids = {}
            aminoAcids[key] = amino[key]
            for i in range(0, limit-1):
                try:
                    key = next(iter_amino)
                except:
                    break
                aminoAcids[key] = amino[key]
            for hmm in dbHMM.items():
                jobHMM.append(rayWorkerThread.remote(metacerberus_hmm.searchHMM, list(aminoAcids.keys()), config['DIR_OUT'], [aminoAcids, config, f"{STEP[8]}", hmm]))

    print("Waiting for HMMER")
    while jobHMM:
        readyHMM,jobHMM = ray.wait(jobHMM)
        keys,values,func = ray.get(readyHMM[0])
        if type(keys) is str:
            # files in list belongs to same key (chunks)
            for value in values:
                if keys not in dictChunks:
                    dictChunks[keys] = []
                dictChunks[keys].append(value)
        else:
            # files in list belongs to different keys
            for i in range(0,len(keys)):
                key = keys[i]
                value = values[i]
                if key not in dictChunks:
                    dictChunks[key] = []
                dictChunks[key].append(value)

    # Merge chunked results
    print("Merging HMMER Results")
    pipeline = []
    for key,value in dictChunks.items():
        tsv_file = Path(config['DIR_OUT'], STEP[8], key, f"{key}.tsv")
        with tsv_file.open('w') as writer:
            print("target", "query", "e-value", "score", "length", "start", "end", sep='\t', file=writer)
            for item in sorted(value):
                writer.write(open(item).read())
                os.remove(item)
        # Filter overlaps
        tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, "filtered.tsv")
        pipeline.append(rayWorkerThread.remote(metacerberus_hmm.filterHMM, key, config['DIR_OUT'], [tsv_file, tsv_filtered, config['PATHDB']]))
        if not config['KEEP']:
            Path(tsv_file).unlink(True)

    del dictChunks
    # Delete chunked files
    for key,value in chunker.items():
        for item in value.files:
            os.remove(item)

    print("Filtering HMMER Results")
    while pipeline:
        ready,pipeline = ray.wait(pipeline, timeout=0)
        if ready:
            key,value,func = ray.get(ready[0])
            hmm_tsv[key] = value

    # step 9 (Parser)
    print("\nSTEP 9: Parse HMMER results")
    jobParse = []
    for key,value in hmm_tsv.items():
        jobParse.append(rayWorker.remote(metacerberus_parser.parseHmmer, key, value, config, f"{STEP[9]}/{key}"))

    hmmRollup = {}
    hmmCounts = {}
    jobCounts = []
    while(jobParse + jobCounts):
        ready,jobParse = ray.wait(jobParse, timeout=0)
        if ready:
            key,value = ray.get(ready[0])
            hmmRollup[key] = value
            jobCounts.append(rayWorker.remote(metacerberus_parser.createCountTables, key, value, config, f"{STEP[9]}/{key}"))

        ready,jobCounts = ray.wait(jobCounts, timeout=0)
        if ready:
            key,value = ray.get(ready[0])
            hmmCounts[key] = value

    # step 10 (Report)
    print("\nSTEP 10: Creating Reports")

    # Copy report files from QC, Parser
    for key in hmmRollup.keys():
        os.makedirs(os.path.join(report_path, key), exist_ok=True)
        shutil.copy( os.path.join(config['DIR_OUT'], config['STEP'][9], key, "HMMER_top_5.tsv"), os.path.join(report_path, key) )

    # Write Stats
    print("Saving Statistics")
    protStats = {}
    for key in hmm_tsv.keys():
        protStats[key] = metacerberus_prostats.getStats(amino[key], hmm_tsv[key], hmmCounts[key], config)
    metacerberus_report.write_Stats(report_path, readStats, protStats, NStats, config)
    del protStats


    # write roll-up tables
    print("Creating rollup tables")
    for sample,tables in hmmCounts.items():
        os.makedirs(f"{report_path}/{sample}", exist_ok=True)
        for name,table in tables.items():
            metacerberus_report.writeTables(table, f"{report_path}/{sample}/{name}")
    for sample,tables in hmmRollup.items():
        os.makedirs(f"{report_path}/{sample}", exist_ok=True)
        for name,table in tables.items():
            shutil.copy(table, Path(report_path, sample, f'{name}_rollup.tsv'))


    # Counts Tables
    print("Creating Count tables")
    dfCounts = dict()
    for dbName in ['FOAM', 'KEGG', 'COG', 'CAZy', 'PHROG', 'VOG']:
        tsv_list = dict()
        for name in hmm_tsv.keys():
            table_path = Path(config['DIR_OUT'], STEP[9], name, f'counts_{dbName}.tsv')
            if table_path.exists():
                name = re.sub(rf'^FragGeneScan_|prodigal_|Protein_', '', name)
                tsv_list[name] = table_path
        combined_path = Path(config['DIR_OUT'], STEP[10], 'combined', f'counts_{dbName}.tsv')
        metacerberus_parser.merge_tsv(tsv_list, Path(combined_path))
        if combined_path.exists():
            dfCounts[dbName] = combined_path
        del(combined_path)


    # HTML of PCA
    pcaFigures = None
    if len(hmm_tsv) < 4:
        print("NOTE: PCA Tables created only when there are at least four sequence files.\n")
    else:
        print("PCA Analysis")
        pcaFigures = metacerberus_visual.graphPCA(dfCounts)
        Path(report_path, 'combined').mkdir(parents=True, exist_ok=True)
        metacerberus_report.write_PCA(os.path.join(report_path, "combined"), pcaFigures)

    # run post processing analysis in R
    if len(hmm_tsv) < 4:
        print("NOTE: Pathview created only when there are at least four sequence files.\n")
    else:
        if config['CLASS']:
            print("\nSTEP 11: Post Analysis with GAGE and PathView")
            outpathview = Path(report_path, 'pathview')
            outpathview.mkdir(exist_ok=True, parents=True)
            rscript = Path(outpathview, 'run_pathview.sh')

            # Check for internet
            try:#attempt to open Google
                request.urlopen('216.58.195.142', timeout=1)
                is_internet = True
            except request.URLError as err: 
                is_internet = False
            
            with rscript.open('w') as writer:
                writer.write(f"#!/bin/bash\n\n")
                for name,countpath in dfCounts.items():
                    if name not in ['FOAM', 'KEGG']:
                        continue
                    shutil.copy(countpath, Path(outpathview, f"{name}_counts.tsv"))
                    shutil.copy(config['CLASS'], Path(outpathview, f"{name}_class.tsv"))
                    writer.write(f"mkdir -p {name}\n")
                    writer.write(f"cd {name}\n")
                    writer.write(f"pathview-metacerberus.R ../{name}_counts.tsv ../{name}_class.tsv\n")
                    writer.write(f"cd ..\n")
                    outcmd = Path(outpathview, name)
                    outcmd.mkdir(parents=True, exist_ok=True)
                    if is_internet:
                        subprocess.run(['pathview-metacerberus.R', countpath, config['CLASS']],
                                        cwd=outcmd,
                                        stdout=Path(outcmd, 'stdout.txt').open('w'),
                                        stderr=Path(outcmd, 'stderr.txt').open('w')
                                    )
            if not is_internet:
                print(f"GAGE and Pathview require internet access to run. Run the script '{rscript}'")

    # HTML of Figures
    print("Creating combined HTML Sunburst and Bar Graphs")
    figSunburst = {}
    for key,value in hmmCounts.items():
        figSunburst[key] = metacerberus_visual.graphSunburst(value)
    
    @ray.remote
    def graphCharts(key, rollup, counts):
        return key, metacerberus_visual.graphBarcharts(rollup, counts)

    jobCharts = []
    for key,value in hmmRollup.items():
        jobCharts.append( graphCharts.remote(key, value, hmmCounts[key]) )
    
    figCharts = {}
    while(jobCharts):
        ready,jobCharts = ray.wait(jobCharts)
        if ready:
            key,value = ray.get(ready[0])
            figCharts[key] = value

    metacerberus_report.createReport(figSunburst, figCharts, config, STEP[10])

    # Finished!
    print("\nFinished Pipeline")
    end = str(datetime.timedelta(seconds=time.time()-startTime))
    logTime(config["DIR_OUT"], socket.gethostname(), "Total_Time", config["DIR_OUT"], end)

    return 0


## Start main method
if __name__ == "__main__":
    sys.exit(main())

## End of script
