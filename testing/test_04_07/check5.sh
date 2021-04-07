#!/bin/bash
#
#SBATCH --job-name=check5
#SBATCH --output=res5.txt
#
#SBATCH --time=11:59:00
#SBATCH --mem-per-cpu=50000

module load anaconda3
conda activate cerberus_env
python mem_usage.py python cerberus.py -i data/GIC31.fasta