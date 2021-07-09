# -*- coding: utf-8 -*-

import os
import shutil
import re

import cerberusVisual


######### Create Report ##########
def createReport(dicTables, dicRollup, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    shutil.copy(f"{config['PATH']}/plotly-2.0.0.min.js", path)

    # Save XLS and CVS reports and HTML files
    for f_name,table in dicTables.items():
        save_path = os.path.join(path, f_name)
        table.to_excel(save_path+'.xlsx', index = False, header=True)
        table.to_csv(save_path+'.csv', index = False, header=True)
        figSunburst = cerberusVisual.graphSunburst(table, path)
        FOAM_Charts, KO_Charts = cerberusVisual.graphBarcharts(dicRollup[f_name])
        outfile = os.path.join(path, f_name+'_report.html')
        writeHTML(outfile, figSunburst, FOAM_Charts, KO_Charts)

    return None


########## Write HTML File ##########
def writeHTML(outfile, figSunburst, FOAM_Charts, KO_Charts):
    # Create HTML Report
    htmlHeader = [
        '<html>',
        '<head><meta charset="utf-8" />',
        '    <script src="plotly-2.0.0.min.js"></script>',
        '</head>',
        '<body>\n']
    
    with open(outfile, 'w') as htmlOut:
        htmlOut.write("\n".join(htmlHeader))
        htmlOut.write("<h1>Report<h1>\n")

        # Sunburst Plots
        htmlFig = figSunburst.to_html(full_html=False, include_plotlyjs=False)
        htmlOut.write(htmlFig + '\n')

        # FOAM Charts
        dicFOAM = {}
        htmlOut.write('<H2>Foam Levels</H2>\n')
        #htmlOut.write('<input type="button" value="Level 1 id="foam-reset"')
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
