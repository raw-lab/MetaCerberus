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

    # Save XLS and CVS reports and HTML files
    for sample,table in figSunburst.items():
        table = table.copy()
        os.makedirs(os.path.join(path, sample), exist_ok=True)
        
        # Write HTML Report
        outpath = os.path.join(path, sample)
        write_HTML_files(outpath, sample, figSunburst[sample], figCharts[sample][0], figCharts[sample][1])
        continue

    return None


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
                    htmlOut.write(f"<h2 style='text-align:center'>{graph.replace('_', ' ')}</h2>")
                    htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
                    htmlOut.write(htmlFig + '\n')
            htmlOut.write('\n</body>\n</html>\n')
    return None


########## Write HTML Files ##########
def write_HTML_files(outpath, sample, figSunburst, FOAM_Charts, KO_Charts):
    # Create HTML Report
    
    # Sunburst Plots
    for key,fig in figSunburst.items():
        with open(f"{outpath}/sunburst_{key}.html", 'w') as htmlOut:
            htmlOut.write("\n".join(htmlHeader))
            htmlOut.write(f"<H1>Sunburst summary of {key} Levels</H1>\n")
            htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
            htmlOut.write(htmlFig + '\n')
            htmlOut.write("\n</body>\n</html>\n")


    # FOAM Bar Charts
    with open(f"{outpath}/barchart_FOAM.html", 'w') as htmlOut:
        htmlOut.write("\n".join(htmlHeader))
        htmlOut.write(f"<h1>Cerberus FOAM Report for '{sample}<h1>\n")
        dicFOAM = {}
        htmlOut.write('<H2>Foam Levels</H2>\n')
        htmlOut.write("<H4>*Clicking on a bar in the graph displays the next level.</br>The graph will cycle back to the first level after reaching the last level.</H4>")
        for title, fig in FOAM_Charts.items():
            if title == "Level 1":
                title = "Level 1: FOAM"
            htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
            try:
                id = re.search('<div id="([a-​z0-9-]*)"', htmlFig).group(1)
            except:
                continue
            dicFOAM[id] = title
            display = "block" if title=="Level 1: FOAM" else "none"
            htmlFig = htmlFig.replace('<div>', f'<div id="{title}" style="display:{display};">', 1)
            htmlOut.write(htmlFig + '\n')
        # Scripts
        htmlOut.write('<script>\n')
        for id, title in dicFOAM.items():
            level = int(title.split(':')[0][-1])
            htmlOut.write(f"""
        document.getElementById("{id}").on('plotly_click', function(data){{
            var name = data.points[0].x;
            var id = "Level {level+1}: " + name
            element = document.getElementById(id)
            if (element !== null)
                element.style.display = "block";
            else
                document.getElementById("Level 1: FOAM").style.display = "block";
            document.getElementById("{title}").style.display = "none";
            // Refresh size
            var event = document.createEvent("HTMLEvents");
            event.initEvent("resize", true, false);
            document.dispatchEvent(event);
        }});""")
        htmlOut.write('</script>\n')
        htmlOut.write('\n</body>\n</html>\n')

    # KO Bar Charts
    with open(f"{outpath}/barchart_KEGG.html", 'w') as htmlOut:
        htmlOut.write("\n".join(htmlHeader))
        htmlOut.write(f"<h1>Cerberus KEGG Report for '{sample}<h1>\n")
        dicKO = {}
        htmlOut.write('<H2>KO Levels</H2>')
        htmlOut.write("<H4>*Clicking on a bar in the graph displays the next level.</br>The graph will cycle back to the first level after reaching the last level.</H4>")
        for title, fig in KO_Charts.items():
            if title == "Level 1":
                title = "Level 1: KO"
            htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
            try:
                id = re.search('<div id="([a-​z0-9-]*)"', htmlFig).group(1)
            except:
                continue
            dicKO[id] = title
            display = "block" if title=="Level 1: KO" else "none"
            htmlFig = htmlFig.replace('<div>', f'<div id="{title}" style="display:{display};">', 1)
            htmlOut.write(htmlFig + '\n')
        # Scripts
        htmlOut.write('<script>\n')
        for id, title in dicKO.items():
            level = int(title.split(':')[0][-1])
            htmlOut.write(f"""
        document.getElementById("{id}").on('plotly_click', function(data){{
            var name = data.points[0].x;
            var id = "Level {level+1}: " + name
            element = document.getElementById(id)
            if (element !== null)
                element.style.display = "block";
            else
                document.getElementById("Level 1: KO").style.display = "block";
            document.getElementById("{title}").style.display = "none";
            // Refresh size
            var event = document.createEvent("HTMLEvents");
            event.initEvent("resize", true, false);
            document.dispatchEvent(event);
        }});""")
        htmlOut.write('</script>\n')
        htmlOut.write('\n</body>\n</html>\n')
        return


########## Write Tables ##########
def writeTables(table, hierarchy, filePrefix):
    #TODO: change this table to cleaner format
    #table['Name'] = table['Name'].apply(lambda x: re.sub("^K[0-9]*:", "", x))
    #table.to_csv(f"{outpath}/{name}_rollup.tsv", index = False, header=True, sep='\t')
    
    ##### Create Hierarchy Table (recursive method) #####
    def createBarFigs(data, writer, level=0):
        d = {}
        for k,v in data.items():
            print("\t"*level, k, f"\t{v[1]}" if level==3 else '', sep='', file=writer)
            d[k] = v[1]
            createBarFigs(v[0], writer, level+1)
        return

    with open(f"{filePrefix}_rollup.tsv", 'w') as writer:
        print("Level 1", "Level 2", "Level 3", "Level 4", "KO-Count", sep='\t', file=writer)
        createBarFigs(hierarchy, writer)

    for i in [1,2,3]:
        table[table['Level']==i][['Name','Count']].to_csv(f"{filePrefix}_level-{i}.tsv", index = False, header=True, sep='\t')
    table[table['Level']==4][['KO Id','Name','Count']].to_csv(f"{filePrefix}_level-4.tsv", index = False, header=True, sep='\t')
