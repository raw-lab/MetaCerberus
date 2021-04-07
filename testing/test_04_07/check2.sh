#!/bin/bash
#
#SBATCH --job-name=check2
#SBATCH --output=res2.txt
#
#SBATCH --time=11:59:00
#SBATCH --mem-per-cpu=50000

module load anaconda3
conda activate cerberus_env
python mem_usage.py python cerberus.py -i data/RW2.fna