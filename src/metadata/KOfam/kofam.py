#!/usr/bin/env python3


import os
import gzip
import subprocess
import json
import re
import time
import pandas as pd
from pathlib import Path
import urllib.request as url
from collections import OrderedDict


in_KEGG = "ko00001_2021-07.json"
out_KEGG = "KEGG.tsv"
in_FOAM = "../FOAM.tsv"
out_FOAM = "FOAM.tsv"

ECregex = re.compile(" \[EC:([^;]*)\]")


#### Recursive Method to load nested json file ####
def convert_json(dicData, writer, level=0, parents={}):
	table = {}
	if level > 0: #first level contains no writable data
		name = dicData['name'].split(maxsplit=1)
		if level < 4:
			parents[level] = name[1]
		else:
			match = ECregex.search(name[1])
			ec = match.group(1) if match else ''
			name[1] = ECregex.sub("", name[1])
			try:
				gene,func = name[1].split('; ')
			except:
				gene = ''
				func = name[1]
			func = func[0].upper() + func[1:]
			if gene == name[0]:
				gene = ''
			print('\t'.join(parents.values()), name[0], func, ec, gene, sep='\t', file=writer)
			table[ name[0] ] = name[1]
	for value in dicData.values():
		if type(value) is list:
			for item in value:
				table.update( convert_json(item, writer, level+1, parents) )
	return table


#### Build KOFam ####
def koFam():
	start = time.time()
	def progress(block, read, size):
		nonlocal start
		down = (100*block*read) / size
		if time.time() - start > 10:
			start = time.time()
			print(f"Progress: {round(down,2)}%")
		return
	#url.urlretrieve("https://www.genome.jp/ftp/db/kofam/profiles.tar.gz", "profiles.tar.gz", reporthook=progress)
	print("Extracting KOFam")
	subprocess.run(['tar', '-xzf', "profiles.tar.gz"])
	#Path("profiles.tar.gz").unlink()
	
	pathProfiles = Path('profiles')
	reKO = re.compile(r'NAME  K', re.MULTILINE)
	for db in ['prokaryote', 'eukaryote']:
		print(f"Building KOFam_{db}")
		dbList = Path(pathProfiles, f'{db}.hal')
		dbOut = f'KOFam_{db}.hmm.gz'
		with dbList.open() as reader, gzip.open(dbOut, 'wt') as writer:
			for line in reader:
				nextKO = Path(pathProfiles, line.strip())
				writer.write(nextKO.read_text())
		#dbList.unlink()
		#subprocess.run(['gzip', '-f', dbOut])
	
	print("Building KOFam_all")
	dbOut = 'KOFam_all.hmm.gz'
	with gzip.open(dbOut, 'wt') as writer:
		for filename in os.listdir(pathProfiles):
			nextKO = Path(pathProfiles, filename)
			if filename.endswith('.hmm'):
				writer.write(nextKO.read_text())
			#nextKO.unlink()
	#pathProfiles.rmdir()
	#subprocess.run(['gzip', '-f', dbOut])
	return

#### START ####

koFam()

# read file
with open(in_KEGG) as reader:
	data = json.load(reader)

# parse json
with open(out_KEGG, 'w') as writer:
	print("L1", "L2", "L3", "ID", "Function", "EC", "Gene", sep='\t', file=writer)
	table = convert_json(data, writer)

# add functions from KEGG to FOAM
koNames = {}
koEC = {}
for key,val in table.items(): # split the names and the EC
	koNames[key] = ECregex.sub("", val)
	match = ECregex.search(val)
	if match:
		koEC[key] = match.group(1)

#df = pd.read_csv(in_FOAM, sep='\t')
#df['Function'] = df['ID'].map(koNames)
#df['EC'] = df['KO'].map(koEC)
#
#df.to_csv(out_FOAM, sep='\t', index=False)
