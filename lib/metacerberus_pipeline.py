# -*- coding: utf-8 -*-

"""pipeline.py MetaCerberus module for processing the main pipeline jobs.
"""


import os
import re
import shutil
import subprocess
import urllib.request as request
from pathlib import Path
import time
import hydraMPP as hydra

from meta_cerberus import (
	metacerberus_qc, metacerberus_merge, metacerberus_trim, metacerberus_decon, metacerberus_formatFasta, metacerberus_metastats,
	metacerberus_genecall, metacerberus_hmm, metacerberus_parser,
	metacerberus_prostats, metacerberus_visual, metacerberus_report, Chunker
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

	outpath = Path(outpath)
	outpath.mkdir(parents=True, exist_ok=True)

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
				Path(outpath, STEP[2], key))] = key
			#TODO: quick fix, make parallel
			if not config['EXE_FASTP']:
				print("WARNING: Skipping paired end trimming, FASTP not found")
				r1 = value
				r2 = reverse
			else:
				r1,r2 = metacerberus_trim.trimPairedRead([key, [value,reverse]], config, Path(outpath, STEP[3], key))
			value = metacerberus_merge.mergePairedEnd([r1,r2], config, Path(outpath, STEP[3], key, "merged"))
			pipeline[hydra.put('trimSingleRead', value)] = key
		del fastqPaired # memory cleanup
		# Check quality - single end reads
		for key,value in fastq.items():
			pipeline[metacerberus_qc.checkQuality.remote(value, config['EXE_FASTQC'], Path(outpath, STEP[2], key))] = key
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
				pipeline[metacerberus_trim.trimSingleRead.remote([key, value], config, Path(outpath, STEP[3], key))] = key

	# Step 5 Contig Entry Point
	# Only do this if a fasta file was given, not if fastq
	if fasta:# and "scaffold" in config:
		if config['REMOVE_N_REPEATS']:
			print("\nSTEP 5a: Removing N's from contig files")
			for key,value in fasta.items():
				pipeline[metacerberus_formatFasta.removeN.remote(value, Path(outpath, STEP[5], key), config['REPLACE'])] = key
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
				tsv_filtered = Path(outpath, STEP[8], key, "filtered.tsv")
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
		logTime(outpath, hostname, func, key, delay)

		if func == "checkQuality":
			if value:
				name = key
				key = key.rstrip('_decon').rstrip('_trim')
				#os.makedirs(os.path.join(report_path, key), exist_ok=True)
				#shutil.copy(value, os.path.join(report_path, key, f"qc_{name}.html"))
		if func == "trimSingleRead":
			# Wait for Trimmed Reads
			fastq[key] = value
			pipeline[metacerberus_qc.checkQuality.remote(value, config['EXE_FASTQC'], Path(outpath, STEP[3], key, "quality"))] = key+'_trim'
			if fastq and config['ILLUMINA']:
				if config['SKIP_DECON'] or not config['EXE_BBDUK']:
					if not config['EXE_BBDUK']:
						set_add(step_curr, "decon", "WARNING: Skipping decontamination, BBDUK not found")
					set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
					pipeline[metacerberus_formatFasta.reformat.remote(value, Path(outpath, STEP[5], key), config['REPLACE'])] = key
				else:
					set_add(step_curr, 4, "STEP 4: Decontaminating trimmed files")
					pipeline[metacerberus_decon.deconSingleReads.remote([key, value], config, Path(outpath, STEP[4], key))] = key
			else:
				set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
				pipeline[metacerberus_formatFasta.reformat.remote(value, Path(outpath, STEP[5], key), config['REPLACE'])] = key
		if func.startswith("decon"):
			fastq[key] = value
			set_add(step_curr, 5.2, "STEP 5b: Reformating FASTQ files to FASTA format")
			pipeline[metacerberus_qc.checkQuality.remote(value, config['EXE_FASTQC'], Path(outpath, STEP[4], key, "quality"))] = key+'_decon'
			pipeline[metacerberus_formatFasta.reformat.remote(value, Path(outpath, STEP[5], key))] = key
		if func == "removeN" or func == "reformat":
			if func == "removeN":
				fasta[key] = value[0]
				if value[1]:
					NStats[key] = value[1]
				set_add(step_curr, 6, "STEP 6: Metaome Stats")
				readStats[key] = metacerberus_metastats.getReadStats(value[0], config, Path(outpath, STEP[6], key))
			elif func == "reformat":
				fasta[key] = value
			set_add(step_curr, 7, "STEP 7: ORF Finder")
			if key.startswith("FragGeneScan_"):
				pipeline[metacerberus_genecall.findORF_fgs.remote(fasta[key], config, Path(outpath, STEP[7], key))] = key
			elif key.startswith("prodigalgv_"):
				pipeline[metacerberus_genecall.findORF_prod.remote(fasta[key], config, Path(outpath, STEP[7], key), config['META'], True)] = key
			elif key.startswith("prodigal_"):
				pipeline[metacerberus_genecall.findORF_prod.remote(fasta[key], config, Path(outpath, STEP[7], key), config['META'])] = key
			elif key.startswith("phanotate_"):
				pipeline[metacerberus_genecall.findORF_phanotate.remote(fasta[key], config, Path(outpath, STEP[7], key), config['META'])] = key
			groupORF += 1
		if func.startswith("findORF_"):
			if not value:
				print("ERROR: error from ORF caller")
				continue
			# fail if amino file is empty
			if Path(value).stat().st_size == 0:
				print("WARNING: no ORFs found in:", key, value)
				continue
			#TODO: Check for duplicate headers in amino acids
			#      This causes an issue with the GFF and summary files
			if config['GROUPED']:
				#TODO: Remove GROUPED option?
				amino[key] = value
				groupORF -= 1
				if not Path(outpath, 'grouped').exists():
					Path(outpath, 'grouped').mkdir(parents=True, exist_ok=True)
				outfile = Path(outpath, 'grouped', 'grouped.faa')
				Path(outpath, STEP[8], key).mkdir(parents=True, exist_ok=True)
				with outfile.open('a') as writer, Path(value).open() as reader:
					for line in reader:
						writer.write(line)
						if line.startswith('>'):
							name = line[1:].rstrip().split()[0]
							if name in groupIndex:
								print("WARNING: Duplicate header:", name)
							groupIndex[name] = key
				if groupORF > 0:
					continue #Continue until all ORFs are done
				value = outfile
				key = "grouped"
			set_add(step_curr, 8, "STEP 8: HMMER Search")
			amino[key] = value
			if config['CHUNKER'] > 0:
				chunks = Chunker.create_chunks(amino[key], Path(outpath, 'chunks', key), f"{config['CHUNKER']}M", '>')
				for hmm in dbHMM.items():
					if hmm[0].endswith("FOAM"):
						continue
					outfile = Path(outpath, STEP[8], key, f'{hmm[0]}-{key}.tsv')
					if not config['REPLACE'] and outfile.exists():
						pipeline[hydra.put("searchHMM", [str(outfile)])] = [f"{hmm[0]}/{key}"]
						continue
					chunkCount = 1
					for chunk in chunks:
						key_chunk = f'chunk-{hmm[0]}-{chunkCount}-{len(chunks)}_{key}'
						key_name = f'chunk-{chunkCount}-{len(chunks)}_{key}'
						chunkCount += 1
						pipeline[metacerberus_hmm.searchHMM.options(num_cpus=jobs_hmmer).remote(
												{key_name:chunk}, config, Path(outpath, STEP[8], key), hmm, 4)] = [key_chunk]
			else: # Chunker not enabled
				for hmm in dbHMM.items():
					if hmm[0].endswith("FOAM"):
						continue
					outfile = Path(outpath, STEP[8], key, f'{hmm[0]}-{key}.tsv')
					if not config['REPLACE'] and outfile.exists():
						pipeline[hydra.put("searchHMM", [str(outfile)])] = [f"{hmm[0]}/{key}"]
						continue
					hmm_key = f"{hmm[0]}/{key}"
					pipeline[metacerberus_hmm.searchHMM.options(num_cpus=jobs_hmmer).remote(
															{key:value}, config, Path(outpath, STEP[8]), hmm, 4)] = [hmm_key]
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
										tsv_out = Path(outpath, STEP[8], k, f"{hmm}-{k}.tsv")
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
								tsv_out = Path(outpath, STEP[8], k, f"{hmm}-{k}.tsv")
								tsv_filtered = Path(outpath, STEP[8], k, f"filtered-{hmm}.tsv")
								pipeline[metacerberus_hmm.filterHMM.remote(tsv_out, tsv_filtered, dbHMM[hmm], config['REPLACE'])] = f"{hmm}/{k}"
								if re.search(r'KEGG', str(tsv_out)):
									hmm_foam = re.sub(r'KEGG', 'FOAM', hmm)
									tsv_out_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_out)))
									tsv_filtered_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_filtered)))
									pipeline[metacerberus_hmm.filterHMM.remote(tsv_out_foam, tsv_filtered_foam, dbHMM[hmm_foam], config['REPLACE'])] = f"{hmm_foam}/{k}"
							# FINISH SPLITTING GROUP
							continue
						# Not grouped
						tsv_out = Path(outpath, STEP[8], key, f"{hmm}-{key}.tsv")
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
						tsv_filtered = Path(outpath, STEP[8], key, f"filtered-{hmm}.tsv")
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
					tsv_out = Path(outpath, STEP[8], key, f"{hmm}-{key}.tsv")
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
					tsv_filtered = Path(outpath, STEP[8], key, f"filtered-{hmm}.tsv")
					pipeline[metacerberus_hmm.filterHMM.remote(tsv_out, tsv_filtered, dbHMM[hmm], config['REPLACE'])] = f"{hmm}/{key}"
					if re.search(r'KEGG', str(tsv_out)):
						hmm_foam = re.sub(r'KEGG', 'FOAM', hmm)
						tsv_filtered_foam = Path(re.sub(r'KEGG', 'FOAM', str(tsv_filtered)))
						pipeline[metacerberus_hmm.filterHMM.remote(tsv_out_foam, tsv_filtered_foam, dbHMM[hmm_foam], config['REPLACE'])] = f"{hmm_foam}/{key}"
		if func.startswith('filterHMM'):
			hmm,key = key.split('/')
			set_add(step_curr, 9, "STEP 9: Parse HMMER results")
			pipeline[metacerberus_parser.parseHmmer.remote(value, config, Path(outpath, STEP[9], key), hmm, dbHMM[hmm])] = key

			#TODO: This becomes a bottleneck with a large amount of samples. This begins when hmm/filtering ends, and becomes linear.. Large memory holding all the jobs in queue
			tsv_filtered = Path(outpath, STEP[8], key, "filtered.tsv")
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
				outfile = Path(outpath, STEP[9], key, f"top_5.tsv")
				pipeline[metacerberus_parser.top5.remote(tsv_filtered, outfile)] = key
		if func.startswith('parseHmmer'):
			if not value:
				print("WARNING: no hmm results from:", key)
			if key not in hmmRollup:
				hmmRollup[key] = dict()
			hmmRollup[key].update(value)
			pipeline[metacerberus_parser.createCountTables.remote(value, Path(outpath, STEP[9], key), config['REPLACE'])] = key
		if func.startswith('createCountTables'):
			if key not in hmmCounts:
				hmmCounts[key] = dict()
			hmmCounts[key].update(value)

	# End main pipeline
	return fastq, fasta, amino, rollup, hmm_tsv, hmm_tsvs, hmmRollup, hmmCounts, readStats, NStats

