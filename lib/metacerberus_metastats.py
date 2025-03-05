# -*- coding: utf-8 -*-

"""metacerberus_metastats.py: Module for checking quality of .fastq files
Uses countfasta.py
"""

import os
import subprocess
from pathlib import Path


# Check contigs
def getReadStats(contig, config:dict, subdir:Path):
    subdir = Path(subdir)
    os.makedirs(subdir, exist_ok=True)
    
    # Metaome_stats
    try:
        command = [ config['EXE_COUNT_ASSEMBLY'], '-f', contig, '-i 100' ]
        with open(f"{subdir}/stderr.txt", 'w') as ferr, open(f"{subdir}/read-stats.txt", 'w') as writer:
            proc = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=ferr)
            stats = proc.stdout.decode('utf-8', 'ignore')
            writer.write(stats)
    except Exception as e:
        print(e)
        print("Error: countAssembly.py failed: " + subdir)
        print(command)

    return stats
