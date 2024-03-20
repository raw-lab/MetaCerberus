#! /usr/bin/env python


import re
import gzip


def fix_hmm():
	with open("Pfam.hmm") as reader, gzip.open("Pfam.hmm.gz", 'wt') as writer:
		prev = ""
		line = reader.readline()
		while line:
			match = re.search(r'ACC\s+([A-Z0-9]+)', line)
			if match:
				name = match.group(1)
				print("NAME ", name, file=writer)
			elif prev:
				writer.write(prev)
			prev = line
			line = reader.readline()
		writer.write(prev)


def lookup():
	with open("Pfam-A.clans.tsv") as reader, open("Pfam.tsv", 'w') as writer:
		print("ID", "Function", "Clan", "Gene", sep='\t', file=writer)
		for line in reader:
			line = line.rstrip('\n').split('\t')
			ID = line[0]
			CLAN = line[1]
			CLAN_NAME = line[2]
			GENE = line[3]
			FUNCTION = line[4]
			print(ID, FUNCTION, CLAN, GENE, sep='\t', file=writer)


#fix_hmm()
lookup()
