#!/usr/bin/env python


target = dict()
with open("/home/jlfiguer/Documents/MetaCerberus/Inphrared/1Feb2024_vConTACT2_proteins.faa") as reader:
	for line in reader:
		if line.startswith('>'):
			line = line.strip('\n').split(maxsplit=1)
			target[line[0][1:]] = line[1]

pvog = dict()
with open("annotation_summary.tsv") as reader:
	header = reader.readline().strip('\n').split('\t')
	for line in reader:
		line = line.strip('\n').split('\t')
		if line[3] == "Hypothetical":
			continue
		try:
			if line[1] not in pvog:
				pvog[line[1]] = [line[0], float(line[5])]
			if float(line[5]) > pvog[line[1]][1]:
				pvog[line[1]] = [line[0], float(line[5])]
		except:
			print(line[0:2], line[4:6])
			exit(1)

err = 0
with open("PVOG.tsv", 'w') as writer:
	for k,v in sorted(pvog.items()):
		if v[0] in target:
			print(k, target[v[0]], sep='\t', file=writer)
		else:
			err += 1

print(err)

# 0 "target"
# 1 "best_hit"
# 2 "HMM"
# 3 "product"
# 4 "evalue"
# 5 "score"
# 6 "EC"
# 7 "PVOG"
# 8 "PVOG_name"
# 9 "PVOG_evalue"
# "PVOG_score"
# "EC"
# "PVOG_length"
