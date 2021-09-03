# -*- coding: utf-8 -*-

import os
import shutil
import re
import pandas as pd
import pkg_resources as pkg


#GLOBAL standard html header to include plotly script
htmlHeader = [
    '<html>',
    '<head><meta charset="utf-8" />',
    '    <script src="plotly-2.0.0.min.js"></script>',
    '</head>',
    '<body>\n']

# TODO: Option for how to include plotly.js.
# False uses script in <head>, 'cdn' loads from internet.
# Can I use both???
plotly_source = 'cdn'


######### Create Report ##########
def createReport(figSunburst, figCharts, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    plotly = pkg.resource_filename('cerberus_data', 'plotly-2.0.0.min.js')
    shutil.copy(plotly, path)
    
    # Sunburst HTML files
    for sample,figures in figSunburst.items():
        outpath = os.path.join(path, sample)
        for name,fig in figures.items():
            with open(f"{outpath}/sunburst_{name}.html", 'w') as htmlOut:
                htmlOut.write("\n".join(htmlHeader))
                htmlOut.write(f"<H1>Sunburst summary of {name} Levels</H1>\n")
                htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
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


########## Write PCA Report ##########
def write_Stats(outpath: os.PathLike, readStats: dict, protStats: dict, config: dict):
    dictStats = protStats.copy()

    # Merge Stats
    nstatLabels = ['N25', 'N50', 'N75', 'N90']
    trimLabels = ['passed', 'low quality', 'too many Ns', 'too short', 'low complexity', 'adapter trimmed', 'bases: adapters', 'duplication rate %']
    deconLabels = ['contaminants', 'QTrimmed', 'Total Removed', 'Results']
    reNstats = re.compile(r"N25[\w\s:%()]*>= ([0-9]*)[\w\s:%()]*>= ([0-9]*)[\w\s:%()]*>= ([0-9]*)[\w\s:%()]*>= ([0-9]*)")
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
        # Trimmed stats
        infile = os.path.join(config['DIR_OUT'], config['STEP'][3], key, "stderr.txt")
        try:
            trimStats = '\n'.join(open(infile).readlines())
            trim = reTrim.search(trimStats, re.MULTILINE)
            if trim:
                for i,label in enumerate(trimLabels, 1):
                    dictStats[key]['trim: '+label] = trim.group(i)
        except: pass
        # Decon stats
        infile = os.path.join(config['DIR_OUT'], config['STEP'][4], key, "stderr.txt")
        try:
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
    #Write Combined Stats to File
    outfile = os.path.join(outpath, "combined", "stats.tsv")
    os.makedirs(os.path.join(outpath, "combined"), exist_ok=True)
    pd.DataFrame(dictStats).to_csv(outfile, sep='\t')
    return


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
                    # type= plotly.graph_objs._figure.Figure
                    #htmlOut.write(f"<h2 style='text-align:center'>{graph.replace('_', ' ')}</h2>")
                    htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
                    htmlOut.write(htmlFig + '\n')
            htmlOut.write('\n</body>\n</html>\n')
    return None


########## Write Tables ##########
def writeTables(table: pd.DataFrame, filePrefix: os.PathLike):
    table = table.copy()

    regex = re.compile(r"^lvl[0-9]: ")
    table['Name'] = table['Name'].apply(lambda x : regex.sub('',x))

    levels = int(max(table[table.Level != 'Function'].Level))
    for i in range(1,levels+1):
        filter = table['Level']==str(i)
        table[filter][['Name','Count']].to_csv(f"{filePrefix}_level-{i}.tsv", index = False, header=True, sep='\t')
    regex = re.compile(r"^K[0-9]*: ")
    table['Name'] = table['Name'].apply(lambda x : regex.sub('',x))
    table[table['Level']=='Function'][['KO Id','Name','Count']].to_csv(f"{filePrefix}_level-ko.tsv", index = False, header=True, sep='\t')


########## Write HTML Files ##########
def write_HTML_files(outfile, figure, sample, name):

    with open(outfile, 'w') as htmlOut:
        htmlOut.write("\n".join(htmlHeader))
        htmlOut.write(f"<h1>Cerberus {name} Report for '{sample}<h1>\n")
        levels = {}
        htmlOut.write(f'<H2>{name} Levels</H2>\n')
        htmlOut.write("<H4>*Clicking on a bar in the graph displays the next level.</br>The graph will cycle back to the first level after reaching the last level.</H4>")
        for title, figure in figure.items():
            htmlFig = figure.to_html(full_html=False, include_plotlyjs=plotly_source)
            try:
                id = re.search('<div id="([a-​z0-9-]*)"', htmlFig).group(1)
            except:
                continue
            levels[id] = title
            display = "block" if title=="Level 1" else "none"
            htmlFig = htmlFig.replace('<div>', f'<div id="{title}" style="display:{display};">', 1)
            htmlOut.write(htmlFig + '\n')
        # Scripts
        htmlOut.write('<script>\n')
        for id, title in levels.items():
            level = int(title.split(':')[0][-1])
            htmlOut.write(f"""
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
        htmlOut.write('</script>\n')
        htmlOut.write('\n</body>\n</html>\n')

        return
