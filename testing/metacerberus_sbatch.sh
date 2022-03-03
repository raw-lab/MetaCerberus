#!/bin/bash

#SBATCH --partition=Orion
#SBATCH --job-name=cerberus_tests
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128GB
#SBATCH --time=1-0
#SBATCH -e slurm-%x-%j.err
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

if [ "$SLURM_NNODES" -gt 1 ]; then
  echo "Initializing Ray on $SLURM_NNODES Nodes"
  source slurm-metacerberus.sh
fi

command time meta-cerberus.py -c config.yaml

echo ""
echo "======================================================"
echo "End Time   : $(date)"
echo "======================================================"
echo ""
