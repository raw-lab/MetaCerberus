#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pandas as pd
import scipy.stats as ss
import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as ps
from pathlib import Path
from plot_header import colors

outpath = Path("plots")

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
		tools.add(tool)

		if sample_type not in dfAnnotate:
			dfAnnotate[sample_type] = pd.DataFrame()
			dfEvalue[sample_type] = pd.DataFrame()
		with filepath.open() as reader:
			ORFs = dict()
			KOs = dict()
			COGs = dict()
			CAZYs = dict()
			EVals = dict()
			if tool != 'InterProScan':
				# skip headers
				reader.readline()
			try:
				for line in reader:
					line = line.rstrip('\n').split('\t')
					if line[0] not in ORFs:
						ORFs[line[0]] = 0
						KOs[line[0]] = 0
						COGs[line[0]] = 0
						CAZYs[line[0]] = 0
					if tool.startswith('DRAM'):
						if list(filter(re_hypothetical.search, line)):
							ORFs[line[0]] |= 2
						elif len(line[8] + line[10] + line[17] + line[18]) > 0:
							ORFs[line[0]] |= 4
						# ko counts
						if line[8].startswith('K'):
							KOs[line[0]] += 1
					if tool.startswith('InterProScan'):
						if list(filter(re_hypothetical.search, line)):
							ORFs[line[0]] |= 2
						elif line[5] != '-' and line[11] != '-':
							ORFs[line[0]] |= 4
					if tool.startswith('Metacerberus'):
						if line[12] == "Hypothetical":
							ORFs[line[0]] |= 2
						elif float(line[9]) < 1e-15 and float(line[10]) >= 60:
							ORFs[line[0]] |= 4
							dfEval.at[sample, 'sample_type'] = sample_type
							dfEval.at[sample, 'tool'] = tool
							dfEval.at[sample, 'evalue'] = line[9]
						# ko counts
						if line[2].startswith('K'):
							if float(line[9]) < 1e-15 and float(line[10]) >= 60:
								KOs[line[0]] += 1
					if tool.startswith('PROKKA'):
						if line[6] == "hypothetical protein":
							ORFs[line[0]] |= 2
						else:
							ORFs[line[0]] |= 4
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
					ko_count = sum(KOs.values())
					dfAnnotate[sample_type].at[sample, f'{tool}-KO_count'] = ko_count
				# Evalue
				#dfEval.at[sample, 'sample_type'] = sample_type
				#dfEval.at[sample, 'tool'] = tool
				#dfEval.at[sample, 'evalue'] = EVals[line[0]]
			except:
				#print("ERROR:", filepath)
				continue
	print("TOOLS:", tools)

	# Plot Results
	outhtm = Path(outpath, 'htm')
	outtsv = Path(outpath, 'tsv')
	outimg = Path(outpath, 'img')
	outhtm.mkdir(exist_ok=True, parents=True)
	outtsv.mkdir(exist_ok=True, parents=True)
	outimg.mkdir(exist_ok=True, parents=True)

	fontSize = 16
	figKO_bacteria = go.Figure(layout_title_text=f'KO Counts')
	figKO_viruses = go.Figure(layout_title_text=f'KO Counts')
	dfEval.to_csv(Path(outtsv, f"evals.tsv"), sep='\t', index_label="Sample_ID")
	for sample_type,df in dfAnnotate.items():
		# Save Tables
		df:pd.DataFrame = df.sort_index()#.fillna(0)

		#print("\n", key, df, sep='\n')
		df.to_csv(Path(outtsv, f"annotations_{sample_type}.tsv"), sep='\t', index_label="Sample_ID")

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
			# KO counts
			if tool.startswith('DRAM') or tool.startswith('Metacerberus'):
				trace = go.Bar(
					y = [df[f'{tool}-KO_count'].sum()],
					x = [f'{sample_type}'],
					name = f'{tool}',
					marker_color = colors[tool],
					)
				if sample_type in ['CPR', 'GTDB-bacteria', 'GTDB-archaea']:
					figKO_bacteria.add_trace(trace)
				else:
					figKO_viruses.add_trace(trace)
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
		figAnnotate.write_html(file=Path(outhtm, f"annotations-{sample_type}.html"))
		figAnnotate.write_image(Path(outimg, f'annotations-{sample_type}.svg'), width=1400, height=700)

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
		figORF.write_html(file=Path(outhtm, f"ORF_counts-{sample_type}.html"))
		figORF.write_image(Path(outimg, f'ORF_counts-{sample_type}.svg'), width=800, height=400)

		# Save stats
		#dfStats.to_csv(Path(outtsv, f"stats_{sample_type}.tsv"), sep='\t', index_label="Sample_ID")

	# KO counts
	figKO_bacteria.update_layout(
		template = "plotly_white",
		font = dict(size=fontSize, color="Black"),
		barmode='group',
		bargap = 0.2,
		bargroupgap = 0.1,
		)
	figKO_bacteria.update_xaxes(gridcolor="rgba(00,00,00,0.00)", tickangle=90)
	figKO_bacteria.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor="rgba(38,38,38,0.15)", title=dict(text='KO counts'))
	#figKO.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
	figKO_bacteria.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
	figKO_bacteria.write_html(file=Path(outhtm, f"KO_counts-bacteria.html"))
	figKO_bacteria.write_image(Path(outimg, f'KO_counts-bacteria.svg'), width=800, height=400)

	figKO_viruses.update_layout(
		template = "plotly_white",
		font = dict(size=fontSize, color="Black"),
		barmode='group',
		bargap = 0.2,
		bargroupgap = 0.1,
		)
	figKO_viruses.update_xaxes(gridcolor="rgba(00,00,00,0.00)", tickangle=90)
	figKO_viruses.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor="rgba(38,38,38,0.15)", title=dict(text='KO counts'))
	#figKO.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
	figKO_viruses.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
	figKO_viruses.write_html(file=Path(outhtm, f"KO_counts-viruses.html"))
	figKO_viruses.write_image(Path(outimg, f'KO_counts-viruses.svg'), width=800, height=400)

	return 0

## MAIN ##
if __name__ == "__main__":
	main()

## End of Script
