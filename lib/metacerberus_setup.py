# -*- coding: utf-8 -*-

"""metacerberus_setup.py: Module for seting up dependencies
"""

import os
import re
import time
import shutil
import subprocess
import platform
import urllib.request as url

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

    pathDB = os.path.abspath(pathDB)
    os.makedirs(pathDB, exist_ok=True)
    print(f"Downloading Database files to {pathDB}")
    print("This will take a few minutes...")
    url.urlretrieve("https://osf.io/72p6g/download", os.path.join(pathDB, "FOAM_readme.txt"), reporthook=progress)
    url.urlretrieve("https://osf.io/muan4/download", os.path.join(pathDB, "FOAM-onto_rel1.tsv"), reporthook=progress)
    url.urlretrieve("https://osf.io/2hp7t/download", os.path.join(pathDB, "KEGG-onto_rel1.tsv"), reporthook=progress)
    #url.urlretrieve("https://osf.io/bdpv5/download", os.path.join(pathDB, "FOAM-hmm_rel1a.hmm.gz"))


    print("Downloading KOFam")
    url.urlretrieve("https://www.genome.jp/ftp/db/kofam/profiles.tar.gz", os.path.join(pathDB, "profiles.tar.gz"), reporthook=progress)
    print("Extracting KOFam")
    subprocess.run(['tar', '-xzf', "profiles.tar.gz"], cwd=pathDB)
    os.remove(os.path.join(pathDB, "profiles.tar.gz"))
    
    pathProfiles = os.path.join(pathDB, 'profiles')
    reKO = re.compile(r'NAME  K', re.MULTILINE)
    for db in ['prokaryote', 'eukaryote']:
        print(f"Building KOFam-{db}")
        dbList = os.path.join(pathProfiles, f'{db}.hal')
        dbOut = os.path.join(pathDB, f'KOFam_{db}.hmm')
        with open(dbList) as reader, open(dbOut, 'w') as writer:
            for line in reader:
                nextKO = os.path.join(pathProfiles, line.strip())
                writer.write(reKO.sub(r'NAME  KO:K', open(nextKO).read()))
        os.remove(dbList)
        subprocess.run(['gzip', '-f', dbOut], cwd=pathDB)

    print("Building KOFam-all")
    dbOut = os.path.join(pathDB, 'KOFam_all.hmm')
    with open(dbOut, 'w') as writer:
        for filename in os.listdir(pathProfiles):
            nextKO = os.path.join(pathProfiles, filename)
            if filename.endswith('.hmm'):
                writer.write(reKO.sub(r'NAME  KO:K', open(nextKO).read()))
            os.remove(nextKO)
    os.removedirs(pathProfiles)
    subprocess.run(['gzip', '-f', dbOut], cwd=pathDB)

    #url.urlretrieve("https://osf.io/f6q9u/download", os.path.join(pathDB, "KOFam-all.hmm.gz"))
    #url.urlretrieve("https://osf.io/km8fu/download", os.path.join(pathDB, "KOFam-eukaryote.hmm.gz"))
    #url.urlretrieve("https://osf.io/pgdua/download", os.path.join(pathDB, "KOFam-prokaryote.hmm.gz"))
    return


# Download Frag Gene Scan Plus
def FGS(pathFGS:os.PathLike):
    system = platform.system()

    if system == "Windows":
        print("Windows is not supported")
        return None
    subprocess.run(['tar', '-xzf', f'FragGeneScanRS-{system}.tar.gz'], cwd=pathFGS)

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
