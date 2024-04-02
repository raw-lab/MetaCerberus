#!/usr/bin/env python

import re
from pathlib import Path

vog_annot = Path("vog_annotations.tsv")
vog_cat = Path("vog_functional_categories.txt")
vog_onto = Path("VOG-onto_rel1.tsv")


#GroupName	ProteinCount	SpeciesCount	FunctionalCategory	ConsensusFunctionalDescription

vog_cat = vog_cat.read_text()
with vog_annot.open() as reader, vog_onto.open('w') as writer:
	print("L1", "ID", "Function", "EC", "UNIPROT ID", sep='\t', file=writer)
	reader.readline() # Skip header
	for line in reader:
		ID,pcount,scount,CAT,NAME = line.strip('\n').split('\t')
		L1 = ""
		for i in range(0, len(CAT), 2):
			code = CAT[i:i+2]
			match = re.search(rf'\[{code}\] (.*)', vog_cat, re.MULTILINE)
			if match:
				L1 += f'{match.group(1)} | '
		L1 = L1.rstrip('| ')

		if NAME.startswith("REFSEQ"):
			UNIPROT = ""
			NAME = NAME.split(maxsplit=1)[-1]
		else:
			UNIPROT,NAME = NAME.split('|')[-1].split(maxsplit=1)

		NAME = NAME[0].upper() + NAME[1:]

		print(L1, ID, NAME, "", UNIPROT, sep='\t', file=writer)
