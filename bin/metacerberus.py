#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""metacerberus.py: Versatile Functional Ontology Assignments for Metagenomes

Uses Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data.
"""


__version__     = "1.4.1"
__date__        = "February 2025"
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
import shutil
import subprocess
import configargparse as argparse #replace argparse with: https://pypi.org/project/ConfigArgParse/
import pkg_resources as pkg #to import package data files
import time
import datetime
from urllib import request
import socket
import hydraMPP as hydra

# our package import
from meta_cerberus import (
    metacerberus_setup,
    metacerberus_qc, metacerberus_merge, metacerberus_trim, metacerberus_decon, metacerberus_formatFasta, metacerberus_metastats,
    metacerberus_genecall, metacerberus_hmm, metacerberus_parser,
    metacerberus_prostats, metacerberus_visual, metacerberus_report, Chunker,
    metacerberus_pipeline
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

def logTime(dirout, host, funcName, path, timed):
    now = time.localtime()
    now = f"{now[3]:2}:{now[4]:2}:{now[5]:2}"
    with open(f'{dirout}/time.tsv', 'a+') as outTime:
        print(host, now, timed, funcName, path, file=outTime, sep='\t')
    return


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
    input.add_argument('--phanotate', nargs='+', default=[], help='Phage sequence (EXPERIMENTAL)')
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
    #output.add_argument('--tmpdir', type=str, default="", help='temp directory for HydraMPP (experimental) [Hydra default]')

    # Database options
    database = parser.add_argument_group(f'''Database options''')
    database.add_argument('--hmm', nargs='+', default=['KOFam_all'], help="A list of databases for HMMER. 'ALL' uses all downloaded databases. Use the option --list-db for a list of available databases [KOFam_all]")
    database.add_argument("--db-path", type=str, default=metacerberus_hmm.PATHDB, help="Path to folder of databases [Default: under the library path of MetaCerberus]")

    # MPP options
    network = parser.add_argument_group("MPP options")
    network.add_argument('--address', default='local', help="Address for MPP. local=no networking, host=make this machine a host, ip-address=connect to remote host [local]")
    network.add_argument('--port', type=int, default=24515, help="The port to listen/connect to [24515]")

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

    dbHMM = metacerberus_hmm.loadHMMs(args.db_path, args.hmm)
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

    # Get FGS+ Path from Library Path
    config['EXE_FGS'] = os.path.join(PATHFGS, DEPENDENCIES["EXE_FGS"])
    if args.fraggenescan and not Path(config['EXE_FGS']).exists():
        print("Setting up FragGeneScanRS")
        metacerberus_setup.FGS(PATHFGS)

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
            proc = subprocess.run(["which", value], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            path = proc.stdout.strip()
            if proc.returncode == 0:
                print(f"{value:20} {path}")
                config[key] = path
                if not os.path.isfile(path):
                    print(f"{value:20} WARNING: '{value}' @ '{path} not found")
                    config[key] = None
            else:
                print(f"{value:20} NOT FOUND, must be defined in config file as {key}:<path>")
                config[key] = None
        except:
            print(f"ERROR executing 'which {value}'")


    # Initialize HydraMPP for Distributed MPP
    print("Initializing HydraMPP")
    try:
        hydra.init(address=args.address, port=args.port, num_cpus=args.cpus, log_to_driver=DEBUG)
    except Exception as e:
        print("Failed to initialize HydraMPP")
        print(e)
        return 1
    
    print(f"\nRunning HydraMPP on {len(hydra.nodes())} node{'s' if len(hydra.nodes())>1 else ''}")
    for node in hydra.nodes():
        print(f"\tNode: '{node['hostname']}':'{node['address']}' Using {node['num_cpus']} CPUs")
    temp_dir = Path(hydra.nodes()[0]['temp'])
    print("HydraMPP temporary directory:", temp_dir)

    config['CPUS'] = hydra.nodes()[0]['num_cpus']


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

    if not any([fastq, fasta, amino, rollup]):
        parser.error("ERROR: No sequences loaded, please check the input files and try again.")

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


    print("Running main pipeline")
    results = metacerberus_pipeline.run_jobs(fastq, fasta, amino, rollup, config, config['DIR_OUT'])
    if results:
        fastq, fasta, amino, rollup, hmm_tsv, hmm_tsvs, hmmRollup, hmmCounts, readStats, NStats = results
    else:
        return 1


    # Log time of main pipeline
    time_pipeline = str(datetime.timedelta(seconds=time.time()-startTime))
    logTime(config["DIR_OUT"], socket.gethostname(), "Pipeline_time", config["DIR_OUT"], time_pipeline)

    # step 10 (Report)
    print("\nSTEP 10: Creating Reports")


    metacerberus_pipeline.report(config['DIR_OUT'], config, dbHMM, fasta, amino, hmm_tsv, hmm_tsvs, hmmRollup, hmmCounts, readStats, NStats)

    # Finished!
    print("\nFinished Pipeline")
    end = str(datetime.timedelta(seconds=time.time()-startTime))
    logTime(config["DIR_OUT"], socket.gethostname(), "Total_Time", config["DIR_OUT"], end)

    # Cleaning up
    temp_dir = Path(hydra.nodes()[0]['temp'])
    #print("Cleaning up Hydra temporary directory", temp_dir)
    #hydra.shutdown()
    #TODO: Clean temp directory
    #if temp_dir.exists():
    #    shutil.rmtree(temp_dir)

    return 0


## Start main method
if __name__ == "__main__":
    sys.exit(main())

## End of script
