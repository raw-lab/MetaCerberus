#!/usr/bin/env python


from pathlib import Path

phrog_annot = Path("phrog_annot_v4.tsv")
phrog_onto = Path("PHROG-onto_rel1.tsv")


#phrog	color	annot	category

with phrog_annot.open() as reader, phrog_onto.open('w') as writer:
	print("L1", "ID", "Function", "EC", sep='\t', file=writer)
	reader.readline() # Skip header
	for line in reader:
		ID,COL,NAME,L1 = line.strip('\n').split('\t')
		print(L1, f"phrog_{ID}", NAME, "", sep='\t', file=writer)
