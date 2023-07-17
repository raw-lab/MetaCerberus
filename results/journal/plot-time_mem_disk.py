#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pathlib import Path
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as ps
from plot_header import colors

outpath = Path("plots")
time_factors = [1, 60, 3600]

def get_seconds(time_str):
	time = time_str.split(':')
	seconds = 0
	for i,t in enumerate(time[::-1], start=0):
		seconds += float(t) * time_factors[i]
	return seconds

def get_minutes(time_str):
	return get_seconds(time_str) / 60

def get_hours(time_str):
	return get_seconds(time_str) / 3600

def main():
	re_file = re.compile(r'slurm-([A-Za-z]+)-([0-9]+)_([0-9]+).out')
	re_data = re.compile(r'([0-9:.]+)elapsed.* ([0-9]+)maxresident')
	re_disk = re.compile(r'^([0-9]+)\sresults\/([A-Za-z_]+)\/([A-Za-z0-9-_]+)\/[A-Za-z\/]+\/(.+)$')
	re_sample = re.compile(r'^([0-9]+)\s.+\/([A-Za-z0-9_.]+)$', re.MULTILINE)
	df = dict(Time=pd.DataFrame(), Mem=pd.DataFrame(), Disk=pd.DataFrame())

	# Gather data
	data_size = open("disk_usage.txt").read()
	for filepath in Path("log").rglob('*'):
		match = re_file.search(str(filepath))
		if match:
			tool,jobid,sampleid = match.groups()
			if int(sampleid) > 200: #TODO: FILTERING OUT JUST GTDB FOR NOW
				continue
			data = open(filepath).read()
			match = re_data.search(data)
			if match:
				time,mem = match.groups()
				df['Time'].at[int(sampleid), tool] = float(get_minutes(time))
				df['Mem'].at[int(sampleid), tool] = float(mem) / 1e6
				match_name = re.search(fr'Running {tool} On .+\/([A-Za-z0-9_.]+).fna$', data, re.MULTILINE)
				if match_name:
					name = match_name.group(1)
					match_size = re.search(rf'^([0-9]+)\sresults\/{tool}.+{name}$', data_size, re.MULTILINE)
					if match_size:#results/Metacerberus/GTDB-100
						fsize = match_size.group(1)
						#print(name, ":", fsize)
						df['Disk'].at[int(sampleid), tool] = float(fsize)
		continue

	# Plotting Results
	outpath.mkdir(exist_ok=True, parents=True)

	for name,data in df.items():
		#print(f"\n{name}", df[name], sep='\n')
		df[name] = df[name].reindex(sorted(df[name].columns, reverse=False), axis=1).sort_index()
		df[name].index = df[name].index.map(str)
		df[name].to_csv(Path(outpath, f"{name}.tsv"), sep='\t', index_label="Sample_ID")
		if name == 'Time':
			title = "Time used"
			label = "Time (minutes)"
		elif name == 'Mem':
			title = "RAM used"
			label = "Memory (GB)"
		elif name == 'Disk':
			title = "Disk used"
			label = "Disk space (KB)"
		fig = go.Figure(layout_title_text=f"{title}")
		for tool in ['Metacerberus', 'DRAM', 'InterProScan', 'PROKKA']:
			trace_name = f'{tool}'
			trace = go.Box(
				y = df[name][f'{tool}'],
				name = trace_name,
				marker_color = colors[tool],
				legendgrouptitle = dict(font=dict(color=colors[tool]))
				)
			fig.add_trace(trace)
		fig.update_layout(
			template = "plotly_white",
			#legend_title = "",
			showlegend = False,
			#paper_bgcolor = 'rgba(0,0,0,0)',
			#plot_bgcolor = 'rgba(0,0,0,0)',
			font=dict(size=24, color="Black"), #TODO: Match font color to figure color
		)
		fig.update_xaxes(gridcolor="rgba(00,00,00,0.00)", tickangle=0)
		fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor="rgba(38,38,38,0.15)", title=dict(text=label))
		fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
		fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
		fig.write_html(file=Path(outpath, f"{name}.html"))
		fig.write_image(file=Path(outpath, f"{name}.svg"), width=1520, height=756)

	return 0

## MAIN ##
if __name__ == "__main__":
	main()

## End of Script
