# -*- coding: utf-8 -*-

import os
import shutil
import re
import pandas as pd
import copy


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
def createReport(dicTables, figSunburst, figCharts, pcaFigure, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    os.makedirs(os.path.join(path, "combined"), exist_ok=True)
    shutil.copy(os.path.join(config['PATH'], "plotly-2.0.0.min.js"), path)

    # Save XLS and CVS reports and HTML files
    dfFOAM = pd.DataFrame()
    dfKEGG = pd.DataFrame()
    for sample,table in dicTables.items():
        os.makedirs(os.path.join(path, sample), exist_ok=True)
        
        # Write rollup tables
        outfile = os.path.join(path, sample, sample+'_rollup.tsv')
        tbl = copy.deepcopy(table) # Make a copy or will damage table for counts spreadsheet
        #tbl['Name'] = tbl['Name'].apply(lambda x: x.split(':',1)[1] if re.match("^K[0-9]*:", x) else x)
        tbl['Name'] = tbl['Name'].apply(lambda x: re.sub("^K[0-9]*:", "", x))
        tbl.to_csv(outfile, index = False, header=True, sep='\t')

        # Write HTML Report
        outpath = os.path.join(path, sample)
        write_HTML_files(outpath, sample, figSunburst[sample], figCharts[sample][0], figCharts[sample][1])
        #outfile = os.path.join(outpath, sample+"_report"+".html")
        #writeHTML(outfile, sample, figSunburst[sample], figCharts[sample][0], figCharts[sample][1])

        # Create spreadsheet of counts
        # FOAM
        X = table[table['Type']=="Foam"]
        row = dict(zip(X['Name'].tolist(), X['Count'].tolist()))
        row = pd.Series(row, name=sample)
        dfFOAM = dfFOAM.append(row)
        # KEGG
        X = table[table['Type']=="KO"]
        row = dict(zip(X['Name'].tolist(), X['Count'].tolist()))
        row = pd.Series(row, name=sample)
        dfKEGG = dfKEGG.append(row)

    # Write spreadsheet of counts as TSV
    dfFOAM = dfFOAM.T.fillna(0).astype(int)
    dfKEGG = dfKEGG.T.fillna(0).astype(int)
    dfFOAM.to_csv(os.path.join(path, "combined", 'FOAM_counts.tsv'), index = True, header=True, sep='\t')
    dfKEGG.to_csv(os.path.join(path, "combined", 'KEGG_counts.tsv'), index = True, header=True, sep='\t')

    # PCA HTML Plots
    if pcaFigure:
        outfile = os.path.join(path, "combined", "combined_report_PCA.html")
        with open(outfile, 'w') as htmlOut:
            htmlOut.write("\n".join(htmlHeader))
            samples = [s.replace("mic_", '').replace("euk_", '') for s in dicTables.keys()]
            htmlOut.write(f"<h1>PCA Report for: {', '.join(samples)}<h1>\n")
            for db_type,fig in pcaFigure.items():
                htmlOut.write(f"<h2 style='text-align:center'>{db_type.replace('_', ' ')}</h2>")
                htmlFig = fig.to_html(full_html=False, include_plotlyjs=plotly_source)
                htmlOut.write(htmlFig + '\n')
            htmlOut.write('\n</body>\n</html>\n')

    return None


########## Write HTML Files ##########
def write_HTML_files(outpath, sample, figSunburst, FOAM_Charts, KO_Charts):
    # Create HTML Report
    
    # Sunburst Plots
    with open(f"{outpath}/{sample}_sunburst.html", 'w') as htmlOut:
        # Sunburst Plots
        htmlOut.write("\n".join(htmlHeader))
        htmlOut.write('<H1>Sunburst summary of FOAM and KEGG Levels</H1>\n')
        htmlFig = figSunburst.to_html(full_html=False, include_plotlyjs=plotly_source)
        htmlOut.write(htmlFig + '\n')
        htmlOut.write('\n</body>\n</html>\n')


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


########## Write HTML File ##########
def writeHTML(outfile, sample, figSunburst, FOAM_Charts, KO_Charts):
    # Create HTML Report
    
    with open(outfile, 'w') as htmlOut:
        htmlOut.write("\n".join(htmlHeader))
        htmlOut.write(f"<h1>Cerberus Report for '{sample}<h1>\n")

        # Sunburst Plots
        htmlOut.write('<H2>Sunburst summary of FOAM and KEGG Levels</H2>\n')
        htmlFig = figSunburst.to_html(full_html=False, include_plotlyjs=plotly_source)
        htmlOut.write(htmlFig + '\n')

        # FOAM Bar Charts
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
        # KO Bar Charts
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
