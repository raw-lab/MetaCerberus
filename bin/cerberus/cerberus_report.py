# -*- coding: utf-8 -*-

import os
import shutil
import re
import pandas as pd


#GLOBAL standard html header to include plotly script
htmlHeader = [
    '<html>',
    '<head><meta charset="utf-8" />',
    '    <script src="plotly-2.0.0.min.js"></script>',
    '</head>',
    '<body>\n']


######### Create Report ##########
def createReport(dicTables, figSunburst, figCharts, pcaFigure, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    shutil.copy(f"{config['PATH']}/plotly-2.0.0.min.js", path)

    # Save XLS and CVS reports and HTML files
    dfFOAM = pd.DataFrame()
    dfKEGG = pd.DataFrame()
    for name,table in dicTables.items():
        os.makedirs(os.path.join(path, name), exist_ok=True)
        # Write rollup tables
        outfile = os.path.join(path, name, name+'_rollup.tsv')
        table.to_csv(outfile, index = False, header=True, sep='\t')

        # Create spreadsheet of counts
        # FOAM
        X = table[table['Type']=="Foam"]
        row = dict(zip(X['Name'].tolist(), X['Count'].tolist()))
        row = pd.Series(row, name=name)
        dfFOAM = dfFOAM.append(row)
        # KEGG
        X = table[table['Type']=="KO"]
        row = dict(zip(X['Name'].tolist(), X['Count'].tolist()))
        row = pd.Series(row, name=name)
        dfKEGG = dfKEGG.append(row)

        # Write HTML Report
        outfile = os.path.join(path, name, name+"_report"+".html")
        writeHTML(outfile, figSunburst[name], figCharts[name][0], figCharts[name][1])

    dfFOAM = dfFOAM.T.fillna(0).astype(int)
    dfKEGG = dfKEGG.T.fillna(0).astype(int)
    dfFOAM.to_csv(os.path.join(path, 'FOAM_counts.tsv'), index = True, header=True, sep='\t')
    dfKEGG.to_csv(os.path.join(path, 'KEGG_counts.tsv'), index = True, header=True, sep='\t')

    # PCA Plot
    if pcaFigure:
        for db_type,fig in pcaFigure.items():
            outfile = os.path.join(path, f"report_{db_type}_PCA.pdf")
            fig.write_image(outfile)

            outfile = os.path.join(path, f"report_{db_type}_PCA_standalone.html")
            fig.write_html(outfile)

            outfile = os.path.join(path, f"report_{db_type}_PCA.html")
            with open(outfile, 'w') as htmlOut:
                htmlOut.write("\n".join(htmlHeader))
                htmlOut.write("<h1>Report<h1>\n")
                htmlFig = fig.to_html(full_html=False, include_plotlyjs=False)
                htmlOut.write(htmlFig + '\n')
                htmlOut.write('\n</body>\n</html>\n')

    return None


########## Write HTML File ##########
def writeHTML(outfile, figSunburst, FOAM_Charts, KO_Charts):
    # Create HTML Report
    
    with open(outfile, 'w') as htmlOut:
        plotly = 'cdn' # TODO: Option for how to include plotly.js. False uses script in <head>, 'cdn' loads from internet.
        htmlOut.write("\n".join(htmlHeader))
        htmlOut.write("<h1>Report<h1>\n")

        # Sunburst Plots
        htmlFig = figSunburst.to_html(full_html=False, include_plotlyjs=plotly)
        htmlOut.write(htmlFig + '\n')

        # FOAM Charts
        dicFOAM = {}
        htmlOut.write('<H2>Foam Levels</H2>\n')

        for title, fig in FOAM_Charts.items():
            if title == "Level 1":
                title = "Level 1: FOAM"
            htmlFig = fig.to_html(full_html=False, include_plotlyjs=False)
            try:
                id = re.search('<div id="([a-​z0-9-]*)"', htmlFig).group(1)
            except:
                continue
            dicFOAM[id] = title
            display = "block" if title=="Level 1: FOAM" else "none"
            htmlFig = htmlFig.replace('<div>', f'<div id="{title}" style="display:{display};">', 1)
            htmlOut.write(htmlFig + '\n')
        # KO Charts
        dicKO = {}
        htmlOut.write('<H2>KO Levels</H2>')
        for title, fig in KO_Charts.items():
            if title == "Level 1":
                title = "Level 1: KO"
            htmlFig = fig.to_html(full_html=False, include_plotlyjs=False)
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
