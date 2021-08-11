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
def createReport(dicTables, protStats, figSunburst, figCharts, pcaFigure, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    plotly = pkg.resource_filename('cerberus_data', 'plotly-2.0.0.min.js')
    shutil.copy(plotly, path)

    # Save XLS and CVS reports and HTML files
    for sample,table in dicTables.items():
        table = table.copy()
        os.makedirs(os.path.join(path, sample), exist_ok=True)
        
        # Write rollup tables
        outpath = os.path.join(path, sample)
        outfile = os.path.join(outpath, sample+'_rollup.tsv')
        table['Name'] = table['Name'].apply(lambda x: re.sub("^K[0-9]*:", "", x))
        table.to_csv(outfile, index = False, header=True, sep='\t')
        outfile = os.path.join(outpath, sample+'_lvl-1.tsv')
        table[table['Level']==1][['Type','Name','Count']].to_csv(outfile, index = False, header=True, sep='\t')
        outfile = os.path.join(outpath, sample+'_lvl-2.tsv')
        table[table['Level']==2][['Type','Name','Count']].to_csv(outfile, index = False, header=True, sep='\t')
        outfile = os.path.join(outpath, sample+'_lvl-3.tsv')
        table[table['Level']==3][['Type','Name','Count']].to_csv(outfile, index = False, header=True, sep='\t')
        outfile = os.path.join(outpath, sample+'_lvl-4.tsv')
        table[table['Level']==4][['Type','KO Id','Name','Count']].to_csv(outfile, index = False, header=True, sep='\t')

        # Write HTML Report
        outpath = os.path.join(path, sample)
        write_HTML_files(outpath, sample, figSunburst[sample], figCharts[sample][0], figCharts[sample][1])
        continue

    # PCA Files
    outpath = os.path.join(path, "combined")
    os.makedirs(os.path.join(outpath), exist_ok=True)
    outfile = os.path.join(outpath, "protein_stats.tsv")
    header = True
    with open(outfile, 'w') as statsOut:
        for key,value in protStats.items():
            if header:
                print("Sample", *list(value.keys()), sep='\t', file=statsOut)
                header = False
            print(key, *value.values(), sep='\t', file=statsOut)
    if pcaFigure:
        outpath = os.path.join(path, "combined")
        os.makedirs(os.path.join(outpath), exist_ok=True)
        outfile = os.path.join(outpath, "combined_report_PCA.html")
        with open(outfile, 'w') as htmlOut:
            htmlOut.write("\n".join(htmlHeader))
            samples = [s.replace("mic_", '').replace("euk_", '') for s in dicTables.keys()]
            htmlOut.write(f"<h1>PCA Report for: {', '.join(samples)}<h1>\n")
            for db_type,fig in pcaFigure.items():
                if type(fig) is pd.DataFrame:
                    fig.to_csv(f"{outpath}/{db_type}.tsv", index=False, header=True, sep='\t')
                else:
                    htmlOut.write(f"<h2 style='text-align:center'>{db_type.replace('_', ' ')}</h2>")
                    htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
                    htmlOut.write(htmlFig + '\n')
            htmlOut.write('\n</body>\n</html>\n')

    return None


########## Write HTML Files ##########
def write_HTML_files(outpath, sample, figSunburst, FOAM_Charts, KO_Charts):
    # Create HTML Report
    
    # Sunburst Plots
    for key,fig in figSunburst.items():
        with open(f"{outpath}/{sample}_sunburst_{key}.html", 'w') as htmlOut:
            htmlOut.write("\n".join(htmlHeader))
            htmlOut.write(f"<H1>Sunburst summary of {key} Levels</H1>\n")
            htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
            htmlOut.write(htmlFig + '\n')
            htmlOut.write("\n</body>\n</html>\n")


    # FOAM Bar Charts
    with open(f"{outpath}/{sample}_FOAM.html", 'w') as htmlOut:
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
    with open(f"{outpath}/{sample}_KEGG.html", 'w') as htmlOut:
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
