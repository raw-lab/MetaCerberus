# -*- coding: utf-8 -*-

"""pipeline.py MetaCerberus module for processing the main pipeline jobs.
"""


import os
import re
from pathlib import Path
import time
import hydraMPP as hydra

from meta_cerberus import (
    metacerberus_qc, metacerberus_merge, metacerberus_trim, metacerberus_decon, metacerberus_formatFasta, metacerberus_metastats,
    metacerberus_genecall, metacerberus_hmm, metacerberus_parser,
    Chunker
)


# known file extensions
FILES_FASTQ = ['.fastq', '.fq']#, '.fastq.gz', '.fq.gz']
FILES_FASTA = [".fasta", ".fa", ".fna", ".ffn"]
FILES_AMINO = [".faa"]

# step names
STEP = {
    1:"step_01-loadFiles",
    2:"step_02-QC",
    3:"step_03-trim",
    4:"step_04-decontaminate",    
    5:"step_05-format",
    6:"step_06-metaomeQC",
    7:"step_07-geneCall",
    8:"step_08-hmmer",
    9:"step_09-parse",
    10:"step_10-visualizeData"}


def set_add(to_set:set, item, msg:str):
    if item not in to_set:
        to_set.add(item)
        print('\n', msg, '\n', sep='')
    return to_set

def logTime(dirout, host, funcName, path, timed):
    now = time.localtime()
    now = f"{now[3]:2}:{now[4]:2}:{now[5]:2}"
    with open(f'{dirout}/time.tsv', 'a+') as outTime:
        print(host, now, timed, funcName, path, file=outTime, sep='\t')
    return



