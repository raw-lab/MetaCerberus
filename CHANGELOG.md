# Change log

## Version 1.4.0

### v1.4.0 New Features

- Replaced Ray with HydraMPP
  - Reduced number of dependencies making install easier

### v1.4.0 Improvements

- Removed a redundant hmm search when using KOFam
- Organized output files

### v1.4.0 Bug Fixes

- Fixed resume feature for hmm step
- Fixed counting conflict between parser and filter steps

## Version 1.3.2

### v1.3.2 Bug Fixes

- Fixed Ray dependency issue for MetaCerberus-lite, or when Ray is not available.

## Version 1.3.1

### v1.3.1 New Features

- created "lite" version.
  - removed hard dependency requirements, failing more gracefully to make some dependencies optional
  - added linear override for Ray when Ray is not found
- Implemented PyHMMER
- Implemented Pyrodigal
- Implemented Pyrodigal-gv
- Added ORF start and end to output summary files
- Improved speed in creating final GFF files
- Fixed dependency checking for lite version
- Made N removal optional
- Improved Genbank output

### v1.3.1 Bug Fixes

- Fixed prodigal-gv GFF
- Fixed some Phanotate bugs
- Fixed bug with --protein option
- Fixed crash when GFF is not present
- Other minor bug fixes

## Version 1.3.0

### v1.3.0 New Features

- Custom download location for databases
- Ability to download individual databases
- Update downloaded databases (currently re-downloads the database)
- List available databases
- Custom database support
  -HMM file with .hmm extension (also supports .hmm.gz)
  -A TSV file is also required with minimum columns: ID, Function
  -The ID field must match the NAME field of the HMM file, one row per HMM entry
- Output files
  -reworked output directories to separate graphs/stats from annotation files
  -Final folder with annotation summary and files in GTF, genbank, GFF, .FAA, .FNA, .FFN
- Other improvements
  -Performance improvements
  -Improved some error handling and reporting

### v1.3.0 Bug Fixes

- Multi-domain in summary files
  -Individual database summary files contain a line per match found
  -The combined summary file lists only the best match based on e-value
- Slurm on cluster with multiple nodes now working
- Filtering algorithm fix (on rare circumstances it would enter an infinite loop)
