#!/usr/bin/env python

import re
from pathlib import Path

cazy_onto = "CAZyDB.08062022.fam-activities.tsv"
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


fun = Path(fun_lookup).read_text()
with open(cazy_onto) as cazy, open(cazy_out, 'w') as writer:
    print('ID', 'FUN', 'EC', 'NAME', sep='\t', file=writer)
    for line in cazy:
        if line.startswith('#'):
            continue
        match = re.search(rf'(\w+)\t(.+?)\(EC ([0-9.-]+)\)', line)
        if match:
            ID,NAME,EC = match.groups()
            NAME = NAME.strip()
        else:
            ID = re.search(rf'(\w+)\t', line).group(1)
            NAME = ''
            EC = ''

        FUN_ID = re.search(r'^([A-Z]+)', ID).group(1)
        FUN = re.search(rf'{FUN_ID}\t(.+)', fun).group(1)
        print(ID, FUN, EC, NAME, sep='\t', file=writer)
