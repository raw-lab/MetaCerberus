Multiprocessing MultiComputing with RAY
===========================================

- MetaCerberus uses Ray for distributed processing. This is compatible with both multiprocessing on a single node (computer) or multiple nodes in a cluster.  
MetaCerberus has been tested on a cluster using `Slurm`_.  

.. _Slurm: https://github.com/SchedMD/slurm

.. :important::
   A script has been included to facilitate running MetaCerberus on Slurm. To use MetaCerberus on a Slurm cluster, setup your slurm script and run it using ``sbatch``.  

Example command to run your slurm script:
-----------------------------------------
::

   sbatch example_script.sh


Example Script:  
-------------------
::

   #!/usr/bin/env bash

   #SBATCH --job-name=test-job
   #SBATCH --nodes=3
   #SBATCH --tasks-per-node=1
   #SBATCH --cpus-per-task=16
   #SBATCH --mem=128MB
   #SBATCH -e slurm-%j.err
   #SBATCH -o slurm-%j.out
   #SBATCH --mail-type=END,FAIL,REQUEUE

   echo "====================================================="
   echo "Start Time  : $(date)"
   echo "Submit Dir  : $SLURM_SUBMIT_DIR"
   echo "Job ID/Name : $SLURM_JOBID / $SLURM_JOB_NAME"
   echo "Node List   : $SLURM_JOB_NODELIST"
   echo "Num Tasks   : $SLURM_NTASKS total [$SLURM_NNODES nodes @ $SLURM_CPUS_ON_NODE CPUs/node]"
   echo "======================================================"
   echo ""

   # Load any modules or resources here
   conda activate metacerberus
   # source the slurm script to initialize the Ray worker nodes
   source ray-slurm-metacerberus.sh
   # run MetaCerberus
   metacerberus.py --prodigal [input_folder] --illumina --dir_out [out_folder]

   echo ""
   echo "======================================================"
   echo "End Time   : $(date)"
   echo "======================================================"
   echo ""
