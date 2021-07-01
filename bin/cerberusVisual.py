# -*- coding: utf-8 -*-

import os
import shutil
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from functools import reduce
from plotly.offline import plot
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go


######### Create Report ##########
def createReport(table_list, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    fout = open(f"{path}/stdout.txt", 'w')
    ferr = open(f"{path}/stderr.txt", 'w')

    shutil.copy(f"{config['PATH']}/plotly-2.0.0.min.js", path)

    fout.close()
    ferr.close()
    return None


######### Create PCA HTML Graph ##########
def graphPCA(path, table_list):
    filelist = []
    for file in table_list:
        a=file[0]
        y=file[2]
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
        for i, var in enumerate(pca.explained_variance_ratio_ * 100)
    }

    fig = px.scatter_3d(
        X_train, x=0, y=1, z=2, color=res1.index,
        labels=labels
    )

    fig.update_layout({
        'plot_bgcolor' : '#7f7f7f',
        'paper_bgcolor': '#FFFFFF',
        'paper_bgcolor': "rgba(0,0,0,0)",
        'plot_bgcolor' : '#7f7f7f',
    })

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
                zerolinecolor="black",),)
        )

    plot(fig, filename=path+'/'+'PCA_plot'+".html", auto_open=False)
    return


########## Create FOAM and KO HTML Report##########
def create_html(table, config, subdir):
    path = f"{config['DIR_OUT']}/{subdir}"
    os.makedirs(path, exist_ok=True)
    f_name = os.path.basename(path)
    reportFile = os.path.join(path, 'report.html')
    
    xls_path = os.path.join(path, f_name+'_output.xlsx')
    csv_path = os.path.join(path, f_name+'_output.csv')
    table.to_excel(xls_path, index = False, header=True)
    table.to_csv(csv_path, index = False, header=True)

    FT = table[table['Type']=='Foam'].drop(['Type'],axis=1)
    KO = table[table['Type']=='KO'].drop(['Type'],axis=1)

    dfFoam = table[table["Type"]=='Foam']
    dfKO = table[table["Type"]=='KO']
    count = table['Count']
    midpoint = np.average(count, weights=count)*2

    figSunburst = go.Figure()

    figFOAMSunburst = px.sunburst(dfFoam, path=['Type','Layer','Name'], values='Count',
                    color='Count',
                    color_continuous_scale='RdBu',
                    color_continuous_midpoint = midpoint)

    figSunburst.add_trace(go.Sunburst( #TODO: FIX .tolist()
        labels=figFOAMSunburst['data'][0]['labels'],
        parents=figFOAMSunburst['data'][0]['parents'],
        values=figFOAMSunburst['data'][0]['values'],
        ids=figFOAMSunburst['data'][0]['ids'],
        domain=dict(column=0)))

    figKOSunburst=px.sunburst(dfKO, path=['Type','Layer','Name'], values='Count',
                    color='Count',
                    color_continuous_scale='RdBu',
                    color_continuous_midpoint=midpoint)

    figSunburst.add_trace(go.Sunburst( #TODO: FIX .tolist()
        labels=figKOSunburst['data'][0]['labels'],
        parents=figKOSunburst['data'][0]['parents'],
        values=figKOSunburst['data'][0]['values'],
        ids=figKOSunburst['data'][0]['ids'],
        domain=dict(column=1)
    ))

    figSunburst.update_layout(
        grid= dict(columns=2, rows=1),
        margin = dict(t=0, l=0, r=0, b=0)
    )

    # Create FOAM and KO Bar Charts
    foam_Charts = {}
    for i in range(1, 5):
        data = FT[FT['Layer']==i]
        layout = go.Layout (title = f"Foam, Layer {i}")
        
        foam_Charts[i] = go.Figure (layout=layout,
            data=[go.Bar(y=data['Count'], x=data['Name'])])

    KO_Charts = {}
    for i in range(1, 5):
        data = KO[KO['Layer']==i]
        layout = go.Layout (title = f"KO, Layer {i}")
        
        KO_Charts[i] = go.Figure (layout=layout,
            data=[go.Bar(y=data['Count'], x=data['Name'])])


    # Create HTML Report
    htmlHeader = [
        '<html>',
        '<head><meta charset="utf-8" />',
        '    <script src="plotly-2.0.0.min.js"></script>',
        '</head>',
        '<body>\n']
    
    htmlselectOptions = [
        '    <option value="1">Layer 1</option>',
        '    <option value="2">Layer 2</option>',
        '    <option value="3">Layer 3</option>',
        '    <option value="4">Layer 4</option>',
        '</select>\n']
    
    htmlScripts = [
        '<script>',
        '    foam = document.getElementById("foam-layers")',
        '    foam.onchange = function() {',
        '        for (let i=1; i <= 4; i++)',
        '            if (i != foam.value)',
        '               document.getElementById("foam"+i).style.display = "none";',
        '        document.getElementById("foam"+foam.value).style.display = "block";',
        '        var event = document.createEvent("HTMLEvents");',
        '        event.initEvent("resize", true, false);',
        '        document.dispatchEvent(event);',
        '    }',
        '    ko = document.getElementById("ko-layers")',
        '    ko.onchange = function() {',
        '        for (let i=1; i <= 4; i++)',
        '            if (i != ko.value)',
        '               document.getElementById("ko"+i).style.display = "none";',
        '        document.getElementById("ko"+ko.value).style.display = "block";',
        '        var event = document.createEvent("HTMLEvents");',
        '        event.initEvent("resize", true, false);',
        '        document.dispatchEvent(event);',
        '    }',
        '</script>\n']

    with open(reportFile, 'w') as htmlOut:
        htmlOut.write("\n".join(htmlHeader))
        htmlOut.write("<h1>Report<h2>\n")

        # Sunburst Plots
        htmlFig = figSunburst.to_html(full_html=False, include_plotlyjs=False)
        htmlOut.write(htmlFig + '\n')

        # FOAM layers
        htmlOut.write('<H3>Foam Layers</H3>')
        htmlOut.write('<select class="default" id="foam-layers" name="BarGraph">')
        htmlOut.write("\n".join(htmlselectOptions))
        for i, fig in foam_Charts.items():
            htmlFig = fig.to_html(full_html=False, include_plotlyjs=False)
            display = "block" if i==1 else "none"
            htmlFig = htmlFig.replace("<div>", f'<div id="foam{i}" style="display:{display};">', 1)
            htmlOut.write(htmlFig + '\n')

        # KO layers
        htmlOut.write('<H3>KO Layers</H3>')
        htmlOut.write('<select class="default" id="ko-layers" name="BarGraph">')
        htmlOut.write("\n".join(htmlselectOptions))
        for i, fig in KO_Charts.items():
            htmlFig = fig.to_html(full_html=False, include_plotlyjs=False)
            display = "block" if i==1 else "none"
            htmlFig = htmlFig.replace("<div>", f'<div id="ko{i}" style="display:{display};">', 1)
            htmlOut.write(htmlFig + '\n')

        htmlOut.write('\n'.join(htmlScripts))
        htmlOut.write('\n</body>\n</html>\n')

    return
