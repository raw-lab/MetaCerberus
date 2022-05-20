#!/bin/bash

#SBATCH --partition=Orion
#SBATCH --job-name=MetaCerberus-Update
#SBATCH --nodes=3
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=56GB
#SBATCH --time=1-0
#SBATCH -o slurm-%x-%j.out
#SBATCH --mail-type=END,FAIL,REQUEUE

echo "====================================================="
echo "Start Time  : $(date)"
echo "Submit Dir  : $SLURM_SUBMIT_DIR"
echo "Job ID/Name : $SLURM_JOBID / $SLURM_JOB_NAME"
echo "Node List   : $SLURM_JOB_NODELIST"
echo "Num Tasks   : $SLURM_NTASKS total [$SLURM_NNODES nodes @ $SLURM_CPUS_ON_NODE CPUs/node]"
echo "======================================================"
echo ""


module load anaconda3
eval "$(conda shell.bash hook)"
conda activate metacerberus


# run MetaCerberus
command time metacerberus.py -c config.yaml --cpus $SLURM_CPUS_ON_NODE --slurm_nodes $SLURM_JOB_NODELIST


echo ""
echo "======================================================"
echo "End Time   : $(date)"
echo "======================================================"
echo ""
