#!/usr/bin/env python

import re
import shutil
from pathlib import Path


samples = open('samples_combined_fna.txt').read()
outdir = Path('samples', 'proteins')
for filename in Path('bak-results').rglob('*.faa'):
	if not re.search(r'Metacerberus', str(filename)):
		continue
	#outfile = Path('PROTEINS', *filename.parts[2:])
	name = filename.parent.name.lstrip('prodigal_')
	#print(filename, filename.parent.name.lstrip('prodigal_'))
	match = re.search(fr'(.*){name}.fna', samples, re.MULTILINE)
	if match:
		#print(filename)
		outfile = Path("PROTEINS", match.group(1), f'{name}.faa')
		#print(outfile)
		outfile.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy(filename, outfile)
