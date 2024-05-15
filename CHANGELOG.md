# Change log

## Version 1.3.0

### New Features

-Custom download location for databases
-Ability to download individual databases
-Update downloaded databases (currently re-downloads the database)
-List available databases
-Custom database support
  -HMM file with .hmm extension (also supports .hmm.gz)
  -A TSV file is also required with minimum columns: ID, Function
  -The ID field must match the NAME field of the HMM file, one row per HMM entry
-Output files
  -reworked output directories to separate graphs/stats from annotation files
  -Final folder with annotation summary and files in GTF, genbank, GFF, .FAA, .FNA, .FFN
-Other improvements
  -Performance improvements
  -Improved some error handling and reporting

### Bug Fixes

-Multi-domain in summary files
  -Individual database summary files contain a line per match found
  -The combined summary file lists only the best match based on e-value
-Slurm on cluster with multiple nodes now working
-Filtering algorithm fix (on rare circumstances it would enter an infinite loop)
