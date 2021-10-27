#!/bin/bash

#SBATCH --partition=Andromeda
#SBATCH --job-name=cerberus_tests
#SBATCH --exclusive
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=256GB
#SBATCH --time=30-0
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
conda activate cerberus

if [ "$SLURM_NNODES" -gt 1 ]; then
  echo "Initializing Ray on $SLURM_NNODES Nodes"
  source cerberus_slurm.sh
fi

command time cerberus-pipeline.py -c config.yaml

echo ""
echo "======================================================"
echo "End Time   : $(date)"
echo "======================================================"
echo ""
