#!/usr/bin/env python


with open("tigrfam.info") as reader, open("TIGRFAM.tsv", 'w') as writer:
	print("ID", "Function", "Gene", sep='\t', file=writer)
	for line in reader:
		if line.startswith("AC"):
			ID = line.rstrip().split(maxsplit=1)[1]
		if line.startswith("DE"): #EN
			FUNCTION = line.rstrip().split(maxsplit=1)[1]
		if line.startswith("GS"):
			GENEID = line.rstrip().split(maxsplit=1)[1]
		if line.startswith("TP"):
			print(ID, FUNCTION, GENEID, sep='\t', file=writer)
			ID = FUNCTION = GENEID = ""
