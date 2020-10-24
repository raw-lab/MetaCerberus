#!/usr/bin/env python
import sys
from collections import Counter

tids = sys.argv[1] #File of genbank tids

ac=open(tids, 'r')

	
lignes = ac.readlines()
ac.close()

mytids=[]

for i in lignes:
	mytids.append(str.strip(i,"\n"))


cnt = Counter()
for word in mytids:
	cnt[word] += 1

for i in cnt.keys():
	print str(i)+"\t"+str(cnt[i])