def run_jobs(fastq, fasta, amino, rollup, config, outpath):
	# Main Pipeline
	pipeline = dict()
	step_curr = set()

	dbHMM = config['HMM']


	# Entry Point: Fastq
	if fastq:
		# Step 2 (check quality of fastq files)
		print("\nSTEP 2: Merging paired-end reads and checking quality of fastq files")
		# Merge Paired End Reads
		fastqPaired = dict()
		for ext in FILES_FASTQ:
			fastqPaired.update( {k:v for k,v in fastq.items() if "R1"+ext in v and v.replace("R1"+ext, "R2"+ext) in fastq.values() } )
		if len(fastqPaired) > 0 and not config['EXE_FLASH']:
			print('ERROR: FLASH is required for merging paired end FASTQ files.\nPlease install FLASH and edit the PATH variable or set the path in a config file')
			return None
		print("\nSTEP 3: Trimming fastq files")
		for key,value in fastqPaired.items():
			reverse = fastq.pop(key.replace("R1", "R2"))
			forward = fastq.pop(key)
			key = key.removesuffix("R1").rstrip('-_')
			# Check quality - paired end reads
			pipeline[metacerberus_qc.checkQuality.remote([forward,reverse], config['EXE_FASTQC'],
				f"{config['DIR_OUT']}/{STEP[2]}/{key}")] = key
			#TODO: quick fix, make parallel
			if not config['EXE_FASTP']:
				print("WARNING: Skipping paired end trimming, FASTP not found")
				r1 = value
				r2 = reverse
			else:
				r1,r2 = metacerberus_trim.trimPairedRead([key, [value,reverse]], config, Path(STEP[3], key))
			value = metacerberus_merge.mergePairedEnd([r1,r2], config, f"{STEP[3]}/{key}/merged")
			pipeline[hydra.put('trimSingleRead', value)] = key
		del fastqPaired # memory cleanup
		# Check quality - single end reads
		for key,value in fastq.items():
			pipeline[metacerberus_qc.checkQuality.remote(value, config['EXE_FASTQC'], f"{config['DIR_OUT']}/{STEP[2]}/{key}")] = key
		# Trim
		if config['NANOPORE'] and not config['EXE_PORECHOP']:
			print("WARNING: Skipping Nanopore trimming, PORECHOP not found")
			for key,value in fastq.items():
				pipeline[hydra.put("trimSingleRead", value)] = key
		elif not config['EXE_FASTP']:
			print("WARNING: Skipping single-end trimming, FASTP not found")
			for key,value in fastq.items():
				pipeline[hydra.put("trimSingleRead", value)] = key
		else:
			for key,value in fastq.items():
				pipeline[metacerberus_trim.trimSingleRead.remote([key, value], config, Path(STEP[3], key))] = key

	# Step 5 Contig Entry Point
	# Only do this if a fasta file was given, not if fastq
	if fasta:# and "scaffold" in config:
		if config['REMOVE_N_REPEATS']:
			print("\nSTEP 5a: Removing N's from contig files")
			for key,value in fasta.items():
				pipeline[metacerberus_formatFasta.removeN.remote(value, config, Path(STEP[5], key))] = key
		else:
			for key,value in fasta.items():
				pipeline[hydra.put("reformat", value)] = key


	# Step 8 Protein Entry Point
	groupORF = 0
	if amino:
		set_add(step_curr, 8, "STEP 8: HMMER Search")
		for key,value in amino.items():
			pipeline[hydra.put('findORF_', value)] = key
			groupORF += 1

	# Step 9 Rollup Entry Point
	hmm_tsv = dict()
	hmm_tsvs = dict()
	if rollup:
		set_add(step_curr, 8.5, "STEP 8: Filtering rollup file(s)")
		for key,value in rollup.items():
			amino[key] = None
			for hmm in dbHMM:
				tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, "filtered.tsv")
				pipeline[metacerberus_hmm.filterHMM.remote(value, tsv_filtered, dbHMM[hmm], config['REPLACE'])] = f"{hmm}/{key}"

	NStats = dict()
	readStats = dict()

	groupIndex = dict()
	dictChunks = dict()
	hmmRollup = {}
	hmmCounts = {}

	#TODO: Optimize this for PyHMMER, taking into account available CPUs/requested jobs
	jobs_hmmer = 4
	while pipeline:
		ready,queue = hydra.wait(pipeline, timeout=1)
		if not ready:
			continue
		key = pipeline.pop(ready[0])
		s,func,value,_,delay,hostname = hydra.get(ready[0])
		logTime(config['DIR_OUT'], hostname, func, key, delay)

		if func == "checkQuality":
			if value:
				name = key
				key = key.rstrip('_decon').rstrip('_trim')
				#os.makedirs(os.path.join(report_path, key), exist_ok=True)
				#shutil.copy(value, os.path.join(report_path, key, f"qc_{name}.html"))
		if func == "trimSingleRead":
			# Wait for Trimmed Reads
			fastq[key] = value
			pipeline[metacerberus_qc.checkQuality.remote(value, config['EXE_FASTQC'], f"{config['DIR_OUT']}/{STEP[3]}/{key}/quality")] = key+'_trim'
			if fastq and config['ILLUMINA']:
				if config['SKIP_DECON'] or not config['EXE_BBDUK']:
					if not config['EXE_BBDUK']:
						set_add(step_curr, "decon", "WARNING: Skipping decontamination, BBDUK not found")
					set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
					pipeline[metacerberus_formatFasta.reformat.remote(value, config, f"{STEP[5]}/{key}")] = key
				else:
					set_add(step_curr, 4, "STEP 4: Decontaminating trimmed files")
					pipeline[metacerberus_decon.deconSingleReads.remote([key, value], config, f"{STEP[4]}/{key}")] = key
			else:
				set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
				pipeline[metacerberus_formatFasta.reformat.remote(value, config, f"{STEP[5]}/{key}")] = key
		if func.startswith("decon"):
			fastq[key] = value
			set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
			pipeline[metacerberus_qc.checkQuality.remote(value, config['EXE_FASTQC'], f"{config['DIR_OUT']}/{STEP[4]}/{key}/quality")] = key+'_decon'
			pipeline[metacerberus_formatFasta.reformat.remote(value, config, f"{STEP[5]}/{key}")] = key
		if func == "removeN" or func == "reformat":
			if func == "removeN":
				fasta[key] = value[0]
				if value[1]:
					NStats[key] = value[1]
				set_add(step_curr, 6, "STEP 6: Metaome Stats")
				readStats[key] = metacerberus_metastats.getReadStats(value[0], config, Path(STEP[6], key))
			elif func == "reformat":
				fasta[key] = value
			set_add(step_curr, 7, "STEP 7: ORF Finder")
			if key.startswith("FragGeneScan_"):
				pipeline[metacerberus_genecall.findORF_fgs.remote(fasta[key], config, f"{STEP[7]}/{key}")] = key
			elif key.startswith("prodigalgv_"):
				pipeline[metacerberus_genecall.findORF_prod.remote(fasta[key], config, f"{STEP[7]}/{key}", config['META'], True)] = key
			elif key.startswith("prodigal_"):
				pipeline[metacerberus_genecall.findORF_prod.remote(fasta[key], config, f"{STEP[7]}/{key}", config['META'])] = key
			elif key.startswith("phanotate_"):
				pipeline[metacerberus_genecall.findORF_phanotate.remote(fasta[key], config, f"{STEP[7]}/{key}", config['META'])] = key
			groupORF += 1
		if func.startswith("findORF_"):
			if not value:
				print("ERROR: error from ORF caller")
				continue
			# fail if amino file is empty
			if Path(value).stat().st_size == 0:
				print("ERROR: no ORFs found in:", key, value)
				continue
			#TODO: Check for duplicate headers in amino acids
			#      This causes an issue with the GFF and summary files
			if config['GROUPED']:
				amino[key] = value
				groupORF -= 1
				if not Path(config['DIR_OUT'], 'grouped').exists():
					Path(config['DIR_OUT'], 'grouped').mkdir(parents=True, exist_ok=True)
				outfile = Path(config['DIR_OUT'], 'grouped', 'grouped.faa')
				Path(config['DIR_OUT'], STEP[8], key).mkdir(parents=True, exist_ok=True)
				with outfile.open('a') as writer, Path(value).open() as reader:
					for line in reader:
						writer.write(line)
						if line.startswith('>'):
							name = line[1:].rstrip().split()[0]
							if name in groupIndex:
								print("WARN: Duplicate header:", name)
							groupIndex[name] = key
				if groupORF > 0:
					continue #Continue until all ORFs are done
				value = outfile
				key = "grouped"
			set_add(step_curr, 8, "STEP 8: HMMER Search")
			amino[key] = value
			if config['CHUNKER'] > 0:
				chunks = Chunker.create_chunks(amino[key], Path(config['DIR_OUT'], 'chunks', key), f"{config['CHUNKER']}M", '>')
				for hmm in dbHMM.items():
					if hmm[0].endswith("FOAM"):
						continue
					outfile = Path(config['DIR_OUT'], STEP[8], key, f'{hmm[0]}-{key}.tsv')
					if not config['REPLACE'] and outfile.exists():
						pipeline[hydra.put("searchHMM", [str(outfile)])] = [f"{hmm[0]}/{key}"]
						continue
					chunkCount = 1
					for chunk in chunks:
						key_chunk = f'chunk-{hmm[0]}-{chunkCount}-{len(chunks)}_{key}'
						key_name = f'chunk-{chunkCount}-{len(chunks)}_{key}'
						chunkCount += 1
						pipeline[metacerberus_hmm.searchHMM.options(num_cpus=jobs_hmmer).remote(
												{key_name:chunk}, config, Path(STEP[8], key), hmm, 4)] = [key_chunk]
			else: # Chunker not enabled
				for hmm in dbHMM.items():
					if hmm[0].endswith("FOAM"):
						continue
					outfile = Path(config['DIR_OUT'], STEP[8], key, f'{hmm[0]}-{key}.tsv')
					if not config['REPLACE'] and outfile.exists():
						pipeline[hydra.put("searchHMM", [str(outfile)])] = [f"{hmm[0]}/{key}"]
						continue
					hmm_key = f"{hmm[0]}/{key}"
					pipeline[metacerberus_hmm.searchHMM.options(num_cpus=jobs_hmmer).remote(
															{key:value}, config, Path(STEP[8]), hmm, 4)] = [hmm_key]
		if func.startswith('searchHMM'):
			#TODO: This whole section needs reworking to remove redundant code, and improve grouped option
			if value is None:
				print("Error with hmmsearch")
				continue
			keys = key
			for key,tsv_file in zip(keys,value):
				match = re.search(r"^chunk-([A-Za-z_]+)-(\d+)-(\d+)_(.+)", key)
				if match: # Matches if the keys are part of chunks
					hmm,i,l,key = match.groups()
					hmm_key = f"{hmm}-{key}"
					if hmm_key not in dictChunks:
						dictChunks[hmm_key] = list()
					dictChunks[hmm_key].append(tsv_file)
					if len(dictChunks[hmm_key]) == int(l):
						# All chunks of a file have returned
						if config['GROUPED']:
							key_set = set()
							# Split the grouped file into their own hmm_tsv files
							for item in sorted(dictChunks[hmm_key]):
								with open(item) as reader:
									for line in reader:
										name = line.split()[0]
										k = groupIndex[name]
										key_set.add(k)
										tsv_out = Path(config['DIR_OUT'], STEP[8], k, f"{hmm}-{k}.tsv")
										with tsv_out.open('a') as writer:
											writer.write(line)
										if re.search(r'KEGG', str(tsv_out)):
											tsv_out_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_out)))
											with tsv_out_foam.open('a') as writer:
												writer.write(line)
								dictChunks[hmm_key].remove(item)
								if not config['KEEP']:
									os.remove(item)
							set_add(step_curr, 8.1, "STEP 8: Filtering HMMER results")
							#TODO: Still need to add FOAM filtering for grouped option
							for k in key_set:
								tsv_out = Path(config['DIR_OUT'], STEP[8], k, f"{hmm}-{k}.tsv")
								tsv_filtered = Path(config['DIR_OUT'], STEP[8], k, f"filtered-{hmm}.tsv")
								pipeline[metacerberus_hmm.filterHMM.remote(tsv_out, tsv_filtered, dbHMM[hmm], config['REPLACE'])] = f"{hmm}/{k}"
								if re.search(r'KEGG', str(tsv_out)):
									hmm_foam = re.sub(r'KEGG', 'FOAM', hmm)
									tsv_out_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_out)))
									tsv_filtered_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_filtered)))
									pipeline[metacerberus_hmm.filterHMM.remote(tsv_out_foam, tsv_filtered_foam, dbHMM[hmm_foam], config['REPLACE'])] = f"{hmm_foam}/{k}"
							# FINISH SPLITTING GROUP
							continue
						# Not grouped
						tsv_out = Path(config['DIR_OUT'], STEP[8], key, f"{hmm}-{key}.tsv")
						tsv_out.parent.mkdir(parents=True, exist_ok=True)
						if re.search(r'KEGG', str(tsv_out)):
							tsv_out_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_out)))
							writer_foam = tsv_out_foam.open('w')
						with tsv_out.open('w') as writer:
							for item in sorted(dictChunks[hmm_key]):
								if re.search(r'KEGG', str(tsv_out)):
									writer_foam.write(open(item).read())
								writer.write(open(item).read())
								dictChunks[hmm_key].remove(item)
								if not config['KEEP']:
									os.remove(item)
						tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, f"filtered-{hmm}.tsv")
						set_add(step_curr, 8.1, "STEP 8: Filtering HMMER results")
						pipeline[metacerberus_hmm.filterHMM.remote(tsv_out, tsv_filtered, dbHMM[hmm], config['REPLACE'])] = f"{hmm}/{key}"
						if re.search(r'KEGG', str(tsv_out)):
							writer_foam.close()
							hmm_foam = re.sub(r'KEGG', 'FOAM', hmm)
							tsv_filtered_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_filtered)))
							pipeline[metacerberus_hmm.filterHMM.remote(tsv_out_foam, tsv_filtered_foam, dbHMM[hmm_foam], config['REPLACE'])] = f"{hmm_foam}/{key}"
				else:
				# Not chunked file
					hmm,key = key.split(sep='/', maxsplit=1)
					tsv_out = Path(config['DIR_OUT'], STEP[8], key, f"{hmm}-{key}.tsv")
					#TODO: This becomes a bottleneck with a large amount of samples. This begins when hmm/filtering ends, and becomes linear. Large memory holding all the jobs in queue
					if not tsv_out.exists() or not tsv_out.samefile(Path(tsv_out)):
						with tsv_out.open('w') as writer:
							writer.write(open(tsv_file).read())
						if not config['KEEP']:
								os.remove(tsv_file)
					if re.search(r'KEGG', str(tsv_out)):
						tsv_out_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_out)))
						with tsv_out_foam.open('w') as writer:
							writer.write(open(tsv_out).read())
					set_add(step_curr, 8.1, "STEP 8: Filtering HMMER results")
					tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, f"filtered-{hmm}.tsv")
					pipeline[metacerberus_hmm.filterHMM.remote(tsv_out, tsv_filtered, dbHMM[hmm], config['REPLACE'])] = f"{hmm}/{key}"
					if re.search(r'KEGG', str(tsv_out)):
						hmm_foam = re.sub(r'KEGG', 'FOAM', hmm)
						tsv_filtered_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_filtered)))
						pipeline[metacerberus_hmm.filterHMM.remote(tsv_out_foam, tsv_filtered_foam, dbHMM[hmm_foam], config['REPLACE'])] = f"{hmm_foam}/{key}"
		if func.startswith('filterHMM'):
			hmm,key = key.split('/')
			set_add(step_curr, 9, "STEP 9: Parse HMMER results")
			pipeline[metacerberus_parser.parseHmmer.remote(value, config, Path(config['DIR_OUT'], STEP[9], key), hmm, dbHMM[hmm])] = key

			#TODO: This becomes a bottleneck with a large amount of samples. This begins when hmm/filtering ends, and becomes linear.. Large memory holding all the jobs in queue
			tsv_filtered = Path(config['DIR_OUT'], STEP[8], key, "filtered.tsv")
			if key not in hmm_tsvs:
				hmm_tsvs[key] = dict()
				with tsv_filtered.open('w') as writer:
					print("target", "query", "e-value", "score", "length", "start", "end", "hmmDB", sep='\t', file=writer)
			if hmm not in hmm_tsvs[key]:
				hmm_tsvs[key][hmm] = value
			with tsv_filtered.open('a') as writer, open(value) as reader:
				reader.readline() # Skip header
				for line in reader:
					print(*line.rstrip('\n').split('\t'), hmm, sep='\t', file=writer)
			if len(hmm_tsvs[key]) == len(dbHMM):
				hmm_tsv[key] = tsv_filtered
				outfile = Path(config['DIR_OUT'], STEP[9], key, f"top_5.tsv")
				pipeline[metacerberus_parser.top5.remote(tsv_filtered, outfile)] = key
		if func.startswith('parseHmmer'):
			if not value:
				print("Warning: no hmm results from:", key)
			if key not in hmmRollup:
				hmmRollup[key] = dict()
			hmmRollup[key].update(value)
			pipeline[metacerberus_parser.createCountTables.remote(value, config, f"{STEP[9]}/{key}")] = key
		if func.startswith('createCountTables'):
			if key not in hmmCounts:
				hmmCounts[key] = dict()
			hmmCounts[key].update(value)

	# End main pipeline
	return fastq, fasta, amino, rollup, hmm_tsv, hmm_tsvs, hmmRollup, hmmCounts, readStats, NStats
