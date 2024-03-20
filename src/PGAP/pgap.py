#! /usr/bin/env python



def lookup():
	with open("hmm_PGAP.tsv") as reader, open("PGAP.tsv", 'w') as writer:
		print("ID", "Function", "Source", sep='\t', file=writer)
		reader.readline()
		for line in reader:
			line = line.rstrip('\n').split('\t')
			SOURCE = line[1]
			ID = line[2]
			FUNCTION = line[10]
			print(ID, FUNCTION, SOURCE, sep='\t', file=writer)


lookup()
