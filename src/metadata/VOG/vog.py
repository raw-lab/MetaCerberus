#!/usr/bin/env python

import re
from pathlib import Path
import io
import urllib.request as url
import gzip
import tarfile as tar


def main():
	path, baseurl = download()
	parse(path)
	download_hmm(path, baseurl)
	return


# Download latest files.
def download():
	baseurl = "https://fileshare.lisc.univie.ac.at/vog/latest"
	version = url.urlopen(f"{baseurl}/release.txt").read().decode().strip()
	path = Path(version)

	path.mkdir(parents=True, exist_ok=True)

	print("Downloading: vog.annotations.tsv.gz")
	with open(path/"vog-annotations.tsv", 'w') as writer:
		data = url.urlopen(f"{baseurl}/vog.annotations.tsv.gz").read()
		data = gzip.decompress(data)
		writer.write(data.decode())

	print("Downloading: vogdb.functional_categories.txt")
	with open(path/"vogdb-functional_categories.txt", 'w') as writer:
		data = url.urlopen(f"{baseurl}/vogdb.functional_categories.txt").read()
		writer.write(data.decode())
	
	return path, baseurl

def download_hmm(path, baseurl):
	print("Downloading: vog.hmm.tar.gz")
	data = url.urlopen(f"{baseurl}/vog.hmm.tar.gz").read()
	data = gzip.decompress(data)
	with tar.open(fileobj=io.BytesIO(data)) as reader, gzip.open(path/"VOG.hmm.gz", "wb") as writer:
		print("Writing:", path/"VOG.hmm.gz")
		for file in reader:
			
			writer.write(reader.extractfile(file.name).read())
	return


def parse(path):
	vog_annot = Path(path, "vog-annotations.tsv")
	vog_cat = Path(path, "vogdb-functional_categories.txt")
	vog_onto = Path(path, "VOG.tsv")

	#GroupName	ProteinCount	SpeciesCount	FunctionalCategory	ConsensusFunctionalDescription

	vog_cat = vog_cat.read_text()
	with vog_annot.open() as reader, vog_onto.open('w') as writer:
		print("L1", "ID", "Function", "EC", "UNIPROT ID", sep='\t', file=writer)
		reader.readline() # Skip header
		for line in reader:
			ID,pcount,scount,CAT,NAME = line.strip('\n').split('\t')
			L1 = ""
			for i in range(0, len(CAT), 2):
				code = CAT[i:i+2]
				match = re.search(rf'\[{code}\] (.*)', vog_cat, re.MULTILINE)
				if match:
					L1 += f'{match.group(1)} | '
			L1 = L1.rstrip('| ')

			if NAME.startswith("REFSEQ"):
				UNIPROT = ""
				NAME = NAME.split(maxsplit=1)[-1]
			else:
				UNIPROT,NAME = NAME.split('|')[-1].split(maxsplit=1)

			NAME = NAME[0].upper() + NAME[1:]

			print(L1, ID, NAME, "", UNIPROT, sep='\t', file=writer)
	return


if __name__ == "__main__":
	main()
