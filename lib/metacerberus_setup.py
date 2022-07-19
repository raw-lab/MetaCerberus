# -*- coding: utf-8 -*-

"""metacerberus_setup.py: Module for seting up dependencies
"""

import os
import shutil
import subprocess
import platform
import urllib.request as url
from git import Repo


# Download Database
def Download(pathDB):
    os.makedirs(pathDB, exist_ok=True)
    print(f"Downloading Database files to {pathDB}")
    print("This will take a few minutes...")
    url.urlretrieve("https://osf.io/72p6g/download", os.path.join(pathDB, "FOAM_readme.txt"))
    url.urlretrieve("https://osf.io/muan4/download", os.path.join(pathDB, "FOAM-onto_rel1.tsv"))
    url.urlretrieve("https://osf.io/2hp7t/download", os.path.join(pathDB, "KEGG-onto_rel1.tsv"))
    url.urlretrieve("https://osf.io/bdpv5/download", os.path.join(pathDB, "FOAM-hmm_rel1a.hmm.gz"))
    return


# Download Frag Gene Scan Plus
def FGS(pathFGS:os.PathLike):
    #command = "wget -qO- https://github.com/unipept/FragGeneScanRs/releases/download/v1.1.0/FragGeneScanRs-v1.1.0-x86_64-unknown-linux-musl.tar.gz | tar -xz"
    #os.makedirs(pathFGS, exist_ok=True)
    #url.urlretrieve("https://github.com/unipept/FragGeneScanRs/releases/download/v1.1.0/FragGeneScanRs-v1.1.0-x86_64-unknown-linux-musl.tar.gz",
    #                os.path.join(pathFGS, "FragGeneScanRS.tar.gz"))
    #subprocess.run(['tar', '-xzf', 'FragGeneScanRS.tar.gz'], cwd=pathFGS)
    
    system = platform.system()
    if system == "Windows":
        print("Windows is not supported")
        return None
    subprocess.run(['tar', '-xzf', f'FragGeneScanRS-{system}.tar.gz'], cwd=pathFGS)

    #os.makedirs(pathFGS, exist_ok=True)
    #print(f"Cloning FGS+ to {pathFGS}")
    #try:
    #    Repo.clone_from("https://github.com/hallamlab/FragGeneScanPlus", pathFGS)
    #except:
    #    print("Cloning repo failed, possibly already exists")
    ##rm -rf "$fgspath/.git*"
    #subprocess.run(f'make CFLAG="-fcommon -w" -C "{pathFGS}"', shell=True)
    return os.path.join(pathFGS, 'FragGeneScanRS')


# Remove Database and FGS+
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
