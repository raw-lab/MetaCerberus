#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""metacerberus.py: Versatile Functional Ontology Assignments for Metagenomes

Uses Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data.
"""


__version__     = "1.3.1"
__date__        = "June 2024"
__author__      = "Jose L. Figueroa III, Richard A. White III"
__copyright__   = "Copyright 2022-2024"

def warn(*args, **kwargs):
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


# our package import
from meta_cerberus import (
    metacerberus_setup,
    metacerberus_qc, metacerberus_merge, metacerberus_trim, metacerberus_decon, metacerberus_formatFasta, metacerberus_metastats,
    metacerberus_genecall, metacerberus_hmm, metacerberus_parser,
    metacerberus_prostats, metacerberus_visual, metacerberus_report, Chunker
)


##### Global Variables #####

DEBUG = False

# known file extensions
FILES_FASTQ = ['.fastq', '.fq']#, '.fastq.gz', '.fq.gz']
FILES_FASTA = [".fasta", ".fa", ".fna", ".ffn"]
FILES_AMINO = [".faa"]

# External file paths
PATHDB = pkg.resource_filename("meta_cerberus", "DB")
PATHFGS = pkg.resource_filename("meta_cerberus", "FGS")

# qc sequence default locations (for decontamination)
QC_SEQ = {
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
    'EXE_PHANOTATE' : 'phanotate.py',
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


def set_add(to_set:set, item, msg:str):
    if item not in to_set:
        to_set.add(item)
        print('\n', msg, '\n', sep='')
    return to_set

def logTime(dirout, host, funcName, path, time):
    with open(f'{dirout}/time.tsv', 'a+') as outTime:
        print(host, funcName, time, path, file=outTime, sep='\t')
    return


## Ray Worker Threads ##
@ray.remote
def rayWorkerThread(func, key, dir_log, params:list):
    '''Worker thread for Ray

    Parameters:
        func: The name of the function to call
        key (str): The key name for the value being processed
        dir_log (str): Path to the folder of the logfile
        params**: A list of parameters to send to the called function

    Returns:
        key, ret, function_name
    '''
    start = time.time()
    ret = func(*params)
    end = str(datetime.timedelta(seconds=time.time()-start))
    logTime(dir_log, socket.gethostname(), func.__name__, key, end)
    return key, ret, func.__name__


## MAIN
def main():
    ## Parse the command line
    parser = argparse.ArgumentParser(add_help=False)
    parser.set_defaults()

    # Setup options
    setup = parser.add_argument_group('''Setup arguments''')
    setup_grp = setup.add_mutually_exclusive_group(required=False)
    setup_grp.add_argument('--setup', action="store_true", help="Setup additional dependencies [False]")
    setup_grp.add_argument('--update', action="store_true", help="Update downloaded databases [False]")
    setup_grp.add_argument('--list-db', action="store_true", help="List available and downloaded databases [False]")
    setup.add_argument('--download', nargs='*', default=None, help="Downloads selected HMMs. Use the option --list-db for a list of available databases, default is to download all available databases")
    setup_grp.add_argument('--uninstall', action="store_true", help="Remove downloaded databases and FragGeneScan+ [False]")

    # At least one of these options are required
    input = parser.add_argument_group(f'''Input files
At least one sequence is required.
    accepted formats: [{', '.join(FILES_FASTQ + FILES_FASTA + FILES_AMINO)}]
Example:
> metacerberus.py --prodigal file1.fasta
> metacerberus.py --config file.config
*Note: If a sequence is given in [{', '.join(FILES_FASTQ)}] format, one of --nanopore, --illumina, or --pacbio is required.''')
    input.add_argument('-c', '--config', help = 'Path to config file, command line takes priority', is_config_file=True)
    input.add_argument('--prodigal', nargs='+', default=[], help='Prokaryote nucleotide sequence (includes microbes, bacteriophage)')
    input.add_argument('--fraggenescan', nargs='+', default=[], help='Eukaryote nucleotide sequence (includes other viruses, works all around for everything)')
    input.add_argument('--super', nargs='+', default=[], help='Run sequence in both --prodigal and --fraggenescan modes')
    input.add_argument('--prodigalgv', nargs='+', default=[], help='Giant virus nucleotide sequence')
    input.add_argument('--phanotate', nargs='+', default=[], help='Phage sequence')
    input.add_argument('--protein', '--amino', nargs='+', default=[], help='Protein Amino Acid sequence')
    input.add_argument('--hmmer-tsv', nargs='+', default=[], help='Annotations tsv file from HMMER (experimental)')
    input.add_argument('--class', type=str, default='', help='path to a tsv file which has class information for the samples. If this file is included scripts will be included to run Pathview in R')
    # Raw-read identification
    readtype = input.add_mutually_exclusive_group(required=False)
    readtype.add_argument('--illumina', action="store_true", help="Specifies that the given FASTQ files are from Illumina")
    readtype.add_argument('--nanopore', action="store_true", help="Specifies that the given FASTQ files are from Nanopore")
    readtype.add_argument('--pacbio', action="store_true", help="Specifies that the given FASTQ files are from PacBio")

    # Output options
    output = parser.add_argument_group(f'''Output options''')
    output.add_argument('--dir-out', "--dir_out", type=str, default='./results-metacerberus', help='path to output directory, defaults to "results-metacerberus" in current directory. [./results-metacerberus]')
    output.add_argument('--replace', action="store_true", help="Flag to replace existing files. [False]")
    output.add_argument('--keep', action="store_true", help="Flag to keep temporary files. [False]")
    output.add_argument('--tmpdir', type=str, default="", help='temp directory for RAY (experimental) [system tmp dir]')

    # Database options
    database = parser.add_argument_group(f'''Database options''')
    database.add_argument('--hmm', nargs='+', default=['KOFam_all'], help="A list of databases for HMMER. 'ALL' uses all downloaded databases. Use the option --list-db for a list of available databases [KOFam_all]")
    database.add_argument("--db-path", type=str, default=PATHDB, help="Path to folder of databases [Default: under the library path of MetaCerberus]")

    # optional flags
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--meta', action="store_true", help="Metagenomic nucleotide sequences (for prodigal) [False]")
    optional.add_argument('--scaffolds', action="store_true", help="Sequences are treated as scaffolds [False]")
    optional.add_argument('--minscore', type=float, default=60, help="Score cutoff for parsing HMMER results [60]")
    optional.add_argument('--evalue', type=float, default=1e-09, help="E-value cutoff for parsing HMMER results [1e-09]")
    optional.add_argument('--remove-n-repeats', action="store_true", help="Remove N repeats, splitting contigs [False]")
    optional.add_argument('--skip-decon', action="store_true", help="Skip decontamination step [False]")
    optional.add_argument('--skip-pca', action="store_true", help="Skip PCA [False]")
    optional.add_argument('--cpus', type=int, help="Number of CPUs to use per task. System will try to detect available CPUs if not specified [Auto Detect]")
    optional.add_argument('--chunker', type=int, default=0, help="Split files into smaller chunks, in Megabytes [Disabled by default]")
    optional.add_argument('--grouped', action="store_true", help="Group multiple fasta files into a single file before processing. When used with chunker can improve speed")
    optional.add_argument('--slurm-nodes', type=str, default="", help=argparse.SUPPRESS)# help='list of node hostnames from SLURM, i.e. $SLURM_JOB_NODELIST.')
    optional.add_argument('--slurm-single', action="store_true", help=argparse.SUPPRESS)# help='Force single node use, do not connect to host')
    optional.add_argument('--version', '-v', action='version',
                        version=f'MetaCerberus: \n version: {__version__} {__date__}',
                        help='show the version number and exit')
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
    # Hidden from help, expected to load from config file
    dependencies = parser.add_argument_group()
    for key in DEPENDENCIES:
        dependencies.add_argument(f"--{key}", help=argparse.SUPPRESS)
    dependencies.add_argument('--adapters', type=str, default=QC_SEQ['adapters'], help="FASTA File containing adapter sequences for trimming")
    dependencies.add_argument('--qc_seq', type=str, default="default", help="FASTA File containing control sequences for decontamination")

    args = parser.parse_args()

    if args.uninstall:
        metacerberus_setup.remove(args.db_path, PATHFGS)
        return 0
    if args.list_db:
        downloaded,to_download,urls,hmm_version = metacerberus_setup.list_db(args.db_path)
        if downloaded:
            print("HMM Databases already downloaded:")
            for name,filelist in downloaded.items():
                print(name, hmm_version[name], sep='\t')
                #for filepath in filelist:
                #    print('', filepath, sep='\t')
        else:
            print("No HMM databases are currently downloaded at:", args.db_path)
        if to_download:
            print("Available HMM databases to download:")
            for name,filelist in to_download.items():
                print(name, hmm_version[name], sep='\t')
                #for filepath in filelist:
                #    print('', filepath, sep='\t')
        else:
            print("All available HMM databases already downloaded at:", args.db_path)
        return 0
    if args.setup:
        print("Setting up FragGeneScanRS")
        metacerberus_setup.FGS(PATHFGS)
        return 0
    if args.download is not None:
        metacerberus_setup.download(args.db_path, args.download)
        return 0
    if args.update:
        metacerberus_setup.update(args.db_path)
        return 0

    # HMM Databases
    DB_HMM = dict()
    if Path(PATHDB, "databases.tsv").exists():
        with Path(PATHDB, "databases.tsv").open() as reader:
            header = reader.readline().split()
            for line in reader:
                name,filename,urlpath,date = line.split()
                if ".hmm" in Path(filename).suffixes:
                    if name == "KOFam":
                        name = Path(filename).with_suffix('').stem
                        if name == "KOFam_all" and "ALL" in args.hmm:
                            args.hmm += [name]
                    elif "ALL" in args.hmm:
                        args.hmm += [name]
                    elif "all" in args.hmm:
                        args.hmm += [name]
                    elif "All" in args.hmm:
                        args.hmm += [name]
                    DB_HMM[name] = Path(args.db_path, filename)

    dbHMM = dict()
    for hmm in [x.strip(',') for x in set(args.hmm)]:
        if hmm in DB_HMM:
            if DB_HMM[hmm].exists():
                if Path(DB_HMM[hmm]).name.startswith("KOFam"):
                    dbHMM[f"{hmm}_KEGG"] = DB_HMM[hmm]
                    dbHMM[f"{hmm}_FOAM"] = DB_HMM[hmm]
                else:
                    dbHMM[hmm] = DB_HMM[hmm]
            else:
                print(f"ERROR: Cannot use '{hmm}', please download it using 'metacerberus.py --download")
        else:
            dbpath = Path(hmm)
            while Path(hmm).suffixes:
                hmm = Path(hmm).with_suffix('')
            if dbpath.exists() and hmm.with_suffix('.tsv').exists():
                dbname = Path(dbpath).with_suffix('').stem
                dbHMM[dbname] = dbpath
                print("Loading custom HMM:", dbname, dbpath)
            else:
                print("Unable to load custom database")
    if not len(dbHMM):
        print("ERROR: No HMM DB Loaded")
        return 1

    print(f"\nStarting MetaCerberus v{__version__} Pipeline\n")
    print("Using HMMs:")
    for k,v in dbHMM.items():
        print(k,v)

    # Merge related arguments
    if args.super:
        args.prodigal += args.super
        args.fraggenescan += args.super

    # Check if required flags are set
    if not any([args.prodigal, args.fraggenescan, args.prodigalgv, args.phanotate, args.protein, args.hmmer_tsv]):
        parser.error('At least one sequence must be declared either in the command line or through the config file')
    if args.chunker < 0:
        args.chunker = 0
    if args.grouped and args.chunker == 0:
        args.chunker = 1

    # Initialize Config Dictionary
    config = {}
    config['STEP'] = STEP
    config['PATHDB'] = PATHDB

    # Get FGS+ Folder from Library Path
    config['EXE_FGS'] = os.path.join(PATHFGS, DEPENDENCIES["EXE_FGS"])

    # load all args into config
    for arg,value in args.__dict__.items():
        if value is not None:
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
                if not os.path.isfile(path):
                    print(f"{value:20} WARNING: '{value}' not found")
                    config[key] = None
            else:
                print(f"{value:20} NOT FOUND, must be defined in config file as {key}:<path>")
                config[key] = None
        except:
            print(f"ERROR executing 'which {value}'")

    # Check for dependencies
    #TODO: don't quit on all dependencies, not all paths required
    #for key,value in config.items():
    #    if key.startswith("EXE_") and not os.path.isfile(value):
    #        parser.error(f"Unable to find file: {value}")


    # Initialize RAY for Multithreading
    print("Initializing RAY")

    # First try if ray is setup for a cluster
    #TODO: Fix this, does not set up slurm script
    #if config['SLURM_NODES']:
    #    metacerberus_setup.slurm(config['SLURM_NODES'])
    
    # Get CPU Count
    if 'CPUS' not in config:
        config['CPUS'] = psutil.cpu_count()

    if args.slurm_single:
        # Force single node
        try:
            ray.init(address="local", num_cpus=config['CPUS'], log_to_driver=DEBUG)
            print("Started RAY single node")
        except:
            print("Failed to initizlize Ray with --slurm_single")
            return 0
    else:
        try:
            ray.init(address='auto', log_to_driver=DEBUG)
        except:
            try:
                ray.init(num_cpus=config['CPUS'], log_to_driver=DEBUG)
            except:
                print("Failed to initialize ray")
                return 0
    config['CLUSTER'] = False
    if len(ray.nodes()) > 1:
        config['CLUSTER'] = True
    print(f"Running RAY on {len(ray.nodes())} node(s)")
    print(f"Using {config['CPUS']} CPUs per node")
    temp_dir = Path(ray.nodes()[0]['ObjectStoreSocketName']).parent.parent
    print("Ray temporary directory:", temp_dir)


    startTime = time.time()
    # Step 1 - Load Input Files
    print("\nSTEP 1: Loading sequence files:")
    # Check installed libraries for pyrodigal, pyrodigal-gv
    #required = {'mutagen', 'gTTS'}
    #installed = {pkg.key for pkg in pkg_resources.working_set}
    #missing = required - installed
    fastq = {}
    fasta = {}
    amino = {}
    rollup = {}
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
    # Load prodigal-gv input
    for item in args.prodigalgv:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_FASTQ:
                fastq['prodigalgv_'+name] = item
            elif ext in FILES_FASTA:
                fasta['prodigalgv_'+name] = item
            elif ext in FILES_AMINO:
                print(f"WARNING: Ignoring protein sequence '{item}', please use --protein option for these.")
        elif os.path.isdir(item):
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1]
                if ext in FILES_FASTQ + FILES_FASTA:
                    args.prodigalgv.append(os.path.join(item, file))
        else:
            print(f'{item} is not a valid sequence')
    # Load Prodigal input
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
    if not config['EXE_FGS'] and args.fgs:
        #TODO: setup FGS automatically instead
        print("WARNING: FragGeneScanRS is not installed, skipping files set to use FGS")
        args.fraggenescan = list()
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
    # Load Phanotate input
    if not config['EXE_PHANOTATE'] and args.phanotate:
        print("WARNING: Phanotate is not installed, skipping files set to use Phanotate")
        args.phanotate = list()
    for item in args.phanotate:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in FILES_FASTQ:
                fastq['phanotate_'+name] = item
            elif ext in FILES_FASTA:
                fasta['phanotate_'+name] = item
            elif ext in FILES_AMINO:
                print(f"WARNING: Ignoring protein sequence '{item}', please use --protein option for these.")
        elif os.path.isdir(item):
            for file in os.listdir(item):
                ext = os.path.splitext(file)[1]
                if ext in FILES_FASTQ + FILES_FASTA:
                    args.phanotate.append(os.path.join(item, file))
        else:
            print(f'{item} is not a valid sequence')
    # Load HMMER input
    for item in args.hmmer_tsv:
        item = os.path.abspath(os.path.expanduser(item))
        if os.path.isfile(item):
            name, ext = os.path.splitext(os.path.basename(item))
            if ext in ['.tsv']:
                rollup['rollup_'+name] = item
        else:
            print(f'{item} is not a valid sequence')
    
    print(f"Processing {len(fastq)} fastq sequences")
    print(f"Processing {len(fasta)} fasta sequences")
    print(f"Processing {len(amino)} protein sequences")
    print(f"Processing {len(rollup)} rollup files")

    if len(fastq) > 0:
        config['META'] = True
        if not any([args.illumina, args.nanopore, args.pacbio]):
            parser.error('A FASTQ file was given, but no flag specified as to the type.\nPlease use one of --illumina, --nanopore, or --pacbio')
        else:
            if args.illumina:
                config['QC_SEQ'] = QC_SEQ["illumina"]
            if args.nanopore:
                config['QC_SEQ'] = QC_SEQ["lambda"]
            if args.pacbio:
                config['QC_SEQ'] = QC_SEQ["pacbio"]

    # Main Pipeline
    pipeline = list()
    step_curr = set()
    
    # Entry Point: Fastq
    if fastq:
        # Step 2 (check quality of fastq files)
        #print("\nSTEP 2: Checking quality of fastq files")
        #for key,value in fastq.items():
        #    pipeline.append(rayWorkerThread.remote(metacerberus_qc.checkQuality, key, config['DIR_OUT'], [value, config, f"{STEP[2]}/{key}"]))
        print("\nSTEP 3: Trimming fastq files")
        # Merge Paired End Reads
        fastqPaired = dict()
        for ext in FILES_FASTQ:
            fastqPaired.update( {k:v for k,v in fastq.items() if "R1"+ext in v and v.replace("R1"+ext, "R2"+ext) in fastq.values() } )
        if len(fastqPaired) > 0 and not config['EXE_FLASH']:
            parser.error('ERROR: FLASH is required for merging paired end FASTQ files.\nPlease install FLASH and edit the PATH variable or set the path in a config file')
        for key,value in fastqPaired.items():
            reverse = fastq.pop(key.replace("R1", "R2"))
            forward = fastq.pop(key)
            key = key.removesuffix("R1").rstrip('-_')
            #TODO: quick fix, make parallel
            if not config['EXE_FASTP']:
                print("WARNING: Skipping paired end trimming, FASTP not found")
                r1 = value
                r2 = reverse
            else:
                r1,r2 = metacerberus_trim.trimPairedRead([key, [value,reverse]], config, Path(STEP[3], key))
            value = metacerberus_merge.mergePairedEnd([r1,r2], config, f"{STEP[3]}/{key}/merged")
            pipeline += [ray.put([key, value, 'trimSingleRead'])]
        del fastqPaired # memory cleanup
        # Trim
        if config['NANOPORE'] and not config['EXE_PORECHOP']:
            print("WARNING: Skipping Nanopore trimming, PORECHOP not found")
            for key,value in fastq.items():
                pipeline += [ray.put([key, value, "trimSingleRead"])]
        elif not config['EXE_FASTP']:
            print("WARNING: Skipping single-end trimming, FASTP not found")
            for key,value in fastq.items():
                pipeline += [ray.put([key, value, "trimSingleRead"])]
        else:
            for key,value in fastq.items():
                pipeline += [rayWorkerThread.remote(metacerberus_trim.trimSingleRead, key, config['DIR_OUT'], [[key, value], config, Path(STEP[3], key)])]

    # Step 5 Contig Entry Point
    # Only do this if a fasta file was given, not if fastq
    if fasta:# and "scaffold" in config:
        if config['REMOVE_N_REPEATS']:
            print("\nSTEP 5a: Removing N's from contig files")
            for key,value in fasta.items():
                pipeline.append(rayWorkerThread.remote(metacerberus_formatFasta.removeN, key, config['DIR_OUT'], [value, config, Path(STEP[5], key)]))
        else:
            for key,value in fasta.items():
                pipeline += [ray.put([key, value, "reformat"])]


    # Step 8 Protein Entry Point
    jobsORF = 0
    if amino:
        set_add(step_curr, 8, "STEP 8: HMMER Search")
        for key,value in amino.items():
            pipeline += [ray.put([key, value, 'findORF_'])]
            jobsORF += 1

    # Step 9 Rollup Entry Point
    hmm_tsv = dict()
    hmm_tsvs = dict()
    if rollup:
        set_add(step_curr, 8.5, "STEP 8: Filtering rollup file(s)")
        for key,value in rollup.items():
            amino[key] = None
            for hmm in dbHMM:
                tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, "filtered.tsv")
                pipeline.append(rayWorkerThread.remote(metacerberus_hmm.filterHMM, f"{hmm}/{key}", config['DIR_OUT'], [value, tsv_filtered, dbHMM[hmm]]))

    NStats = dict()
    readStats = dict()
    report_path = os.path.join(config['DIR_OUT'], STEP[10])
    final_path = Path(config['DIR_OUT'], "final")

    groupIndex = dict()
    amino_queue = dict()
    dictChunks = dict()
    countFiltered = dict()
    hmmRollup = {}
    hmmCounts = {}
    if config['CLUSTER']:
        jobs_per_node = 4/config['CPUS']
    else:
        jobs_per_node = 4
    while pipeline:
        ready,pipeline = ray.wait(pipeline, timeout=1)
        if not ready:
            continue
        key,value,func = ray.get(ready[0])

        if func == "checkQuality":
            if value:
                name = key
                key = key.rstrip('_decon').rstrip('_trim')
                #os.makedirs(os.path.join(report_path, key), exist_ok=True)
                #shutil.copy(value, os.path.join(report_path, key, f"qc_{name}.html"))
        if func == "trimSingleRead":
            # Wait for Trimmed Reads
            fastq[key] = value
            pipeline.append(rayWorkerThread.remote(metacerberus_qc.checkQuality, key+'_trim', config['DIR_OUT'], [value, config, f"{STEP[3]}/{key}/quality"]))
            if fastq and config['ILLUMINA']:
                if config['SKIP_DECON'] or not config['EXE_BBDUK']:
                    if not config['EXE_BBDUK']:
                        set_add(step_curr, "decon", "WARNING: Skipping decontamination, BBDUK not found")
                    set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
                    pipeline.append(rayWorkerThread.remote(metacerberus_formatFasta.reformat, key, config['DIR_OUT'], [value, config, f"{STEP[5]}/{key}"]))
                else:
                    set_add(step_curr, 4, "STEP 4: Decontaminating trimmed files")
                    pipeline.append(rayWorkerThread.remote(metacerberus_decon.deconSingleReads, key, config['DIR_OUT'], [[key, value], config, f"{STEP[4]}/{key}"]))
            else:
                set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
                pipeline.append(rayWorkerThread.remote(metacerberus_formatFasta.reformat, key, config['DIR_OUT'], [value, config, f"{STEP[5]}/{key}"]))
        if func.startswith("decon"):
            fastq[key] = value
            set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
            pipeline.append(rayWorkerThread.remote(metacerberus_qc.checkQuality, key+'_decon', config['DIR_OUT'], [value, config, f"{STEP[4]}/{key}/quality"]))
            pipeline.append(rayWorkerThread.remote(metacerberus_formatFasta.reformat, key, config['DIR_OUT'], [value, config, f"{STEP[5]}/{key}"]))
        if func == "removeN" or func == "reformat":
            if func == "removeN":
                fasta[key] = value[0]
                if value[1]:
                    NStats[key] = value[1]
                set_add(step_curr, 6, "STEP 6: Metaome Stats")
                readStats[key] = metacerberus_metastats.getReadStats(value[0], config, os.path.join(STEP[6], key))
            elif func == "reformat":
                fasta[key] = value
            set_add(step_curr, 7, "STEP 7: ORF Finder")
            if key.startswith("FragGeneScan_"):
                pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_fgs, key, config['DIR_OUT'], [fasta[key], config, f"{STEP[7]}/{key}"]))
            elif key.startswith("prodigalgv_"):
                pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_prod, key, config['DIR_OUT'], [fasta[key], config, f"{STEP[7]}/{key}", config['META'], True]))
            elif key.startswith("prodigal_"):
                pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_prod, key, config['DIR_OUT'], [fasta[key], config, f"{STEP[7]}/{key}", config['META']]))
            elif key.startswith("phanotate_"):
                pipeline.append(rayWorkerThread.remote(metacerberus_genecall.findORF_phanotate, key, config['DIR_OUT'], [fasta[key], config, f"{STEP[7]}/{key}", config['META']]))
            jobsORF += 1
        if func.startswith("findORF_"):
            if not value:
                continue
            if Path(value).stat().st_size == 0:
                # fail if amino file is empty
                print("WARNING: no ORFs found in:", key, value)
                continue
            #TODO: Check for duplicate headers in amino acids
            # This causes an issue with the GFF and summary files
            if config['GROUPED']:
                amino[key] = value
                jobsORF -= 1
                if not Path(config['DIR_OUT'], 'grouped').exists():
                    Path(config['DIR_OUT'], 'grouped').mkdir(parents=True, exist_ok=True)
                outfile = Path(config['DIR_OUT'], 'grouped', 'grouped.faa')
                Path(config['DIR_OUT'], STEP[8], key).mkdir(parents=True, exist_ok=True)
                with outfile.open('a') as writer, Path(value).open() as reader:
                    for line in reader:
                        writer.write(line)
                        if line.startswith('>'):
                            name = line[1:].rstrip().split()[0]
                            if name in groupIndex:
                                print("WARN: Duplicate header:", name)
                            groupIndex[name] = key
                if jobsORF > 0:
                    continue #Continue until all ORFs are done
                value = outfile
                key = "grouped"
            set_add(step_curr, 8, "STEP 8: HMMER Search")
            amino[key] = value
            if config['CHUNKER'] > 0:
                chunks = Chunker.Chunker(amino[key], os.path.join(config['DIR_OUT'], 'chunks', key), f"{config['CHUNKER']}M", '>')
                for hmm in dbHMM.items():
                    chunkCount = 1
                    for chunk in chunks.files:
                        key_chunk = f'chunk-{hmm[0]}-{chunkCount}-{len(chunks.files)}_{key}'
                        key_name = f'chunk-{chunkCount}-{len(chunks.files)}_{key}'
                        chunkCount += 1
                        pipeline.append(rayWorkerThread.options(num_cpus=jobs_per_node).remote(metacerberus_hmm.searchHMM, [key_chunk], config['DIR_OUT'],
                                                                                [{key_name:chunk}, config, Path(STEP[8], key), hmm, 4]))
            else:
                outfile = Path(config['DIR_OUT'], STEP[8], key, f'{key}.tsv')
                if config['REPLACE'] or not outfile.exists(): #TODO: Possible bug, will always be true
                    for hmm in dbHMM.items():
                        hmm_key = f"{hmm[0]}/{key}"
                        pipeline.append(rayWorkerThread.options(num_cpus=jobs_per_node).remote(metacerberus_hmm.searchHMM, [hmm_key], config['DIR_OUT'],
                                                                [{key:value}, config, Path(STEP[8]), hmm, 4]))
                else:
                    #TODO: distinguish filtered tsv per hmm
                    tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, "filtered.tsv")
                    set_add(step_curr, 8.1, "STEP 8: Filtering HMMER results")
                    pipeline.append(rayWorkerThread.remote(metacerberus_hmm.filterHMM, key, config['DIR_OUT'], [tsv_out, tsv_filtered, dbHMM[hmm]]))
        if func.startswith('searchHMM'):
            keys = key
            for key,tsv_file in zip(keys,value):
                match = re.search(r"^chunk-([A-Za-z_]+)-(\d+)-(\d+)_(.+)", key)
                if match: # Matches if the keys are part of chunks
                    hmm,i,l,key = match.groups()
                    hmm_key = f"{hmm}-{key}"
                    if hmm_key not in dictChunks:
                        dictChunks[hmm_key] = list()
                    dictChunks[hmm_key].append(tsv_file)
                    if len(dictChunks[hmm_key]) == int(l):
                        # All chunks of a file have returned
                        if config['GROUPED']:
                            key_set = set()
                            for item in sorted(dictChunks[hmm_key]):
                                with open(item) as reader:
                                    for line in reader:
                                        name = line.split()[0]
                                        k = groupIndex[name]
                                        key_set.add(k)
                                        tsv_out = Path(config['DIR_OUT'], STEP[8], k, f"{hmm}-{k}.tsv")
                                        with tsv_out.open('a') as writer:
                                            writer.write(line)
                                dictChunks[hmm_key].remove(item)
                                if not config['KEEP']:
                                    os.remove(item)
                            set_add(step_curr, 8.1, "STEP 8: Filtering HMMER results")
                            for k in key_set:
                                tsv_out = Path(config['DIR_OUT'], STEP[8], k, f"{hmm}-{k}.tsv")
                                tsv_filtered = Path(config['DIR_OUT'], STEP[8], k, f"filtered-{hmm}.tsv")
                                pipeline.append(rayWorkerThread.remote(metacerberus_hmm.filterHMM, f"{hmm}/{k}", config['DIR_OUT'], [tsv_out, tsv_filtered, dbHMM[hmm]]))
                            # FINISH SPLITTING GROUP
                            continue
                        # Not grouped
                        tsv_out = Path(config['DIR_OUT'], STEP[8], key, f"{hmm}-{key}.tsv")
                        tsv_out.parent.mkdir(parents=True, exist_ok=True)
                        with tsv_out.open('w') as writer:
                            for item in sorted(dictChunks[hmm_key]):
                                writer.write(open(item).read())
                                dictChunks[hmm_key].remove(item)
                                if not config['KEEP']:
                                    os.remove(item)
                        tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, f"filtered-{hmm}.tsv")
                        set_add(step_curr, 8.1, "STEP 8: Filtering HMMER results")
                        pipeline.append(rayWorkerThread.remote(metacerberus_hmm.filterHMM, f"{hmm}/{key}", config['DIR_OUT'], [tsv_out, tsv_filtered, dbHMM[hmm]]))
                else:
                # Not chunked file
                    hmm,key = key.split(sep='/', maxsplit=1)
                    tsv_out = Path(config['DIR_OUT'], STEP[8], key, f"{hmm}-{key}.tsv")
                    with tsv_out.open('w') as writer:
                        writer.write(open(tsv_file).read())
                    if not config['KEEP']:
                            os.remove(tsv_file)
                    set_add(step_curr, 8.1, "STEP 8: Filtering HMMER results")
                    tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, f"filtered-{hmm}.tsv")
                    pipeline.append(rayWorkerThread.remote(metacerberus_hmm.filterHMM, f"{hmm}/{key}", config['DIR_OUT'], [tsv_out, tsv_filtered, dbHMM[hmm]]))
        if func.startswith('filterHMM'):
            hmm,key = key.split('/')
            set_add(step_curr, 9, "STEP 9: Parse HMMER results")
            pipeline.append(rayWorkerThread.remote(metacerberus_parser.parseHmmer, key, config['DIR_OUT'], [value, config, f"{STEP[9]}/{key}", hmm, dbHMM[hmm]]))
            
            tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, "filtered.tsv")
            if key not in hmm_tsvs:
                hmm_tsvs[key] = dict()
                with tsv_filtered.open('w') as writer:
                    print("target", "query", "e-value", "score", "length", "start", "end", "hmmDB", sep='\t', file=writer)
            if hmm not in hmm_tsvs[key]:
                hmm_tsvs[key][hmm] = value
            with tsv_filtered.open('a') as writer, open(value) as reader:
                reader.readline() # Skip header
                for line in reader:
                    print(*line.rstrip('\n').split('\t'), hmm, sep='\t', file=writer)
            if len(hmm_tsvs[key]) == len(dbHMM):
                # old method
                hmm_tsv[key] = tsv_filtered
                outfile = Path(config['DIR_OUT'], STEP[9], key, f"top_5-{key}.tsv")
                pipeline.append(rayWorkerThread.remote(metacerberus_parser.top5, key, config['DIR_OUT'],
                                                       [tsv_filtered, outfile]))
                # new method
                outfile = Path(config['DIR_OUT'], STEP[9], key, "HMMER_top_5.tsv")
                pipeline.append(rayWorkerThread.remote(metacerberus_parser.top5s, key, config['DIR_OUT'],
                                                       [hmm_tsvs[key], outfile]))
        if func.startswith('parseHmmer'):
            if key not in hmmRollup:
                hmmRollup[key] = dict()
            hmmRollup[key].update(value)
            pipeline.append(rayWorkerThread.remote(metacerberus_parser.createCountTables, key, config['DIR_OUT'], [value, config, f"{STEP[9]}/{key}"]))
        if func.startswith('createCountTables'):
            if key not in hmmCounts:
                hmmCounts[key] = dict()
            hmmCounts[key].update(value)

    # End main pipeline

    # Log time of main pipeline
    time_pipeline = str(datetime.timedelta(seconds=time.time()-startTime))
    logTime(config["DIR_OUT"], socket.gethostname(), "Pipeline_time", config["DIR_OUT"], time_pipeline)

    # step 10 (Report)
    print("\nSTEP 10: Creating Reports")

    ## Copy report files from QC, Parser
    #for key in hmmRollup.keys():
    #    Path(report_path, key).mkdir(0o777, True, True)
    #    src = os.path.join(config['DIR_OUT'], config['STEP'][9], key, "HMMER_top_5.tsv")
    #    dst = os.path.join(report_path, key)
    #    shutil.copy(src, dst)

    # Write Stats
    Path(final_path, "fasta").mkdir(0o777, True, True)
    print("Creating final reports and statistics")
    protStats = {}
    for key in hmm_tsvs.keys():
        # Copy report files from QC, Parser
        Path(report_path, key).mkdir(0o777, True, True)
        Path(final_path, key).mkdir(0o777, True, True)
        src = os.path.join(config['DIR_OUT'], config['STEP'][9], key, "HMMER_top_5.tsv")
        dst = Path(final_path, key)
        shutil.copy(src, dst)
        # Protein statistics & annotation summary
        summary_tsv = Path(final_path, key, 'final_annotation_summary.tsv')
        protStats[key] = metacerberus_prostats.getStats(amino[key], hmm_tsvs[key], hmmCounts[key], config, dbHMM, summary_tsv, Path(final_path, "fasta", f"{key}.faa"))
        try:
            src = Path(amino[key]).with_suffix(".ffn")
            dst = Path(final_path, "fasta", f"{key}.ffn")
            shutil.copy(src, dst)
        except: pass
        try:
            src = Path(fasta[key])
            dst = Path(final_path, "fasta", f"{key}.fna")
            shutil.copy(src, dst)
        except: pass
        # Create GFFs #TODO: Incorporate this into getStats (or separate all summary into new module)
        gff = [x for x in Path(config['DIR_OUT'], STEP[7], key).glob("*.gff")]
        Path(final_path, "gff").mkdir(511, True, True)
        if len(gff) == 1:
            out_gff = Path(final_path, "gff", f"{key}.gff")
            out_genbank = Path(final_path, f"{key}_template.gbk")
            metacerberus_report.write_datafiles(gff[0], fasta[key], amino[key], summary_tsv, out_gff, out_genbank)
        else:
            out_gff = Path(final_path, "gff", f"{key}.gff")
            with out_gff.open('w') as writer:
                with summary_tsv.open() as read_summary:
                    read_summary.readline()
                    print("##gff-version  3", file=writer)
                    for summ in read_summary:
                        summ = summ.split('\t')
                        data = [summ[0].split('_')[0], ".", ".", ".", ".", ".", ".", ".", ]
                        attributes = ';'.join([f"ID={summ[0]}", f"Name={summ[1]}", f"Alias={summ[2]}", f"Dbxref={summ[3]}", f"evalue={summ[4]}", f"product_start={summ[8]}", f"product_end={summ[9]}", f"product_length={summ[10]}"])
                        print(*data, attributes, sep='\t', file=writer)
                try:
                    with open(fasta[key]) as read_fasta:
                        print("##FASTA", file=writer)
                        for line in read_fasta:
                            writer.write(line)
                except: pass
    metacerberus_report.write_Stats(report_path, readStats, protStats, NStats, config)
    del protStats

    # Write Roll-up Tables
    print("Creating Rollup Tables")
    for sample,tables in hmmCounts.items():
        os.makedirs(f"{report_path}/{sample}", exist_ok=True)
        for name,table in tables.items():
            metacerberus_report.writeTables(table, f"{report_path}/{sample}/{name}")
    for sample,tables in hmmRollup.items():
        os.makedirs(f"{report_path}/{sample}", exist_ok=True)
        for name,table in tables.items():
            shutil.copy(table, Path(final_path, sample, f'rollup_{name}.tsv'))

    # Counts Tables
    print("Mergeing Count Tables")
    dfCounts = dict()
    for dbname,dbpath in dbHMM.items():
        tsv_list = dict()
        for name in hmm_tsv.keys():
            if dbname.startswith("KOFam"):
                dbLookup = re.search(r"KOFam_.*_([A-Z]+)", dbname).group(1)
                dbLookup = dbpath.with_name(f'{dbLookup}.tsv')
            table_path = Path(config['DIR_OUT'], STEP[9], name, f'counts_{dbname}.tsv')
            if table_path.exists():
                name = re.sub(rf'^FragGeneScan_|prodigal_|Protein_', '', name)
                tsv_list[name] = table_path
        combined_path = Path(config['DIR_OUT'], STEP[10], 'combined', f'counts_{dbname}.tsv')
        metacerberus_parser.merge_tsv(tsv_list, Path(combined_path))
        if combined_path.exists():
            dfCounts[dbname] = combined_path
        del(combined_path)

    # PCA output (HTML)
    pcaFigures = None
    if config['SKIP_PCA']:
        pass
    elif len(hmm_tsv) < 4:
        print("NOTE: PCA Tables created only when there are at least four sequence files.\n")
    else:
        print("PCA Analysis")
        pcaFigures = metacerberus_visual.graphPCA(dfCounts)
        Path(report_path, 'combined').mkdir(parents=True, exist_ok=True)
        metacerberus_report.write_PCA(os.path.join(report_path, "combined"), pcaFigures)

    # Run post processing analysis in R
    if not [True for x in dfCounts if x.startswith("KOFam")]:
        print("NOTE: Pathview created only when KOFams are used since it uses KOs for its analysis.\n")
    elif len(hmm_tsv) < 4 or not config['CLASS']:
        print("NOTE: Pathview created only when there are at least four sequence files, and a class tsv file is specified with --class specifying the class for each input file.\n")
    else:
        print("\nSTEP 11: Post Analysis with GAGE and Pathview")
        outpathview = Path(report_path, 'pathview')
        outpathview.mkdir(exist_ok=True, parents=True)
        rscript = Path(outpathview, 'run_pathview.sh')

        # Check for internet
        try:
            #attempt to connect to Google
            request.urlopen('http://216.58.195.142', timeout=1)
            is_internet = True
        except:
            is_internet = False
        
        with rscript.open('w') as writer:
            writer.write(f"#!/bin/bash\n\n")
            for name,countpath in dfCounts.items():
                if not name.startswith("KOFam"):
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

    # Figure outputs (HTML)
    print("Creating combined sunburst and bargraphs")
    figSunburst = {}
    for key,value in hmmCounts.items():
        figSunburst[key] = metacerberus_visual.graphSunburst(value)

    #@ray.remote
    #def graphCharts(key, rollup, counts):
    #    return key, metacerberus_visual.graphBarcharts(rollup, counts)
    
    jobCharts = []
    for key,value in hmmRollup.items():
        #jobCharts.append( graphCharts.remote(key, value, hmmCounts[key]) )
        jobCharts.append( rayWorkerThread.remote(metacerberus_visual.graphBarcharts, key, config['DIR_OUT'], [value, hmmCounts[key]]) )
    
    figCharts = {}
    while(jobCharts):
        ready,jobCharts = ray.wait(jobCharts)
        if ready:
            key,value,_ = ray.get(ready[0])
            figCharts[key] = value

    metacerberus_report.createReport(figSunburst, figCharts, config, STEP[10])

    # Finished!
    print("\nFinished Pipeline")
    end = str(datetime.timedelta(seconds=time.time()-startTime))
    logTime(config["DIR_OUT"], socket.gethostname(), "Total_Time", config["DIR_OUT"], end)

    # Cleaning up
    temp_dir = Path(ray.nodes()[0]['ObjectStoreSocketName']).parent.parent
    print("Cleaning up Ray temporary directory", temp_dir)
    ray.shutdown()
    shutil.rmtree(temp_dir)

    return 0


## Start main method
if __name__ == "__main__":
    sys.exit(main())

## End of script
