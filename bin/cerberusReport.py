# -*- coding: utf-8 -*-

import os
import shutil
import re
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from functools import reduce
from plotly.offline import plot
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go


######### Create Report ##########
def createReport(dicTables, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)

    shutil.copy(f"{config['PATH']}/plotly-2.0.0.min.js", path)

    # Save XLS and CVS reports
    for f_name,table in dicTables.items():
        save_path = os.path.join(path, f_name)
        table.to_excel(save_path+'.xlsx', index = False, header=True)
        table.to_csv(save_path+'.csv', index = False, header=True)
        figSunburst, FOAM_Charts, KO_Charts = createFigures(table)
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
    

######### Create PCA HTML Graph ##########
def graphPCA(path, table_list):
    filelist = []
    for file in table_list:
        print(file)
        a = file.iloc[0]
        y = file.iloc[2]
        a = a[['Name','Count']]
        a = a.rename(columns={'Count':y })
        filelist.append(a)

    print(filelist)
    df_merged = reduce(lambda  left,
                        right: pd.merge(left,
                        right,
                        on=['Name'],
                        how='outer'), filelist)
    result = df_merged.replace(np.nan, 0)
    pivoted = result.T
    res = pivoted.rename(columns=pivoted.iloc[0])
    res1 = res.drop(res.index[0])
    pca = PCA(n_components=3, svd_solver='randomized')
    X_train = pca.fit_transform(res1)
    labels = {
        str(i): ('PC '+str(i+1)+' (' +'%.1f'+ '%s'+')') % (var,'%')
        for i, var in enumerate(pca.explained_variance_ratio_ * 100)}

    fig = px.scatter_3d(
        X_train, x=0, y=1, z=2, color=res1.index,
        labels=labels)

    fig.update_layout({
        'plot_bgcolor' : '#7f7f7f',
        'paper_bgcolor': '#FFFFFF',
        'paper_bgcolor': "rgba(0,0,0,0)",
        'plot_bgcolor' : '#7f7f7f'})

    fig.update_layout(scene = dict(
            xaxis = dict(
                backgroundcolor="rgb(255,255, 255)",
                gridcolor="black",
                showbackground=True,
                zerolinecolor="black",),
            yaxis = dict(
                backgroundcolor="rgb(255,255, 255)",
                gridcolor="black",
                showbackground=True,
                zerolinecolor="black"),
            zaxis = dict(
                backgroundcolor="rgb(255,255, 255)",
                gridcolor="black",
                showbackground=True,
                zerolinecolor="black")))

    plot(fig, filename=path+'/PCA_plot.html', auto_open=False)
    return


########## Create Figures ##########
def createFigures(table):
    dfFoam = table[table["Type"]=='Foam']
    dfKO = table[table["Type"]=='KO']
    count = table['Count']
    midpoint = np.average(count, weights=count)*2

    dfKO = dfKO.replace("KO", "KEGG")

    # Create Sunburst Figures
    figSunburst = go.Figure(layout=dict(
        grid = dict(columns=2, rows=1),
        margin = dict(t=0, l=0, r=0, b=0)))
    figSunburst.update_traces(font=dict(size=[40]))
    col=0
    for df in [dfFoam, dfKO]:
        sun = px.sunburst(df, path = ['Type','Level','Name'],
            values = 'Count', color = 'Count',
            color_continuous_scale = 'RdBu',
            color_continuous_midpoint = midpoint)
        sun.update_traces(textfont=dict(size=[40]))
        figSunburst.add_trace(go.Sunburst(
            labels = sun['data'][0]['labels'],
            parents = sun['data'][0]['parents'],
            values = sun['data'][0]['values'],
            ids = sun['data'][0]['ids'],
            domain = dict(column=col),
            textfont = dict(size=[40])
            ))
        sun.update_traces(textfont=dict(size=[40]))
        figSunburst.update_traces(textfont=dict(size=[40]))
        col += 1
    figSunburst.update_traces(textfont=dict(size=[40]))

    # Create FOAM and KO Bar Charts

    FT = table[table['Type']=='Foam'].drop(['Type'],axis=1)
    KT = table[table['Type']=='KO'].drop(['Type'],axis=1)
    FOAM_Charts = createHierarchyFigures(FT)
    KO_Charts = createHierarchyFigures(KT)

    return figSunburst, FOAM_Charts, KO_Charts


### Create hierarchy figures from table with levels
def createHierarchyFigures(tbl):
    idxName = tbl.columns.get_loc("Name")
    idxLevel = tbl.columns.get_loc("Level")
    idxCount = tbl.columns.get_loc("Count")
    tbl = tbl.values.tolist()

    data = {}
    for row in tbl:
        if row[idxLevel] == 1:
            level1 = row[idxName]
            data[level1] = {}, row[idxCount]
        elif row[idxLevel] == 2:
            level2 = row[idxName]
            data[level1][0][level2] = {}, row[idxCount]
        elif row[idxLevel] == 3:
            level3 = row[idxName]
            data[level1][0][level2][0][level3] = {}, row[idxCount]
        else:
            level4 = row[idxName]
            print(level1, level2, level3, level4)
            data[level1][0][level2][0][level3][0][level4] = row[idxCount]

    ### Helper method for conciseness below ###
    def buildFigure(x, y, title):
        return go.Figure(layout={'title':title,
                #'xaxis_title':"Name",
                'yaxis_title':"KO Count"},
                data=[go.Bar(x=list(x), y=list(y))])
    
    # Gather levels in hierarchy format
    # TODO: This is probably better as a recursive function and/or incorporated with previous loop
    charts = {}
    data1 = {}
    for k1,v1 in data.items():
        data1[k1] = v1[1]
        data2 = {}
        for k2,v2 in v1[0].items():
            data2[k2] = v2[1]
            data3 = {}
            for k3,v3 in v2[0].items():
                data3[k3] = v3[1]
                data4 = {}
                for k4,v4 in v3[0].items():
                    data4[k4] = v4
                if len(data4):
                    title = f"Level 4: {k3}"
                    charts[title] = buildFigure(data4.keys(), data4.values(), title)
            if len(data3):
                title = f"Level 3: {k2}"
                charts[title] = buildFigure(data3.keys(), data3.values(), title)
        if len(data2):
            title = f"Level 2: {k1}"
            charts[title] = buildFigure(data2.keys(), data2.values(), title)
    if len(data1):
        title = "Level 1"
        charts[title] = buildFigure(data1.keys(), data1.values(), title)
    return charts
