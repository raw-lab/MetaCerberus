#! /usr/bin/env python


import re
import gzip
import time
import urllib.request as url


def fix_hmm():
	start = time.time()
	def progress(block, read, size):
		nonlocal start
		down = (100*block*read) / size
		if time.time() - start > 10:
			start = time.time()
			print(f"Progress: {round(down,2)}%")
		return
	url.urlretrieve("http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz", "Pfam-A.hmm.gz", reporthook=progress)

	with gzip.open("Pfam-A.hmm.gz", 'rt') as reader, gzip.open("../Pfam.hmm.gz", 'wt') as writer:
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
	url.urlretrieve("http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.clans.tsv.gz", "Pfam-A.clans.tsv.gz")

	with gzip.open("Pfam-A.clans.tsv.gz", 'rt') as reader, open("../Pfam.tsv", 'w') as writer:
		print("ID", "Function", "Clan", "Gene", sep='\t', file=writer)
		for line in reader:
			line = line.rstrip('\n').split('\t')
			ID = line[0]
			CLAN = line[1]
			CLAN_NAME = line[2]
			GENE = line[3]
			FUNCTION = line[4]
			print(ID, FUNCTION, CLAN, GENE, sep='\t', file=writer)


url.urlretrieve("http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/relnotes.txt", "relnotes.txt")

#fix_hmm()
#lookup()
