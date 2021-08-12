#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""cerberus.py: Versatile Functional Ontology Assignments for Metagenomes

Uses Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data.
"""


__version__ = "0.1"
__author__ = "Jose Figueroa"


import sys
import os
from os.path import join
import subprocess
import configargparse as argparse #replace argparse with: https://pypi.org/project/ConfigArgParse/
import pkg_resources as pkg #to import package data files
import time
import socket
import ray #multiprocessing
import re


# our package import.
from cerberus import (
    cerberus_qc, cerberus_trim, cerberus_decon, cerberus_format, cerberus_metastats,
    cerberus_genecall, cerberus_hmmer, cerberus_parser,
    cerberus_prostats, cerberus_visual, cerberus_report
)


##### Global Variables #####

# known file extensions
FILES_FASTQ = ['.fastq', '.fastq.gz']
FILES_FASTA = [".fasta", ".fa", ".fna", ".ffn"]
FILES_AMINO = [".faa"]

# refseq default locations (for decontamination)
REFSEQ = {
    "adapters": pkg.resource_filename("cerberus_data", "adapters.fna"),
    "illumina": pkg.resource_filename("cerberus_data", "phix174_ill.ref.fna"),
    "lambda": pkg.resource_filename("cerberus_data", "lambda-phage.fna"),
    "pacbio": pkg.resource_filename("cerberus_data", "PacBio_quality-control.fna")
}

# external dependencies
DEPENDENCIES = {
    'EXE_FASTQC': 'fastqc',
    'EXE_FASTP': 'fastp',
    'EXE_PORECHOP': 'porechop',
    'EXE_BBDUK': 'bbduk.sh',
    'EXE_PRODIGAL': 'prodigal',
    'EXE_HMMSEARCH': 'hmmsearch',
    'EXE_COUNT_ASSEMBLY': 'countAssembly.py'
    }

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

def logTime(dirout, host, funcName, path, time):
    with open(f'{dirout}/time.txt', 'a+') as outTime:
        print(host, funcName, time, path, file=outTime, sep='\t')
    return

## RAY WORKER THREAD ##
@ray.remote
def rayWorker(func, key, value, config, path):
    logTime(config["DIR_OUT"], socket.gethostname(), func.__name__, path, "start")
    start = time.time()
    ret = func(value, config, path)
    logTime(config["DIR_OUT"], socket.gethostname(), func.__name__, path, f"{time.time()-start:.2f} seconds")
    return key, ret


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
> cerberus.py --euk file1.fasta --euk file2.fasta --mic file3.fasta
> cerberus.py --config file.config
*Note: If a sequence is given in .fastq format, one of --nanopore, --illumina, or --pacbio is required.''')
    required.add_argument('-c', '--config', help = 'Path to config file, command line takes priority', is_config_file=True)
    required.add_argument('--mic', '--prod', action='append', default=[], help='Procaryote nucleotide sequence (includes microbes, bacteriophage)')
    required.add_argument('--euk', '--fgs', action='append', default=[], help='Eukaryote nucleotide sequence (includes other viruses, works all around for everything)')
    required.add_argument('--meta', action="append", default=[], help="Metagenomic nucleotide sequences (Uses prodigal)")
    required.add_argument('--super', action='append', default=[], help='Run sequence in both --mic and --euk modes')
    required.add_argument('--prot', '--amino', action='append', default=[], help='Protein Amino Acid sequence')
    # Raw-read identification
    readtype = parser.add_mutually_exclusive_group(required=False)
    readtype.add_argument('--illumina', action="store_true", help="Specifies that the given FASTQ files are from Illumina")
    readtype.add_argument('--nanopore', action="store_true", help="Specifies that the given FASTQ files are from Nanopore")
    readtype.add_argument('--pacbio', action="store_true", help="Specifies that the given FASTQ files are from PacBio")
    # optional flags
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--dir_out', type=str, default='./', help='path to output directory, creates "pipeline" folder. Defaults to current directory.')
    optional.add_argument('--scaf', action="store_true", help="Sequences are treated as scaffolds")
    optional.add_argument('--minscore', type=float, default=25, help="Filter for parsing HMMER results")
    optional.add_argument('--cpus', type=int, help="Number of CPUs to use per task. System will try to detect available CPUs if not specified")
    optional.add_argument('--replace', action="store_true", help="Flag to replace existing files. False by default")
    optional.add_argument('--version', '-v', action='version',
                        version=f'Cerberus: \n version: {__version__} June 24th 2021',
                        help='show the version number and exit')
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
    # Hidden from help, expected to load from config file
    dependencies = parser.add_argument_group()
    for key in DEPENDENCIES:
        dependencies.add_argument(f"--{key}", help=argparse.SUPPRESS)
    dependencies.add_argument('--adapters', type=str, default=REFSEQ['adapters'], help="FASTA File containing adapter sequences for trimming")
    dependencies.add_argument('--control_seq', type=str, default="default", help="FASTA File containing control sequences for decontamination")
    
    args = parser.parse_args()

    print("\nStarting Cerberus Pipeline\n")

    # Merge related arguments
    if args.super:
        args.euk += args.super
        args.mic += args.super

    # Check if required flags are set
    if not any([args.euk, args.mic, args.meta, args.prot]):
        parser.error('At least one sequence must be declared either in the command line or through the config file')

    for file in args.euk + args.mic + args.meta:
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
    args

    # Initialize Config Dictionary
    config = {}
    config['PATH'] = os.path.dirname(os.path.abspath(__file__))
    config['EXE_FGS+'] = os.path.abspath(os.path.join(config['PATH'], "FGS+/FGS+"))
    
    # load all args into config
    for arg,value in args.__dict__.items():
        if value is not None:
            if arg == "control_seq": arg = "refseq"
            arg = arg.upper()
            if type(value) is str and os.path.isfile(value):
                value = os.path.abspath(os.path.expanduser(value))
            config[arg] = value

    config['DIR_OUT'] = os.path.abspath(os.path.expanduser(os.path.join(args.dir_out, "pipeline")))
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
                print(f"{value:20} NOT FOUND, must be defined in config file as {key}:(path)")
        except:
            print(f"ERROR executing 'which {value}'")

    # Sanity Check of config file
    for key,value in config.items():
        if key.startswith("EXE_") and not os.path.isfile(value):
            parser.error(f"Unable to find file: {value}")

    # Initialize RAY for Multithreading
    ray.init()

    if 'CPUS' not in config:
        config['CPUS'] = int(ray.available_resources()['CPU'])
    print(f"Running RAY on {len(ray.nodes())} node(s)")
    print(f"Using {config['CPUS']} CPUs per node")


    start = time.time()
    logTime(config["DIR_OUT"], socket.gethostname(), "master", config["DIR_OUT"], "START")
    # Step 1 - Load Input Files
    print("\nSTEP 1: Loading sequence files:")
    fastq = {}
    fasta = {}
    amino = {}
    # Load protein input
    for item in args.prot:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_AMINO:
                amino[name] = item
            else:
                print(f'{item} is not a valid protein sequence')
    # Load microbial input
    for item in args.mic:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_FASTQ:
                fastq['mic_'+name] = item
            elif ext in FILES_FASTA:
                fasta['mic_'+name] = item
            elif ext in FILES_AMINO:
                print(f"WARNING: {item} is a protein sequence, please use --prot option for these.")
                amino[name] = item
        elif os.path.isdir(item):
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1]
                if ext in FILES_FASTQ + FILES_FASTA:
                    args.mic.append(os.path.join(item, file))
        else:
            print(f'{item} is not a valid sequence')
    # Load eukaryotic input
    for item in args.euk:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_FASTQ:
                fastq['euk_'+name] = item
            elif ext in FILES_FASTA:
                fasta['euk_'+name] = item
            elif ext in FILES_AMINO:
                print(f"WARNING: {item} is a protein sequence, please use --prot option for these.")
                amino[name] = item
        elif os.path.isdir(item):
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1]
                if ext in FILES_FASTQ + FILES_FASTA:
                    args.euk.append(os.path.join(item, file))
        else:
            print(f'{item} is not a valid sequence')
    # Load metagenomic input
    for item in args.meta:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_FASTQ:
                fastq['meta_'+name] = item
            elif ext in FILES_FASTA:
                fasta['meta_'+name] = item
            elif ext in FILES_AMINO:
                print(f"WARNING: {item} is a protein sequence, please use --prot option for these.")
                amino[name] = item
        elif os.path.isdir(item):
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1]
                if ext in FILES_FASTQ + FILES_FASTA:
                    args.meta.append(os.path.join(item, file))
        else:
            print(f'{item} is not a valid sequence')
    
    print(f"Fastq sequences:\n  {fastq}")
    print(f"Fasta sequences:\n  {fasta}")
    print(f"Protein Sequences:\n  {amino}")


    # Step 2 (check quality of fastq files)
    jobsQC = []
    if fastq:
        print("\nSTEP 2: Checking quality of fastq files")
        for key,value in fastq.items():
            jobsQC.append(rayWorker.remote(cerberus_qc.checkQuality, key, value, config, f"{STEP[2]}/{key}"))


    # Step 3 (trim fastq files)
    jobTrim = []
    if fastq:
        print("\nSTEP 3: Trimming fastq files")
        for key,value in fastq.items():
            if "R1.fastq" in value:
                reverse = value.replace("R1.fastq", "R2.fastq")
                if reverse in fastq.values():
                    print("Paired end found:", key)
                    jobTrim.append(rayWorker.remote(cerberus_trim.trimPairedRead, key, [key, [value,reverse]], config, f"{STEP[3]}/{key}"))
                    continue
            if "R2.fastq" in value and value.replace("R2.fastq", "R1.fastq") in fastq.values():
                print("Skipping reverse read:", key)
                continue
            jobTrim.append(rayWorker.remote(cerberus_trim.trimSingleRead, key, [key, value], config, f"{STEP[3]}/{key}"))

    # Wait for Trimmed Reads
    trimmedReads = {}
    for job in jobTrim:
        key,value = ray.get(job)
        if type(value) is str:
            trimmedReads[key] = value
        else:
            rev = key.replace("R1", "R2")
            trimmedReads[key] = value[0]
            trimmedReads[rev] = value[1]
        jobsQC.append(rayWorker.remote(cerberus_qc.checkQuality, key, value, config, f"{STEP[3]}/{key}/quality"))


    # step 4 Decontaminate (adapter free read to clean quality read + removal of junk)
    jobDecon = []
    if trimmedReads:
        print("\nSTEP 4: Decontaminating trimmed files")
#        for key,value in trimmedReads.items():
#            jobDecon.append(rayWorker.remote(cerberus_decon.deconSingleReads, key, [key, value], config, f"{STEP[4]}/{key}"))
        for key,value in trimmedReads.items():
            if "R1.fastq" in value:
                reverse = value.replace("R1.fastq", "R2.fastq")
                if reverse in fastq.values():
                    print("Paired end found:", key)
                    jobDecon.append(rayWorker.remote(cerberus_decon.deconPairedReads, key, [key, [value,reverse]], config, f"{STEP[4]}/{key}"))
                    continue
            if "R2.fastq" in value and value.replace("R2.fastq", "R1.fastq") in fastq.values():
                print("Skipping reverse read:", key)
                continue
            jobDecon.append(rayWorker.remote(cerberus_decon.deconSingleReads, key, [key, value], config, f"{STEP[4]}/{key}"))

    # Wait for Decontaminating Reads
    deconReads = {}
    #for job in jobDecon:
        #key,value = ray.get(job)
        #deconReads[key] = value
    for job in jobDecon:
        key,value = ray.get(job)
        if type(value) is str:
            deconReads[key] = value
        else:
            rev = key.replace("R1", "R2")
            deconReads[key] = value[0]
            deconReads[rev] = value[1]
        jobsQC.append(rayWorker.remote(cerberus_qc.checkQuality, key, value, config, f"{STEP[4]}/{key}/quality"))


    # step 5a for cleaning contigs
    jobContigs = [] #TODO: Add config flag for contigs/scaffolds/raw reads
    if fasta:# and "scaf" in config flags:
        print("\nSTEP 5a: Removing N's from contig files")
        for key,value in fasta.items():
            jobContigs.append(rayWorker.remote(cerberus_format.removeN, key, value, config, f"{STEP[5]}/{key}"))
    
    for job in jobContigs:
        key,value = ray.get(job)
        fasta[key] = value

    # step 5b Format (convert fq to fna. Remove quality scores and N's)
    jobFormat = []
    if deconReads:
        print("\nSTEP 5b: Reformating FASTQ files to FASTA format")
        for key,value in deconReads.items():
            jobFormat.append(rayWorker.remote(cerberus_format.reformat, key, value, config, f"{STEP[5]}/{key}"))

    for job in jobFormat:
        key, value = ray.get(job)
        fasta[key] = value

    # step 6 Metaome Stats
    jobReadStats = []
    if fasta:
        print("\nSTEP 6: Metaome Stats\n")
        for key,value in fasta.items():
                jobReadStats.append(rayWorker.remote(cerberus_metastats.getReadStats, key, value, config, join(STEP[6], key)))

    # step 7 (ORF Finder)
    jobGenecall = []
    if fasta:
        print("\nSTEP 7: ORF Finder")
        for key,value in fasta.items():
            if key.startswith("euk_"):
                jobGenecall.append(rayWorker.remote(cerberus_genecall.findORF_euk, key, value, config, f"{STEP[7]}/{key}"))
            elif key.startswith("meta_"):
                jobGenecall.append(rayWorker.remote(cerberus_genecall.findORF_meta, key, value, config, f"{STEP[7]}/{key}"))
            else:
                jobGenecall.append(rayWorker.remote(cerberus_genecall.findORF_mic, key, value, config, f"{STEP[7]}/{key}"))

    # Waiting for GeneCall
    for job in jobGenecall:
        key,value = ray.get(job)
        amino[key] = value


    # step 8 (HMMER)
    print("\nSTEP 8: HMMER Search")
    jobHMM = []
    for key,value in amino.items():
        jobHMM.append(rayWorker.remote(cerberus_hmmer.searchHMM, key, value, config, f"{STEP[8]}/{key}"))

    print("Waiting for HMMER")
    hmmFoam = {}
    jobProtStat = []
    while(jobHMM):
        ready, jobHMM = ray.wait(jobHMM)
        key,value = ray.get(ready[0])
        hmmFoam[key] = value
        # Protein Stats Jobs
        jobProtStat.append(rayWorker.remote(cerberus_prostats.getStats, key, [amino[key], value], config, ""))


    # step 9 (Parser)
    print("\nSTEP 9: Parse HMMER results")
    jobParse = []
    for key,value in hmmFoam.items():
        jobParse.append(rayWorker.remote(cerberus_parser.parseHmmer, key, value, config, f"{STEP[9]}/{key}"))

    print("Waiting for parsed results")
    hmmRollup = {}
    hmmTables = {}
    figSunburst = {}
    figCharts = {}
    while(jobParse):
        ready, jobParse = ray.wait(jobParse)
        key,value = ray.get(ready[0])
        hmmRollup[key] = value
        hmmTables[key] = cerberus_parser.createTables(value)
        figSunburst[key] = cerberus_visual.graphSunburst(hmmTables[key])
        figCharts[key] = cerberus_visual.graphBarcharts(key, value)


    # step 10 (Report)
    print("\nSTEP 10: Creating Reports")
    outpath = os.path.join(config['DIR_OUT'], STEP[10])

    # write read-stats
    while(jobReadStats):
        ready, jobReadStats = ray.wait(jobReadStats)
        key,value = ray.get(ready[0])
        outfile = os.path.join(outpath, key, "read_stats.txt")
        os.makedirs(os.path.join(outpath, key), exist_ok=True)
        with open(outfile, 'w') as writer:
            writer.write(value)

    # write protein-stats
    outfile = os.path.join(outpath, "combined", "protein_stats.tsv")
    os.makedirs(os.path.join(outpath, "combined"), exist_ok=True)
    header = True
    with open(outfile, 'w') as statsOut:
        while(jobProtStat):
            ready, jobProtStat = ray.wait(jobProtStat)
            key,value = ray.get(ready[0])
            if header:
                print("Sample", *list(value.keys()), sep='\t', file=statsOut)
                header = False
            print(key, *value.values(), sep='\t', file=statsOut)

    # write roll-up tables
    for sample,tables in hmmTables.items():
        for name,table in tables.items():
            cerberus_report.writeTables(table, figCharts[sample][2][name], f"{outpath}/{sample}/{name}")

    # figures
    pcaFigures = None
    if len(hmmTables) < 3:
        print("NOTE: PCA Tables and Combined report created only when there are at least three samples.\n")
    else:
        pcaFigures = cerberus_visual.graphPCA(hmmTables)
    cerberus_report.createReport(figSunburst, figCharts, pcaFigures, config, STEP[10])


    # Wait for misc jobs
    jobs = jobsQC
    ready, jobs = ray.wait(jobs, num_returns=len(jobs), timeout=1) # clear buffer
    while(jobs):
        print(f"Waiting for {len(jobs)} jobs.")
        ready, jobs = ray.wait(jobs)
        print("Finished: ", ray.get(ready[0]))


    # Finished!
    print("\nFinished Pipeline")
    logTime(config["DIR_OUT"], socket.gethostname(), "master", config["DIR_OUT"], f"{time.time()-start:.2f} seconds")
    return 0


## Start main method
if __name__ == "__main__":
    sys.exit(main())

## End of script
