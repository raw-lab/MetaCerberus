#! /usr/bin/env python


import re
import gzip


def fix_hmm():
	with open("AMRFinder.hmm") as reader, gzip.open("AMRFinder.hmm.gz", 'wt') as writer:
		prev = ""
		line = reader.readline()
		while line:
			match = re.search(r'ACC\s+([A-Z0-9.]+)', line)
			if match:
				name = match.group(1)
				print("NAME ", name, file=writer)
			elif prev:
				writer.write(prev)
			prev = line
			line = reader.readline()
		writer.write(prev)


def lookup():
	with open("NCBIfam-AMRFinder.tsv") as reader, open("AMRFinder.tsv", 'w') as writer:
		print("L1", "L2", "ID", "Function", "Gene", sep='\t', file=writer)
		reader.readline()
		for line in reader:
			line = line.rstrip('\n').split('\t')
			ID = line[0]
			GENE = line[3]
			FUNCTION = line[5]
			L1 = line[9]
			L2 = line[10]
			print(L1, L2, ID, FUNCTION, GENE, sep='\t', file=writer)


fix_hmm()
lookup()
