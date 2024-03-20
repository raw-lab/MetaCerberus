#! /usr/bin/env python


def lookup():
	with open("gvog.complete.annot.tsv") as reader, open("GVDB.tsv", 'w') as writer:
		print("ID", "Function", sep='\t', file=writer)
		reader.readline()
		for line in reader:
			line = line.rstrip('\n').split('\t')
			ID = line[0]
			FUNCTION = line[4]
			print(ID, FUNCTION, sep='\t', file=writer)


lookup()
