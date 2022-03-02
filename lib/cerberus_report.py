# -*- coding: utf-8 -*-
"""cerberus_report.py: Module to create the final HTML reports and tsv files
"""

from collections import OrderedDict
import os
import time
import shutil
import base64
import re
from dominate.util import raw
import pandas as pd
import pkg_resources as pkg
import plotly.express as px
import dominate
from dominate.tags import *


# standard html header to include plotly script
htmlHeader = [
    '<html>',
    '<head><meta charset="utf-8" />',
    '    <script src="plotly-2.0.0.min.js"></script>',
    '</head>',
    '<body>\n']

# TODO: Option for how to include plotly.js.
# False uses script in <head>, 'cdn' loads from internet.
# Can I use both???
PLOTLY_SOURCE = 'cdn'

# Data resources
STYLESHEET = pkg.resource_stream('meta_cerberus', 'data/style.css').read().decode()
ICON = base64.b64encode(pkg.resource_stream('meta_cerberus', 'data/cerberus_logo.png').read()).decode()
PLOTLY = pkg.resource_filename('meta_cerberus', 'data/plotly-2.0.0.min.js')


######### Create Report ##########
def createReport(figSunburst, figCharts, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    shutil.copy(PLOTLY, path)
    
    # Sunburst HTML files
    for sample,figures in figSunburst.items():
        outpath = os.path.join(path, sample)
        for name,fig in figures.items():
            with open(f"{outpath}/sunburst_{name}.html", 'w') as htmlOut:
                htmlOut.write("\n".join(htmlHeader))
                htmlOut.write(f"<H1>Sunburst summary of {name} Levels</H1>\n")
                htmlFig = fig.to_html(full_html=False, include_plotlyjs=PLOTLY_SOURCE)
                htmlOut.write(htmlFig + '\n')
                htmlOut.write("\n</body>\n</html>\n")

    # Bar Charts
    for sample,figures in figCharts.items():
        outpath = os.path.join(path, sample)
        for name,fig in figures[0].items():
            outfile = os.path.join(outpath, f"barchart_{name}.html")
            write_HTML_files(outfile, fig, sample, name)
        continue

    return None


########## Write Stats ##########
def write_Stats(outpath:os.PathLike, readStats:dict, protStats:dict, NStats:dict, config:dict):
    dictStats = protStats.copy()

    # Merge Stats
    nstatLabels = ['N25', 'N50', 'N75', 'N90']
    trimLabels = ['passed', 'low quality', 'too many Ns', 'too short', 'low complexity', 'adapter trimmed', 'bases: adapters', 'duplication rate %']
    deconLabels = ['contaminants', 'QTrimmed', 'Total Removed', 'Results']
    reNstats = re.compile(r"N25[\w\s:%()]*>= ([0-9]*)[\w\s:%()]*>= ([0-9]*)[\w\s:%()]*>= ([0-9]*)[\w\s:%()]*>= ([0-9]*)")
    reMinMax = re.compile(r"Max.*:.([0-9]*)\nMin.*:.([0-9]*)")
    reGC = re.compile(r"GC count:\s*([0-9]*)[\w\s]*%:\s*([.0-9]*)")
    reTrim = re.compile(r"Filtering result:[\w\s]*: ([0-9]*)[\w\s]*: ([0-9]*)[\w\s]*: ([0-9]*)[\w\s]*: ([0-9]*)[\w\s]*: ([0-9]*)[\w\s]*: ([0-9]*)[\w\s]*: ([0-9]*)[\w\s]*: ([0-9]*)")
    reDecon = re.compile(r"([0-9]*) reads \([0-9%.]*\)[\s]*([0-9]*)[\w\s(0-9-.%)]*:[\s]*([0-9]*) reads \([0-9%.]*\)[\s]*([0-9]*)[\w\s(0-9-.%)]*:[\s]*([0-9]*) reads \([0-9%.]*\)[\s]*([0-9]*)[\w\s(0-9-.%)]*:[\s]*([0-9]*) reads \([0-9%.]*\)[\s]*([0-9]*)")
    for key,value in readStats.items():
        # GC Count
        gcCount = reGC.search(value, re.MULTILINE)
        if gcCount: dictStats[key]['GC count'] = gcCount.group(1)
        if gcCount: dictStats[key]['GC %'] = gcCount.group(2)
        # N25-N90
        Nstats = reNstats.search(value, re.MULTILINE)
        if Nstats:
            for i,label in enumerate(nstatLabels, 1):
                dictStats[key][label] = Nstats.group(i)
        # Min-Max fasta
        min_max = reMinMax.search(value, re.MULTILINE)
        if min_max: dictStats[key]['Contig Min Length'] = min_max.group(2)
        if min_max: dictStats[key]['Contig Max Length'] = min_max.group(1)
        # Trimmed stats
        try:
            infile = os.path.join(config['DIR_OUT'], config['STEP'][3], key, "stderr.txt")
            trimStats = '\n'.join(open(infile).readlines())
            trim = reTrim.search(trimStats, re.MULTILINE)
            if trim:
                for i,label in enumerate(trimLabels, 1):
                    dictStats[key]['trim: '+label] = trim.group(i)
        except: pass
        # Decon stats
        try:
            infile = os.path.join(config['DIR_OUT'], config['STEP'][4], key, "stderr.txt")
            deconStats = '\n'.join(open(infile).readlines())
            decon = reDecon.search(deconStats, re.MULTILINE)
            if decon:
                for i,label in enumerate(deconLabels, 0):
                    dictStats[key]['decon: reads'+label] = decon.group(i*2+1)
                    dictStats[key]['decon: bases'+label] = decon.group(i*2+2)
        except: pass
        # Write fasta stats to file
        outfile = os.path.join(outpath, key, "fasta_stats.txt")
        os.makedirs(os.path.join(outpath, key), exist_ok=True)
        with open(outfile, 'w') as writer:
            writer.write(value)

    # N-Stats
    for key,value in NStats.items():
        repeats = [y for x in value.values() for y in x]
        dictStats[key]["Contigs w/ N-repeats:"] = len(value)
        dictStats[key]["N-repeat Count"] = len(repeats)
        dictStats[key]["N-repeat Total Length"] = sum(repeats)
        dictStats[key]["N-repeat Average "] = round(sum(repeats)/len(repeats), 2)


    #Write Combined Stats to File
    outfile = os.path.join(outpath, "combined", "stats.tsv")
    os.makedirs(os.path.join(outpath, "combined"), exist_ok=True)
    dfStats = pd.DataFrame(dictStats)
    dfStats.to_csv(outfile, sep='\t')

    # HTML Plots of Stats
    outfile = os.path.join(outpath, "combined", "stats.html")

    tsv_stats = base64.b64encode(dfStats.to_csv(sep='\t').encode('utf-8')).decode('utf-8')
    dfStats = dfStats.apply(pd.to_numeric).T.rename_axis('Sample').reset_index()
    regex = re.compile(r"^([a-zA-Z]*_)")
    prefixes = {regex.search(x).group(1):i for i,x in dfStats['Sample'].iteritems()}.keys()

    figPlots = OrderedDict()
    for prefix in prefixes:
        dfPre = dfStats[dfStats['Sample'].str.startswith(prefix)]
        dfPre['Sample'] = dfPre['Sample'].apply(lambda x: regex.sub('', x))
        # ORF Calling Results
        try:
            df = dfPre[["Sample", 'Protein Count (Total)', 'Protein Count (>Min Score)']]
            df = df.melt(id_vars=['Sample'], var_name='count', value_name='value')
            fig = px.bar(df, x='Sample', y='value',
                color='count', barmode='group',
                labels=dict(count="", value="Count"))
            figPlots[f'ORF Calling Results ({prefix[:-1]})'] = fig
        except: pass
        # Average Protein Length
        try:
            fig = px.bar(dfPre, x='Sample', y='Average Protein Length',
                labels={'Average Protein Length':"Peptide Length"})
            figPlots[f'Average Protein Length ({prefix[:-1]})'] = fig
        except: pass
        # Annotations
        try:
            df = dfPre[['Sample', 'FOAM KO Count', 'KEGG KO Count']]
            df.rename(columns={'FOAM KO Count': 'FOAM KO', 'KEGG KO Count':'KEGG KO'}, inplace=True)
            df = df.melt(id_vars=['Sample'], var_name='group', value_name='value')
            fig = px.bar(df, x='Sample', y='value', color='group', barmode='group',
                labels={'value': 'count', 'group':''})
            figPlots[f'Annotations ({prefix[:-1]})'] = fig
        except: pass
        # GC %
        try:
            df = dfPre[['Sample', 'GC %']]
            fig = px.bar(df, x='Sample', y='GC %',
                labels={'GC %':'GC Percent (%)'}
            )
            figPlots[f'GC (%) ({prefix[:-1]})'] = fig
        except: pass
        # Metaome Stats
        try:
            df = dfPre[['Sample', 'N25', 'N50', 'N75', 'N90']]
            df = df.melt(id_vars=['Sample'], var_name='group', value_name='value')
            fig = px.bar(df, x='Sample', y='value',
                color='group', barmode='group',
                labels=dict(group="", value="Sequence Length")
            )
            figPlots[f'Assembly Stats ({prefix[:-1]})'] = fig
        except: pass
        # Contig Min Max
        try:
            df = dfPre[['Sample', 'Contig Min Length', 'Contig Max Length']]
            df = df.melt(id_vars=['Sample'], var_name='group', value_name='value')
            fig = px.bar(df, x='Sample', y='value', text='value',
                color='group', barmode='group',
                labels=dict(group="", value="Sequence Length")
            )
            fig.update_traces(textposition='outside')
            figPlots[f'Min-Max FASTA Length ({prefix[:-1]})'] = fig
        except: pass

    # Update Graph Colors & Export
    os.makedirs(os.path.join(outpath, "combined", "img"),exist_ok=True)
    for key in figPlots.keys():
        figPlots[key].update_layout(dict(plot_bgcolor='White', paper_bgcolor='White'))
        figPlots[key].update_xaxes(showline=True, linewidth=2, linecolor='black')
        figPlots[key].update_yaxes( showline=True, linewidth=2, linecolor='black',
                                    showgrid=True, gridwidth=1, gridcolor='LightGray')
        figPlots[key].write_image(os.path.join(outpath, "combined", "img", key+'.svg'))

    # Create HTML with Figures
    with dominate.document(title='Stats Report') as doc:
        with doc.head:
            meta(charset="utf-8")
            script(type="text/javascript", src="plotly-2.0.0.min.js")
            with style(type="text/css"):
                raw('\n'+STYLESHEET)
        with div(cls="document", id="cerberus-summary"):
            with h1(cls="title"):
                img(src=f"data:image/png;base64,{ICON}", height="40")
                a("CERBERUS", cls="reference external", href="https://github.com/raw-lab/cerberus")
                raw(" - Statistical Summary")
            with div(cls="contents topic", id="contents"):
                with ul(cls="simple"):
                    li(a("Summary", cls="reference internal", href="#summary"))
                    with ul():
                        for key in figPlots.keys():
                            li(a(f"{key}", cls="reference internal", href=f"#{key}"))
                    li(a("Downloads", cls="reference internal", href="#downloads"))
            with div(h1("Summary"), cls="section", id="summary"):
                for key,fig in figPlots.items():
                    with div(h2(f"{key}"), cls="section", id=f"{key}"):
                        raw(fig.to_html(full_html=False, include_plotlyjs=PLOTLY_SOURCE))
            with div(cls="section", id="downloads"):
                h1("Downloads")
                with div(cls="docutils container", id="attachments"):
                    with blockquote():
                        with div(cls="docutils container", id="table-1"):
                            with dl(cls="docutils"):
                                data_URI = f"data:text/tab-separated-values;base64,{tsv_stats}"
                                dt("Combined Stats:")
                                dd(a("combined_stats.tsv", href=data_URI, download="combined_stats.tsv", draggable="true"))
                div(time.strftime("%Y-%m-%d", time.localtime()), cls="docutils container", id="metadata")

    with open(outfile, 'w') as writer:
        writer.write(doc.render())

    return dfStats


########## Write PCA Report ##########
def write_PCA(outpath, pcaFigures):
    # PCA Files
    os.makedirs(os.path.join(outpath), exist_ok=True)

    for database,figures in pcaFigures.items():
        prefix = f"{outpath}/{database}"
        with open(prefix+"_PCA.htm", 'w') as htmlOut:
            htmlOut.write("\n".join(htmlHeader))
            htmlOut.write(f"<h1>PCA Report for {database}<h1>\n")
            for graph,fig in figures.items():
                if type(fig) is pd.DataFrame:
                    fig.to_csv(f"{prefix}_{graph}.tsv", index=False, header=True, sep='\t')
                else:
                    htmlFig = fig.to_html(full_html=False, include_plotlyjs=PLOTLY_SOURCE)
                    htmlOut.write(htmlFig + '\n')
                    fig.write_image(os.path.join(outpath, "img", f"{database}_{graph}.svg"))
            htmlOut.write('\n</body>\n</html>\n')
    return None


########## Write Tables ##########
def writeTables(table: pd.DataFrame, filePrefix: os.PathLike):
    table = table.copy()

    regex = re.compile(r"^lvl[0-9]: ")
    table['Name'] = table['Name'].apply(lambda x : regex.sub('',x))
    try:
        levels = int(max(table[table.Level != 'Function'].Level))
        for i in range(1,levels+1):
            filter = table['Level']==str(i)
            table[filter][['Name','Count']].to_csv(f"{filePrefix}_level-{i}.tsv", index = False, header=True, sep='\t')
        regex = re.compile(r"^K[0-9]*: ")
        table['Name'] = table['Name'].apply(lambda x : regex.sub('',x))
    except:
        return
    table[table['Level']=='Function'][['KO Id','Name','Count']].to_csv(f"{filePrefix}_level-ko.tsv", index = False, header=True, sep='\t')
    return


########## Write HTML Files ##########
def write_HTML_files(outfile, figure, sample, name):
    sample = re.sub(r'^[a-zA-Z]*_', '', sample)
    with dominate.document(title=f'Cerberus: {name} - {sample}') as doc:
        with doc.head:
            meta(charset="utf-8")
            script(type="text/javascript", src="plotly-2.0.0.min.js")
            with style(type="text/css"):
                raw('\n'+STYLESHEET)
        with div(cls="document", id="cerberus-report"):
            # Header
            with h1(cls="title"):
                img(src=f"data:image/png;base64,{ICON}", height="40")
                a("CERBERUS", cls="reference external", href="https://github.com/raw-lab/cerberus")
                raw(f" - {name} Bar Graphs for '{sample}'")
            # Side Panel
            with div(cls="contents topic", id="contents"):
                with ul(cls="simple"):
                    li("(Bargraphs might take a few minutes to load)", cls="reference internal")
                    li("*Clicking on a bar in the graph displays the next level.")
                    li("The graph will cycle back to the first level after reaching the last level.")
            # Main Content
            with div(h1(f"{name} Levels"), cls="section", id="summary"):
                levels = {}
                for title, figure in figure.items():
                    htmlFig = figure.to_html(full_html=False, include_plotlyjs=PLOTLY_SOURCE)
                    try:
                        id = re.search('<div id="([a-z0-9-]*)"', htmlFig).group(1)
                    except:
                        continue
                    levels[id] = title
                    display = "block" if title=="Level 1" else "none"
                    htmlFig = htmlFig.replace('<div>', f'<div id="{title}" style="display:{display};">', 1)
                    raw(htmlFig)
                div(time.strftime("%Y-%m-%d", time.localtime()), cls="docutils container", id="metadata")
            # Scripts
            with script():
                for id, title in levels.items():
                    level = int(title.split(':')[0][-1])
                    raw(f"""
                document.getElementById("{id}").on('plotly_click', function(data){{
                    var name = data.points[0].x;
                    var id = "Level {level+1}: " + name
                    element = document.getElementById(id)
                    if (element !== null)
                        element.style.display = "block";
                    else
                        document.getElementById("Level 1").style.display = "block";
                    document.getElementById("{title}").style.display = "none";
                    // Refresh size
                    var event = document.createEvent("HTMLEvents");
                    event.initEvent("resize", true, false);
                    document.dispatchEvent(event);
                }});""")
    with open(outfile, 'w') as writer:
        writer.write(doc.render())
    return
