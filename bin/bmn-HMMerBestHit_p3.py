#!/usr/bin/env python
# the lines should be grouped by queries (as usual, do sort file.hmm if not)

import string
import re
import argparse
import sys

parser = argparse.ArgumentParser(description="Returns a 'Best Hits' filtered HMM tab output")
parser.add_argument("HMMERres", help="the HMMer tab output")
parser.add_argument("-c", "--column", type=int, default=14, help="default is 14, i.e. the p/ dom score")
parser.add_argument("-s", "--minscore", type=float, default=25, help="the min score required to keep the hit, default is 25")
args = parser.parse_args()

HMMERres = args.HMMERres
col = args.column - 1
minscore = float(args.minscore)

try:
	Hits=open(HMMERres, 'r')
except IOError as e:
	print("HMM output file not found or unreadable: " + HMMERres.strip())
	pass

while True:
	bestHit=Hits.readline()
	if not bestHit.startswith("#"):	
		maxscore=float(bestHit.split()[col])
		query=bestHit.split()[0]
		break

for hit in Hits:
	if not hit.startswith("#"):
		hitSplit=hit.split()
	else: continue
	curScore=float(hitSplit[col])
	if curScore >= minscore:
		if query!=hitSplit[0]:
			if float(bestHit.split()[col]) >= minscore :
				print(bestHit.strip())
			query=hitSplit[0]
			maxscore=float(0)
			bestHit=hit
		elif maxscore<=float(hitSplit[col]):
			bestHit=hit
			maxscore=float(hitSplit[col])
if bestHit is not None:
	print (bestHit.strip())

Hits.close()