def report(outpath, config, dbHMM, fasta, amino, hmm_tsv, hmm_tsvs, hmmRollup, hmmCounts, readStats, NStats):

	report_path = Path(outpath, STEP[10])
	final_path = Path(outpath, "final")

	# Copy report files from QC, Parser
	Path(final_path, "top-5").mkdir(parents=True, exist_ok=True)
	Path(final_path, "rollup").mkdir(parents=True, exist_ok=True)
	Path(final_path, "counts").mkdir(parents=True, exist_ok=True)
	Path(final_path, "gff").mkdir(parents=True, exist_ok=True)
	Path(final_path, "genbank").mkdir(parents=True, exist_ok=True)
	for key in hmm_tsvs.keys():
		Path(final_path, f"annotations-{key}").mkdir(parents=True, exist_ok=True)
		Path(report_path, key).mkdir(parents=True, exist_ok=True)
		for value in hmmRollup[key].values():
			parse_path = Path(value).parent
			break
		top_5s = parse_path.glob("top_5*.tsv")
		for src in top_5s:
			#src = os.path.join(config['DIR_OUT'], config['STEP'][9], key, "top_5.tsv")
			dst = Path(final_path, "top-5", f"{key}-{src.name}")
			shutil.copy(src, dst)
		try:
			src = Path(fasta[key])
			dst = Path(final_path, "fasta", f"{key}.fna")
			shutil.copy(src, dst)
		except: pass
		try:
			src = Path(amino[key]).with_suffix(".ffn")
			dst = Path(final_path, "fasta", f"{key}.ffn")
			shutil.copy(src, dst)
		except: pass

	# Write Stats
	jobStat = dict()
	Path(final_path, "fasta").mkdir(0o777, True, True)
	print("Creating final reports and statistics\n")


	print("Protein stats")
	protStats = {}
	for key in hmm_tsvs.keys():
		# Protein statistics & annotation summary
		summary_tsv = Path(final_path, f"annotations-{key}", 'final_annotation_summary.tsv')
		jobStat[metacerberus_prostats.getStats.remote(amino[key], hmm_tsvs[key], hmmCounts[key], config['MINSCORE'], dbHMM, summary_tsv, Path(final_path, "fasta", f"{key}.faa"))] = key
	while jobStat:
		ready,queue = hydra.wait(jobStat)
		key = jobStat.pop(ready[0])
		s,func,value,_,delay,hostname = hydra.get(ready[0])
		logTime(outpath, hostname, func, key, delay)
		protStats[key] = value

	print("Creating GFF and Genbank files")
	for key in hmm_tsvs.keys():
		# Create GFFs #TODO: Incorporate this into getStats (or separate all summary into new module)
		summary_tsv = Path(final_path, f"annotations-{key}", 'final_annotation_summary.tsv')
		amino_path = Path(amino[key]).parent
		gff = [x for x in amino_path.glob("*.gff")]
		if len(gff) == 1:
			out_gff = Path(final_path, "gff", f"{key}.gff")
			out_genbank = Path(final_path, "genbank", f"{key}_template.gbk")
			jobStat[metacerberus_report.write_datafiles.remote(gff[0], fasta[key], amino[key], summary_tsv, out_gff, out_genbank)] = None
		else:
			out_gff = Path(final_path, "gff", f"{key}.gff")
			with out_gff.open('w') as writer:
				with summary_tsv.open() as read_summary:
					read_summary.readline()
					print("##gff-version  3", file=writer)
					for summ in read_summary:
						summ = summ.split('\t')
						data = [summ[0].split('_')[0], ".", ".", ".", ".", ".", ".", ".", ]
						attributes = ';'.join([f"ID={summ[0]}", f"Name={summ[1]}", f"Alias={summ[2]}", f"Dbxref={summ[3]}", f"evalue={summ[4]}", f"product_start={summ[8]}", f"product_end={summ[9]}", f"product_length={summ[10]}"])
						print(*data, attributes, sep='\t', file=writer)
				try:
					with open(fasta[key]) as read_fasta:
						print("##FASTA", file=writer)
						for line in read_fasta:
							writer.write(line)
				except: pass
	while jobStat:
		ready,queue = hydra.wait(jobStat)
		jobStat.pop(ready[0])
		s,func,value,_,delay,hostname = hydra.get(ready[0])
		logTime(outpath, hostname, func, key, delay)

	metacerberus_report.write_Stats(report_path, readStats, protStats, NStats, config)
	del protStats

	# Write Roll-up Tables
	print("Creating Rollup Tables")
	for sample,tables in hmmCounts.items():
		os.makedirs(f"{report_path}/{sample}", exist_ok=True)
		for name,table in tables.items():
			metacerberus_report.writeTables(table, f"{report_path}/{sample}/{name}")
	for sample,tables in hmmRollup.items():
		os.makedirs(f"{report_path}/{sample}", exist_ok=True)
		for name,table in tables.items():
			shutil.copy(table, Path(final_path, "rollup", f'rollup_{sample}-{name}.tsv'))

	# Counts Tables
	print("Mergeing Count Tables")
	dfCounts = dict()
	for dbname,dbpath in dbHMM.items():
		tsv_list = dict()
		for name in hmm_tsv.keys():
			if dbname.startswith("KOFam"):
				dbLookup = re.search(r"KOFam_.*_([A-Z]+)", dbname).group(1)
				dbLookup = dbpath.with_name(f'{dbLookup}.tsv')
			for value in hmmCounts[name].values():
				parse_path = Path(value).parent
				break
			table_path = Path(parse_path, f'counts_{dbname}.tsv')
			if table_path.exists():
				name = re.sub(rf'^FragGeneScan_|prodigal_|Protein_', '', name)
				tsv_list[name] = table_path
		combined_path = Path(final_path, "counts", f'counts_{dbname}.tsv')
		metacerberus_parser.merge_tsv(tsv_list, Path(combined_path))
		if combined_path.exists():
			dfCounts[dbname] = combined_path
		del(combined_path)

	# PCA output (HTML)
	pcaFigures = None
	if config['SKIP_PCA']:
		pass
	elif len(hmm_tsv) < 4:
		print("NOTE: PCA Tables created only when there are at least four sequence files.\n")
	else:
		print("PCA Analysis")
		pcaFigures = metacerberus_visual.graphPCA.remote(dfCounts)
		ready,pending = hydra.wait([pcaFigures])
		s,func,value,_,delay,hostname = hydra.get(ready[0])
		logTime(outpath, hostname, func, "PCA", delay)
		pcaFigures = value
		Path(report_path, 'combined').mkdir(parents=True, exist_ok=True)
		metacerberus_report.write_PCA(os.path.join(report_path, "combined"), pcaFigures)

	# Run post processing analysis in R
	if not [True for x in dfCounts if x.startswith("KOFam")]:
		print("NOTE: Pathview created only when KOFams are used since it uses KOs for its analysis.\n")
	elif len(hmm_tsv) < 4 or not config['CLASS']:
		print("NOTE: Pathview created only when there are at least four sequence files, and a class tsv file is specified with --class specifying the class for each input file.\n")
	else:
		print("\nSTEP 11: Post Analysis with GAGE and Pathview")
		outpathview = Path(report_path, 'pathview')
		outpathview.mkdir(exist_ok=True, parents=True)
		rscript = Path(outpathview, 'run_pathview.sh')

		# Check for internet
		try:
			#attempt to connect to Google
			request.urlopen('http://216.58.195.142', timeout=1)
			is_internet = True
		except:
			is_internet = False
		
		with rscript.open('w') as writer:
			writer.write(f"#!/bin/bash\n\n")
			for name,countpath in dfCounts.items():
				if not name.startswith("KOFam"):
					continue
				shutil.copy(countpath, Path(outpathview, f"{name}_counts.tsv"))
				shutil.copy(config['CLASS'], Path(outpathview, f"{name}_class.tsv"))
				writer.write(f"mkdir -p {name}\n")
				writer.write(f"cd {name}\n")
				writer.write(f"pathview-metacerberus.R ../{name}_counts.tsv ../{name}_class.tsv\n")
				writer.write(f"cd ..\n")
				outcmd = Path(outpathview, name)
				outcmd.mkdir(parents=True, exist_ok=True)
				if is_internet:
					subprocess.run(['pathview-metacerberus.R', countpath, config['CLASS']],
									cwd=outcmd,
									stdout=Path(outcmd, 'stdout.txt').open('w'),
									stderr=Path(outcmd, 'stderr.txt').open('w')
								)
		if not is_internet:
			print(f"GAGE and Pathview require internet access to run. Run the script '{rscript}'")

	# Figure outputs (HTML)
	print("Creating combined sunburst and bargraphs")
	figSunburst = {}
	for key,value in hmmCounts.items():
		figSunburst[key] = metacerberus_visual.graphSunburst(value)

	jobCharts = dict()
	for key,value in hmmRollup.items():
		jobCharts[metacerberus_visual.graphBarcharts.remote(value, hmmCounts[key])] = key

	figCharts = {}
	while(jobCharts):
		ready,queue = hydra.wait(jobCharts)
		if ready:
			key = jobCharts.pop(ready[0])
			s,func,value,cpus,delay,hostname = hydra.get(ready[0])
			figCharts[key] = value
			logTime(outpath, hostname, func, key, delay)


	metacerberus_report.createReport(figSunburst, figCharts, Path(outpath, STEP[10]))

	return
