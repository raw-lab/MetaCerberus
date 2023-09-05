#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from plot_header import colors


TEST_NAME = "virome"
OUTPATH = Path(f"plots-{TEST_NAME}")
TOOLS = ['DRAM', 'Metacerberus']
SAMPLES = ['META_VIRAL'] # ['VIRAL_METAGENOME'] # 
PREFIX =  'individual' # 'together' #

def main():
	#results/Metacerberus/GTDB-100/genomes/archaea/GCA_021792045.1/step_10-visualizeData/prodigal_GCA_021792045.1/annotation_summary.tsv
	#Metacerberus GTDB-100 GCA_021792045.1/step_10-visualizeData/prodigal_GCA_021792045.1/annotation_summary.tsv
	#results/Metacerberus/GTDB-100/genomes/bacteria/GCF_001968815.1/step_10-visualizeData/prodigal_GCF_001968815.1/annotation_summary.tsv
	#Metacerberus GTDB-100 GCF_001968815.1/step_10-visualizeData/prodigal_GCF_001968815.1/annotation_summary.tsv
	re_gtdb = re.compile(r'^results\/([A-Za-z_]+)\/([A-Za-z0-9-_]+)\/genomes\/([A-Za-z]+)\/([A-Za-z0-9_.]+)\/.+$')
	re_file = re.compile(r'^results\/([A-Za-z_]+)\/([A-Za-z0-9-_]+)\/genomes\/([A-Za-z0-9_.]+)\/.+$')
	re_hypothetical = re.compile(r'([Hh]ypothetical)', re.IGNORECASE)

	dfAnnotate = dict()
	dfEvalue = dict()
	dfEval = pd.DataFrame()

	# Gather data
	file_list = Path("results").rglob('*.tsv')
	tools = set()
	for filepath in sorted(file_list):
		match_GTDB = re_gtdb.search(str(filepath))
		match_other = re_file.search(str(filepath))
		if match_GTDB:
			tool,sample_type,subtype,sample = match_GTDB.groups()
			sample_type = sample_type.rstrip("-100") + '-' + subtype
		elif match_other:
			tool,sample_type,sample = match_other.groups()
		else:
			print("ERROR:", tool, filepath)
			continue

		#print(tool, sample_type, sample, subpath)
		if tool not in TOOLS:
			continue
		tools.add(tool)

		if sample_type not in SAMPLES:
			continue

		if sample_type not in dfAnnotate:
			dfAnnotate[sample_type] = pd.DataFrame()
			dfEvalue[sample_type] = pd.DataFrame()
		with filepath.open() as reader:
			ORFs = dict()
			KOs = dict()
			VOGs = dict()
			CAZYs = dict()
			EVals = dict()
			header = reader.readline().rstrip('\n').split('\t')
			indexes = dict()
			if tool == "DRAM":
				for i,label in enumerate(header):
					if label in ['ko_id', 'viral_id', 'vogdb_id', 'cazy_ids', 'peptidase_id', 'pfam_hits']:
						indexes[label] = i
			try:
				for line in reader:
					line = line.rstrip('\n').split('\t')
					if line[0] not in ORFs:
						ORFs[line[0]] = 0
						KOs[line[0]] = 0
						VOGs[line[0]] = 0
						CAZYs[line[0]] = 0
					if tool.startswith('DRAM'):
						if list(filter(re_hypothetical.search, line)):
							ORFs[line[0]] |= 2
						elif sum([len(line[x]) for x in indexes.values()]) > 0:
							ORFs[line[0]] |= 4
						# id counts
						if 'ko_id' in indexes and line[indexes['ko_id']].startswith('K'):
							KOs[line[0]] += 1
						if 'vogdb_id' in indexes and len(line[indexes['vogdb_id']]):
							VOGs[line[0]] += 1
						if 'cazy_ids' in indexes and len(line[indexes['cazy_ids']]):
							CAZYs[line[0]] += 1
					if tool.startswith('Metacerberus'):
						if line[12] == "Hypothetical":
							ORFs[line[0]] |= 2
						elif float(line[9]) < 1e-15 and float(line[10]) >= 60:
							ORFs[line[0]] |= 4
							dfEval.at[sample, 'sample_type'] = sample_type
							dfEval.at[sample, 'tool'] = tool
							dfEval.at[sample, 'evalue'] = line[9]
							# id counts
							if len(line[2]): #KO
								KOs[line[0]] += 1
							if len(line[6]): #VOG
								VOGs[line[0]] += 1
							if len(line[4]): #CAZy
								CAZYs[line[0]] += 1
				# Store stats in dictionary
				annotated = 0
				hypothetical = 0
				unknown = 0

				for state in ORFs.values():
					if state & 4:
						annotated += 1
					elif state & 2:
						hypothetical += 1
					else:
						unknown += 1
				dfAnnotate[sample_type].at[sample, f'{tool}-ORF_count'] = len(ORFs)
				dfAnnotate[sample_type].at[sample, f'{tool}-Annotated'] = annotated
				dfAnnotate[sample_type].at[sample, f'{tool}-Hypothetical'] = hypothetical
				dfAnnotate[sample_type].at[sample, f'{tool}-Unknown'] = unknown
				if tool.startswith('DRAM') or tool.startswith('Metacerberus'):
					count = sum(KOs.values())
					dfAnnotate[sample_type].at[sample, f'{tool}-KO_count'] = count
					count = sum(VOGs.values())
					dfAnnotate[sample_type].at[sample, f'{tool}-VOG_count'] = count
					count = sum(CAZYs.values())
					dfAnnotate[sample_type].at[sample, f'{tool}-CAZy_count'] = count
				# Evalue
				#dfEval.at[sample, 'sample_type'] = sample_type
				#dfEval.at[sample, 'tool'] = tool
				#dfEval.at[sample, 'evalue'] = EVals[line[0]]
			except Exception as e:
				print("ERROR:", filepath)
				print(repr(e))
				continue
	print("TOOLS:", tools)

	# Plot Results
	outhtm = Path(OUTPATH, 'htm')
	outtsv = Path(OUTPATH, 'tsv')
	outimg = Path(OUTPATH, 'img')
	outhtm.mkdir(exist_ok=True, parents=True)
	outtsv.mkdir(exist_ok=True, parents=True)
	outimg.mkdir(exist_ok=True, parents=True)

	fontSize = 16
	figCounts = dict()
	for label in ['KO', 'VOG', 'CAZy']:
		figCounts[label] = dict()
		for kingdom in ['bacteria', 'virus']:
			figCounts[label][kingdom] = go.Figure(layout_title_text=f'{label} {PREFIX} Counts')
	dfEval.to_csv(Path(outtsv, f"{PREFIX}-evals.tsv"), sep='\t', index_label="Sample_ID")
	for sample_type,df in dfAnnotate.items():
		# Save Tables
		df:pd.DataFrame = df.sort_index()#.fillna(0)

		#print("\n", key, df, sep='\n')
		df.to_csv(Path(outtsv, f"annotations-{PREFIX}_{sample_type}.tsv"), sep='\t', index_label="Sample_ID")

		#df.fillna(0, inplace=True)

		figAnnotate = go.Figure(layout_title_text=f"{sample_type}")
		try:
			ORF_mean = (df[f'Metacerberus-ORF_count'] + df[f'DRAM-ORF_count'] + df[f'PROKKA-ORF_count']) / 3
		except:
			ORF_mean = (df[f'Metacerberus-ORF_count'] + df[f'DRAM-ORF_count']) / 2
		orf_counts = dict()
		figORF = go.Figure(layout_title_text=f"{sample_type}")
		figFails = go.Figure(layout_title_text=f'{sample_type}')
		#dfStats = pd.DataFrame()
		for i,tool in enumerate(['Metacerberus', 'DRAM', 'InterProScan', 'InterProScan_pro', 'PROKKA'], start=1):
			if f'{tool}-ORF_count' not in df.columns:
				continue
			# ORF barchart
			trace = go.Bar(
				y = [df[f'{tool}-ORF_count'].mean()],
				x = [f'{tool}'],
				name = f'{tool}',
				marker_color = colors[tool],
				)
			figORF.add_trace(trace)
			# Annotation fails
			print(sample_type, tool, df[f'{tool}-ORF_count'].isna().sum(), len(df[f'{tool}-ORF_count']))
			trace = go.Bar(
				y = [df[f'{tool}-ORF_count'].isna().sum()],
				x = [f'{tool}'],
				name = f'{tool}',
				marker_color = colors[tool],
				)
			figFails.add_trace(trace)
			# ID COUNTS
			if tool.startswith('DRAM') or tool.startswith('Metacerberus'):
				for label in ['KO', 'VOG', 'CAZy']:
					trace = go.Bar(
						y = [df[f'{tool}-{label}_count'].sum()],
						x = [f'{tool}'],
						name = f'{tool}',
						marker_color = colors[tool],
						)
					if sample_type in ['CPR', 'GTDB-bacteria', 'GTDB-archaea']:
						figCounts[label]['bacteria'].add_trace(trace)
					else:
						figCounts[label]['virus'].add_trace(trace)
			# Annotation counts
			for plot in ['Annotated', 'Hypothetical', 'Unknown']:
				trace_name = f'{tool}-{plot}'
				if tool.startswith('InterProScan'):
					data = 100.0 * df[trace_name] / df[f'Metacerberus-ORF_count']
				else:
					data = 100.0 * (df[trace_name] / df[f'{tool}-ORF_count'])
				# Stats
				#dfStats.at['median', trace_name] = data.median()
				#dfStats.at['q1', trace_name] = data.quantile(0.25)
				#q1=ss.scoreatpercentile(data, 25)
				#q2=ss.scoreatpercentile(data, 50)
				#q3=ss.scoreatpercentile(data, 75)
				#iqr=ss.iqr(data)
				# There are an infinite variety of ways to do this, but the one I’ve used is:
				# [min, q1, median, median, q3, max]
				# [min, q1, q1, median, q3, q3, max]
				#print(sample_type, tool, q1, q2, q3, iqr)
				trace = go.Box(
					y = data, # data as [q1, q2, q2, median, q3, q3, q4]
					#boxpoints = 'all',
					name = trace_name,#f'{plot}-{tool}',
					legendgroup = tool,
					#legendgrouptitle = dict(text=tool),
					marker_color = colors[tool],
					)
				figAnnotate.add_trace(trace)
		# Annotation figures
		figAnnotate.update_layout(
			template = "plotly_white",
			#legend_title = "",
			#showlegend = False,
			#paper_bgcolor = 'rgba(0,0,0,0)',
			#plot_bgcolor = 'rgba(0,0,0,0)',
			font=dict(size=fontSize, color="Black"),
			yaxis_range=[0,100],
			)
		figAnnotate.update_xaxes(gridcolor="rgba(00,00,00,0.00)", tickangle=90)
		figAnnotate.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor="rgba(38,38,38,0.15)", title=dict(text='Percentage of proteins'))
		figAnnotate.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
		figAnnotate.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
		figAnnotate.write_html(file=Path(outhtm, f"annotations-{PREFIX}-{sample_type}.html"))
		figAnnotate.write_image(Path(outimg, f'annotations-{PREFIX}-{sample_type}.svg'), width=1400, height=700)

		# ORF barchart
		trace = go.Bar(
			y = [ORF_mean.mean()],
			x = ['Mean'],
			name = 'Mean',
			marker_color = 'grey')
		figORF.add_trace(trace)

		figORF.update_layout(
			template = "plotly_white",
			font = dict(size=fontSize, color="Black"),
			bargap = 0.2,
			bargroupgap = 0.3,
			)
		figORF.update_xaxes(gridcolor="rgba(00,00,00,0.00)", tickangle=90)
		figORF.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor="rgba(38,38,38,0.15)", title=dict(text='Average ORF <br> called per genome'))
		#figORF.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
		figORF.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
		figORF.write_html(file=Path(outhtm, f"ORF_counts-{PREFIX}-{sample_type}.html"))
		figORF.write_image(Path(outimg, f'ORF_counts-{PREFIX}-{sample_type}.svg'), width=800, height=400)

	# Counts figures
	for label in ['KO', 'VOG', 'CAZy']:
		for kingdom in ['bacteria', 'virus']:
			figCounts[label][kingdom].update_layout(
				title = dict(text = f'{label} counts ({PREFIX})'),
				template = "plotly_white",
				font = dict(size=fontSize, color="Black"),
				showlegend = False,
				barmode='group',
				bargap = 0.2,
				bargroupgap = 0.1,
				)
			figCounts[label][kingdom].update_xaxes(gridcolor="rgba(00,00,00,0.00)")#, tickangle=90)
			figCounts[label][kingdom].update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor="rgba(38,38,38,0.15)", title=dict(text=f'{label} total count'))
			#figKO.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
			figCounts[label][kingdom].update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
			outfile = f"counts-{PREFIX}-{label}-{kingdom}"
			figCounts[label][kingdom].write_html(file=Path(outhtm, f"{outfile}.html"))
			figCounts[label][kingdom].write_image(Path(outimg, f"{outfile}.svg"), width=1520, height=756)

	return 0

## MAIN ##
if __name__ == "__main__":
	main()

## End of Script
