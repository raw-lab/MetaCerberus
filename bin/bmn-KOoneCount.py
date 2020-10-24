#!/usr/bin/env python
import argparse
from argparse import RawTextHelpFormatter
import sys

parser = argparse.ArgumentParser(description="""
HMM in maudules can target several KOs, and give this result (example 1):

KO:K00100,KO:K00224     2
KO:K00120       716
KO:K00128       4573
KO:K00128,KO:K00131,KO:K00135   10

This program separates the KO IDs and adds the corresponding number
divided by the number of split KOs to the corresponding KO (example 2):

KO:K00100	1
KO:K00120	716
KO:K00128	4576.33
KO:K00131	3.33
KO:K00135	3.33
KO:K00224	1

""", formatter_class=RawTextHelpFormatter)
parser.add_argument("rawKOcount", help="""
	File with 'raw' KO counts as showed in example 1,
	for instance, a countEachElement.py output""")
args = parser.parse_args()

nmap=dict()

with open(args.rawKOcount, 'r') as KOfile:
    for line in KOfile:
        if line[0:2]!="KO":
            continue
        [KO,n1]=line.split()
        Ksplit=KO.split(',')
        n2=float(n1)/len(Ksplit)
        for K in Ksplit:
            if nmap.has_key(K):
                nmap[K]=nmap[K]+n2
            else: nmap[K]=n2
                

for [KO,nb] in nmap.items():
	print KO,'{0:.2f}'.format(nb)

