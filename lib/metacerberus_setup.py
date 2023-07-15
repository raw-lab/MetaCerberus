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


# Download Database
def Download(pathDB):
    start = 0
    downloaded = 0
    def progress(block, read, size):
        nonlocal start
        nonlocal downloaded
        if block == 1:
            start = 0
            downloaded = 0
        downloaded += block*read
        if time.time() - start > 10:
            start = time.time()

            print("Progress:", downloaded)

            sz = round(block*read, 2)

            if sz < 2^10:
                sz = f"{sz} Bytes"
            elif sz < 2^20:
                sz = f"{round((sz)/2^10, 2)} Kb"
            else:
                sz = f"{round((sz)/2^20, 2)} Mb"

            if size < 2^10:
                size = f"{sz} Bytes"
            elif size < 2^20:
                size = f"{round((size)/2^10, 2)} Kb"
            else:
                size = f"{round((size)/2^20, 2)} Mb"

            if size > 0:
                print("Downloaded", sz, "out of:", size)
            else:
                print("Downloaded", sz)
        return

    pathDB = Path(pathDB).absolute()
    pathDB.mkdir(exist_ok=True, parents=True)
    print(f"Downloading Database files to {pathDB}")
    print("This will take a few minutes...")
    url.urlretrieve("https://osf.io/d5m6h/download", Path(pathDB, "FOAM-onto_rel1.tsv"))#, reporthook=progress)
    url.urlretrieve("https://osf.io/jgk73/download", Path(pathDB, "KEGG-onto_rel1.tsv"))#, reporthook=progress)

    url.urlretrieve("https://osf.io/cuw94/download", Path(pathDB, "CAZy-onto_rel1.tsv"))#, reporthook=progress)
    url.urlretrieve("https://osf.io/579bc/download", Path(pathDB, "COG-onto_rel1.tsv"))#, reporthook=progress)
    url.urlretrieve("https://osf.io/dnc27/download", Path(pathDB, "PHROG-onto_rel1.tsv"))#, reporthook=progress)
    url.urlretrieve("https://osf.io/pd29f/download", Path(pathDB, "VOG-onto_rel1.tsv"))#, reporthook=progress)

    print("Downloading CAZy")
    url.urlretrieve("https://osf.io/8bxyj/download", os.path.join(pathDB, "CAZy.hmm.gz"))

    print("Downloading COG")
    url.urlretrieve("https://osf.io/ncsfx/download", os.path.join(pathDB, "COG-noIter.hmm.gz"))

    print("Downloading PHROG")
    url.urlretrieve("https://osf.io/5zdnv/download", os.path.join(pathDB, "PHROG.hmm.gz"))

    print("Downloading VOG")
    url.urlretrieve("https://osf.io/93mhp/download", os.path.join(pathDB, "VOG.hmm.gz"))

    print("Downloading KOFam")
    url.urlretrieve("https://osf.io/8dse5/download", os.path.join(pathDB, "KOFam_prokaryote.hmm.gz"))
    url.urlretrieve("https://osf.io/gk7vx/download", os.path.join(pathDB, "KOFam_eukaryote.hmm.gz"))
    url.urlretrieve("https://osf.io/yga2f/download", os.path.join(pathDB, "KOFam_all.hmm.gz"))

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
def Remove(pathDB, pathFGS):
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
