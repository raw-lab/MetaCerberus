#!/usr/bin/env python

import re
from pathlib import Path

cazy_lookup = "CAZyDB.08062022.fam-activities-FIXED.tsv"
fun_lookup = "CAZy.tsv"
cazy_out = "CAZy-onto_rel1.tsv"

#AA15	lytic cellulose monooxygenase (C1-hydroxylating) (EC 1.14.99.54); lytic chitin monooxygenase (EC 1.14.99.53)
#1. ID
#2. Description (EC 1.14.99.-)

#AA	Auxiliary activities
#1. Functional category ID
#2. Functional category description

#L1	L2	ID	Function	EC
#Auxiliary activities	lytic cellulose monooxygenase (C1-hydroxylating)	AA15	1.14.99.53


print("Creating lookup table")
fun = Path(fun_lookup).read_text()
with open(cazy_lookup) as cazy, open(cazy_out, 'w') as writer:
    print('L1', 'ID', 'Function', 'EC', 'FUN_ID', sep='\t', file=writer)
    cazy.readline() # Skip Header
    for line in cazy:
        if line.startswith('#'):
            continue
        ID,NAME,EC = line.strip('\n').split('\t')
        
        match = re.search(r'^([A-Z]+)', ID)
        if match:
            CAT_ID = match.group(1)
            CAT = re.search(rf'{CAT_ID}\t(.+)', fun).group(1)
            print(CAT, ID, NAME, EC, CAT_ID, sep='\t', file=writer)
        else:
            print('ERROR:', line)

print("Fixing HMM db")
zcat dbCAN-HMMdb-V11.hmm.gz | sed "s/\.hmm//g" | gzip > CAZy.hmm.gz
