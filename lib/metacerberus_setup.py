# -*- coding: utf-8 -*-

"""metacerberus_setup.py: Module for seting up dependencies
"""

import os
import time
import shutil
import subprocess
import platform
import urllib.request as url
from pathlib import Path


def list_db(pathDB):
    pathDB = Path(pathDB).absolute()
    pathDB.mkdir(exist_ok=True, parents=True)
    db_tsv = Path(pathDB, "databases.tsv")
    url.urlretrieve("https://raw.githubusercontent.com/raw-lab/MetaCerberus/main/lib/DB/databases.tsv", db_tsv)
    databases = dict()
    url_paths = dict()
    hmm_version = dict()
    downloaded = dict()
    incomplete = dict()
    to_download = dict()
    with db_tsv.open() as reader:
        header = reader.readline().split()
        for line in reader:
            name,filename,urlpath,date = line.split()
            if name not in databases:
                databases[name] = list()
            databases[name] += [filename]

            if name not in url_paths:
                url_paths[name] = dict()
            url_paths[name][filename] = urlpath

            hmm_version[name] = date

    for name,filelist in databases.items():
        down = True
        for filename in filelist:
            filepath = Path(pathDB, filename)
            if not filepath.exists():
                down = False
        if down:
            downloaded[name] = list()
            for filename in filelist:
                filepath = Path(pathDB, filename)
                downloaded[name] += [filepath]
        else:
            to_download[name] = filelist
    return downloaded, to_download, url_paths, hmm_version


# Download Database
def download(pathDB, hmms):
    start = time.time()
    def progress(block, read, size):
        nonlocal start
        down = (100*block*read) / size
        if time.time() - start > 10:
            start = time.time()
            print(f"Progress: {round(down,2)}%")
        return

    pathDB = Path(pathDB).absolute()
    pathDB.mkdir(exist_ok=True, parents=True)
    print(f"Downloading Database files to {pathDB}")
    
    downloaded,to_download,urls,hmm_version = list_db(pathDB)

    if not hmms:
        if to_download:
            print("This may take a few minutes...")
        else:
            print("All know databases already downloaded")
        for name,filelist in to_download.items():
            for filename,urlpath in urls[name].items():
                filepath = Path(pathDB, filename)
                start = time.time()
                print("Downloading:", filename)
                url.urlretrieve(urlpath, filepath, reporthook=progress)
                print(f"Progress: 100%")
    else:
        print("This may take a few minutes...")
        for hmm in hmms:
            if hmm in downloaded:
                print("Database exists, use --update to re-download:", hmm)
            elif hmm in to_download:
                for filename,urlpath in urls[hmm].items():
                    filepath = Path(pathDB, filename)
                    start = time.time()
                    print("Downloading:", filename)
                    url.urlretrieve(urlpath, filepath, reporthook=progress)
                    print(f"Progress: 100%")
            else:
                print("Warning: '",hmm, "' not found in HMMs to download.")
    return


# Update already downloaded databases
def update(pathDB):
    downloaded,to_download,urls,hmm_version = list_db(pathDB)
    for name,filelist in downloaded.items():
        for filepath in filelist:
            Path(filepath).unlink()
    download(pathDB, downloaded.keys())
    return


# Copy FragGeneScanRS
def FGS(pathFGS:os.PathLike):
    system = platform.system()

    if system == "Windows":
        print("Windows is not supported")
        return None
    subprocess.run(['tar', '-xzf', f'FragGeneScanRS-{system}.tar.gz'], cwd=pathFGS)

    return os.path.join(pathFGS, 'FragGeneScanRS')


# Remove Database and FGSRS
def remove(pathDB, pathFGS):
    shutil.rmtree(pathDB, ignore_errors=True)
    shutil.rmtree(os.path.join(pathFGS, "FragGeneScanRS"), ignore_errors=True)
    return


# Setup SLURM
def slurm(SLURM_JOB_NODELIST):
    """Sets up RAY on a SLURM cluster
    Not Yet Fully Implemented"""

    print("WARNING: Not yet fully implemented")

    proc = subprocess.run(['scontrol', 'show', 'hostnames', SLURM_JOB_NODELIST],
        stdout=subprocess.PIPE, text=True)
    if proc.returncode == 0:
        nodes = proc.stdout.split()
    else:
        print(f"ERROR executing 'scontrol show hostnames {SLURM_JOB_NODELIST}'")
        return None
    print("NODES:", nodes)

    head_node = nodes[0]
    proc = subprocess.run(['srun', '--nodes=1', '--ntasks=1', '-w', head_node, 'hostname', '--ip-address'],
        stdout=subprocess.PIPE, text=True)
    if proc.returncode == 0:
        head_node_ip = proc.stdout.strip()
    else:
        print(f"ERROR getting head node IP")
        return None

    port = 6379
    ip_head = f"{head_node_ip}:{port}"
    print("IP Head:", ip_head)

    print("Starting HEAD at", head_node)
    cmd = ["srun", "--nodes=1", "--ntasks=1", "-w", head_node, "ray", "start", "--head", f"--node-ip-address={head_node_ip}", f"--port={port}", "--num-cpus", "1", "--block"]
    subprocess.Popen(cmd)
    time.sleep(5)

    # Start Worker Nodes
    for i in range(1, len(nodes)):
        print(f"Starting WORKER {i} at {nodes[i]}")
        cmd = ["srun", "--nodes=1", "--ntasks=1", "-w", nodes[i], "ray", "start", "--address", ip_head, "--num-cpus", "1", "--block"]
        subprocess.Popen(cmd)
        time.sleep(5)
    return
