#!/usr/bin/env python

import re
from pathlib import Path

cog_def = "cog-20.def.tab"
fun_lookup = "fun-20.tab"
cog_out = "COG-onto_rel1.tsv"

#COG0001	H	Glutamate-1-semialdehyde aminotransferase	HemL	Heme biosynthesis		2CFB
#COG-ID     CAT FUNCTION                                    GENE    PATHWAY                 PDB

#1. COG ID
#2. COG functional category (could include multiple letters in the order of importance)
#3. COG name
#4. Gene associated with the COG (optional)
#5. Functional pathway associated with the COG (optional)
#6. PubMed ID, associated with the COG (multiple entries are semicolon-separated; optional)
#7. PDB ID of the structure associated with the COG (multiple entries are semicolon-separated; optional)

#H	DCDCFC	Coenzyme transport and metabolism
#1. Functional category ID (one letter)
#2. Hexadecimal RGB color associated with the functional category
#3. Functional category description

#L1	L2	L3	ID	Function	EC
#Metabolism	Carbohydrate metabolism	Glycolysis / Gluconeogenesis [PATH:ko00010]	K00844	HK; hexokinase	2.7.1.1

# CORRECTED:
#L1 - Coenzyme transport and metabolism
#L2 - Heme biosynthesis
#L3 - HemL
#L4 - 2CFB
#F  - Glutamate-1-semialdehyde aminotransferase


fun = Path(fun_lookup).read_text()
with open(cog_def) as cog, open(cog_out, 'w') as writer:
    print('L1', 'L2', 'L3', 'L4', 'ID', 'Function', 'EC', sep='\t', file=writer)
    for line in cog:
        COG_ID, FUN_CAT, FUNCTION, GENE, PATHWAY, PUBMED, PDB_ID = line.strip('\n').split('\t')
        CAT_NAME = list()
        for c in FUN_CAT:
            COLOR,CAT = re.search(rf'{c}\t(.*)\t(.*)', fun).groups()
            CAT_NAME += [CAT]
        print(''.join(CAT_NAME), PATHWAY, GENE, PDB_ID, COG_ID, FUNCTION, '', sep='\t', file=writer)
