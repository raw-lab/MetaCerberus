#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""cerberus.py: Versatile Functional Ontology Assignments for Metagenomes

Uses Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data.
"""



__version__ = "1.0"



import sys
import os
import subprocess
import configargparse as argparse #replace argparse with: https://pypi.org/project/ConfigArgParse/
import time
import socket
import ray

# our package import.
from cerberus import (
    cerberus_qc, cerberus_trim, cerberus_decon, cerberus_format,
    cerberus_genecall, cerberus_hmmer, cerberus_parser,
    cerberus_visual, cerberus_report
)

#import cerberusQC, cerberusTrim, cerberusDecon, cerberusFormat
#import cerberusGenecall, cerberusParser, cerberusReport
#import cerberusVisual


##### Global Variables #####
# file extensions
FILES_FASTQ = ['.fastq', '.fastq.gz']
FILES_FASTA = [".fasta", ".fa", ".fna", ".ffn"]
FILES_AMINO = [".faa"]

# external dependencies
DEPENDENCIES = {
        'EXE_FASTQC': 'fastqc',
        'EXE_FASTP': 'fastp',
        'EXE_PORECHOP': 'porechop',
        'EXE_BBDUK': 'bbduk.sh',
        'EXE_PRODIGAL': 'prodigal',
        'EXE_HMMSEARCH': 'hmmsearch'}

# step names
STEP = {
    1:"step_01-loadFiles",
    2:"step_02-QC",
    3:"step_03-trim",
    4:"step_04-decontaminate",    
    5:"step_05-format",
    6:"step_06-geneCall",
    7:"step_07-hmmer",
    8:"step_08-parse",
    9:"step_09-visualizeData"}


## PRINT to stderr ##
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    return


## RAY WORKER THREAD ##
@ray.remote
def rayWorker(func, key, value, config, path):
    start = time.time()
    eprint(f"{socket.gethostname()} | {func.__name__} | {path}")
    ret = func(value, config, path)
    with open(f'{config["DIR_OUT"]}/time.txt', 'a+') as outTime:
        outTime.write(f'{func.__name__}\t{path}\t{time.time()-start:.2f} seconds\n')
    return key, ret


## MAIN
def main():
    ## Parse the command line
    parser = argparse.ArgumentParser(add_help=False)
    parser.set_defaults()
    # At least one of these options are required
    required = parser.add_argument_group('''At least one sequence is required
<accepted formats {.fastq .fasta .faa .fna .ffn .rollup}>
Example:
> cerberus.py --euk file1.fasta --euk file2.fasta --mic file3.fasta
> cerberus.py --config file.config''')
    readtype = parser.add_mutually_exclusive_group(required=False)
    optional = parser.add_argument_group('optional arguments')
    
    required.add_argument('-c', '--config', help = 'Path to config file, command line takes priority', is_config_file=True)
    required.add_argument('--euk', '--prod', action='append', default=[], help='Eukaryote sequence (includes other viruses)')
    required.add_argument('--mic', '--fgs', action='append', default=[], help='Microbial sequence (includes bacteriophage)')
    required.add_argument('--super', action='append', default=[], help='Run sequence in both --mic and --euk modes')
    required.add_argument('--prot', '--amino', action='append', default=[], help='Protein Amino Acid sequence')
    
    #args = parser.parse_known_args()

    # Raw-read identification
    readtype.add_argument('--nanopore')
    readtype.add_argument('--illumina')
    readtype.add_argument('--pacbio')
    # optional flags
    optional.add_argument('--dir_out', help='path to output directory, creates "pipeline" folder. Defaults to current directory.', type=str)
    optional.add_argument('--scaf', action="store_true", help="Sequences are treated as scaffolds")
    optional.add_argument('--meta', action="store_true", help="Metagenomic flag for Prodigal (Eukaryote)")
    optional.add_argument('--minscore', type=float, default=25, help="Filter for parsing HMMER results")
    optional.add_argument('--cpus', type=int, help="Number of CPUs to use per task. System will try to detect available CPUs if not specified")
    optional.add_argument('--replace', action="store_true", help="Flag to replace existing files. False by default")
    optional.add_argument('--version', '-v', action='version',
                        version='Cerberus: \n version: {} June 24th 2021'.format(__version__),
                        help='show the version number and exit')
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
    # Hidden from help, expected to load from config file
    dependencies = parser.add_argument_group()
    for key in DEPENDENCIES:
        dependencies.add_argument(f"--{key}", help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Merge related arguments
    if args.super:
        args.euk += args.super
        args.mic += args.super

    # Check if required flags are set
    if not any([args.euk, args.mic, args.prot]):
        parser.print_help()
        parser.error('At least one sequence must be declared either in the command line or through the config file')

    # Initialize Config Dictionary
    config = {}
    config['PATH'] = os.path.dirname(os.path.abspath(__file__))
    config['EXE_FGS+'] = os.path.abspath(os.path.join(config['PATH'], "FGS+/FGS+"))

    # load all args into config
    for arg,value in args.__dict__.items():
        if value is not None:
            arg = arg.upper()
            if arg.startswith("EXE_"):
                value = os.path.abspath(os.path.expanduser(value))
            if arg.startswith("DIR_"):
                value = os.path.abspath(os.path.expanduser(os.path.join(value, "pipeline")))
                os.makedirs(value, exist_ok=True)
            config[arg] = value

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
    
    
    # Step 1 - Load Input Files
    fastq = {}
    fasta = {}
    amino = {}
    print("\nLoading sequence files:")
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

    print(f"\nFastq sequences: {fastq}")
    print(f"\nFasta sequences: {fasta}")
    print(f"\nProtein Sequences: {amino}")


    # Step 2 (check quality of fastq files)
    jobs = []
    if fastq:
        print("\nSTEP 2: Checking quality of fastq files")
        for key,value in fastq.items():
            jobs.append(rayWorker.remote(cerberus_qc.checkQuality, key, value, config, f"{STEP[2]}/{key}"))


    # Step 3 (trim fastq files)
    jobTrim = []
    if fastq:
        print("\nSTEP 3: Trimming fastq files")
        for key,value in fastq.items():
            jobTrim.append(rayWorker.remote(cerberus_trim.trimReads, key, [key, value], config, f"{STEP[3]}/{key}"))

    # Waitfor Trimmed Reads
    trimmedReads = {}
    for job in jobTrim:
        key,value = ray.get(job)
        trimmedReads[key] = value

    if trimmedReads:
        print("\nChecking quality of trimmed files")
        for key,value in trimmedReads.items():
            jobs.append(rayWorker.remote(cerberus_qc.checkQuality, key, value, config, f"{STEP[3]}/{key}/quality"))


    # step 4 Decontaminate (adapter free read to clean quality read + removal of junk)
    jobDecon = []
    if trimmedReads:
        print("\nSTEP 4: Decontaminating trimmed files")
        for key,value in trimmedReads.items():
            jobDecon.append(rayWorker.remote(cerberus_decon.deconReads, key, [key, value], config, f"{STEP[4]}/{key}"))

    deconReads = {}
    for job in jobDecon:
        key,value = ray.get(job)
        deconReads[key] = value


    # step 5a for cleaning contigs
    jobContigs = [] #TODO: Add config flag for contigs/scaffolds/raw reads
    if fasta:# and "scaf" in config["FLAGS"]:
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


    # step 6 (ORF Finder)
    jobGenecall = []
    if fasta:
        print("STEP 6: ORF Finder")
        for key,value in fasta.items():
            if key.startswith("euk_"):
                jobGenecall.append(rayWorker.remote(cerberus_genecall.findORF_euk, key, value, config, f"{STEP[6]}/{key}"))
            else:
                jobGenecall.append(rayWorker.remote(cerberus_genecall.findORF_mic, key, value, config, f"{STEP[6]}/{key}"))

    # Waiting for GeneCall
    for job in jobGenecall:
        key,value = ray.get(job)
        amino[key] = value


    # step 7 (HMMER)
    print("STEP 7: HMMER Search")
    jobHMM = []
    for key,value in amino.items():
        jobHMM.append(rayWorker.remote(cerberus_hmmer.search, key, value, config, f"{STEP[7]}/{key}"))

    print("Waiting for HMMER")
    hmmFoam = {}
    for job in jobHMM:
        key,value = ray.get(job)
        hmmFoam[key] = value


    # step 8 (Parser)
    print("STEP 8: Parse HMMER results")
    jobParse = []
    for key,value in hmmFoam.items():
        jobParse.append(rayWorker.remote(cerberus_parser.parseHmmer, key, value, config, f"{STEP[8]}/{key}"))

    print("Waiting for parsed results")
    hmmRollup = {}
    hmmTables = {}
    figSunburst = {}
    figCharts = {}
    for job in jobParse:
        key,value = ray.get(job)
        hmmRollup[key] = value
        hmmTables[key] = cerberus_parser.createTables(value)
        figSunburst[key] = cerberus_visual.graphSunburst(hmmTables[key])
        figCharts[key] = cerberus_visual.graphBarcharts(value)


    # step 9 (Report)
    print("Creating Reports")
    pcaFigures = None
    if len(hmmTables) > 2:
        pcaFigures = cerberus_visual.graphPCA(hmmTables)
    
    cerberus_report.createReport(hmmTables, figSunburst, figCharts, pcaFigures, config, f"{STEP[9]}")


    # Wait for misc jobs
    print("Waiting for lingering jobs")
    ready, pending = ray.wait(jobs)
    while(pending):
        print(f"Waiting for {len(pending)} jobs.")
        ready, pending = ray.wait(pending)


    # Finished!
    print("\nFinished Pipeline")
    return 0


## Start main method
if __name__ == "__main__":
    sys.exit(main())

## End of script
