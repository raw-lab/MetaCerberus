# -*- coding: utf-8 -*-

import os
import numpy as np
from numpy.core.numeric import roll
import pandas as pd
from sklearn.decomposition import PCA
from functools import reduce
from plotly.offline import plot
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go


######### Create PCA Graph ##########
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
    return fig


########## Create Sunburst Figures ##########
def graphSunburst(table, path=None):
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
    if path:
        figSunburst.write_html(file=os.path.join(path, "sunburst.htm"), include_plotlyjs="plotly-2.0.0.min.js")
    return figSunburst


########## Create Bar Chart Figures ##########
def graphBarcharts(fileRollup):
#    if table is not None:
#        FT = table[table['Type']=='Foam'].drop(['Type'],axis=1)
#        KT = table[table['Type']=='KO'].drop(['Type'],axis=1)
#        print("FOAM Hierarchy")
#        FOAM_Charts = createHierarchyFigures(FT)
#        print("KO Hierarchy")
#        KO_Charts = createHierarchyFigures(KT)
#        return FOAM_Charts, KO_Charts

    df = pd.read_csv(fileRollup, names=['Id','Count','Foam','KO'], delimiter='\t')

    # This method avoids chained indexing
    # Reformat data. Splits string into list, strips brackets and quotes
    def helper(x):
        x = x.strip('[]').split("', ")
        return [i.strip("'") for i in x]
    
    # Convert 'Count" column to numeric
    df["Count"] = pd.to_numeric(df["Count"])
    # call helper method to reformat 'FOAM' and 'KO' columns
    df['Foam'] = df['Foam'].apply(helper)
    df['KO'] = df['KO'].apply(helper)

    # Enumerate data
    foamCounts = {}
    for row in range(len(df)):
        for name in df['Foam'][row]:
            if name not in foamCounts:
                foamCounts[name] = df['Count'][row]
            foamCounts[name] += 1
    dictFoam = {}
    # FOAM
    for row in range(len(df['Foam'])):
        for i,name in enumerate(df['Foam'][row], 1):
            if name == '':
                continue
            if i == 1:
                level1 = name
                if name not in dictFoam:
                    dictFoam[level1] = {}, foamCounts[name]
            elif i == 2:
                level2 = name
                if name not in dictFoam[level1][0]:
                    dictFoam[level1][0][level2] = {}, foamCounts[name]
            elif i == 3:
                level3 = name
                if name not in dictFoam[level1][0][level2][0]:
                    dictFoam[level1][0][level2][0][level3] = {}, foamCounts[name]
            else:
                level4 = name
                if name in dictFoam[level1][0][level2][0][level3][0]:
                    print("WARNING: Possible bug???", row)
                dictFoam[level1][0][level2][0][level3][0][level4] = foamCounts[name]
    koCounts = {}
    for row in range(len(df)):
        for name in df['KO'][row]:
            if name not in koCounts:
                koCounts[name] = df['Count'][row]
            koCounts[name] += 1
    dictKO = {}
    # KO
    for row in range(len(df['KO'])):
        for i,name in enumerate(df['KO'][row], 1):
            if name == '':
                continue
            if i == 1:
                level1 = name
                if name not in dictKO:
                    dictKO[level1] = {}, koCounts[name]
            elif i == 2:
                level2 = name
                if name not in dictKO[level1][0]:
                    dictKO[level1][0][level2] = {}, koCounts[name]
            elif i == 3:
                level3 = name
                if name not in dictKO[level1][0][level2][0]:
                    dictKO[level1][0][level2][0][level3] = {}, koCounts[name]
            else:
                level4 = name
                if name in dictKO[level1][0][level2][0][level3][0]:
                    print("WARNING: Possible bug???", row) #TODO: Remove when bugs not found
                dictKO[level1][0][level2][0][level3][0][level4] = koCounts[name]
    
    return createHierarchyFigures(dictFoam), createHierarchyFigures(dictKO)


### Create hierarchy figures from table with levels
def createHierarchyFigures(data):
    ### Helper method for conciseness below ###
    def buildFigure(x, y, title):
        return go.Figure(layout={'title':title,
                #'xaxis_title':"Name",
                'yaxis_title':"Count"},
                data=[go.Bar(x=list(x), y=list(y))])
    
    # Create figures in hierarchy format
    # TODO: This is probably better as a recursive function
    charts = {}
    data1 = {}
    for k1,v1 in data.items():
        #print("\t", k1, v1[1])
        data1[k1] = v1[1]
        data2 = {}
        for k2,v2 in v1[0].items():
            #print("\t\t", k2, v2[1])
            data2[k2] = v2[1]
            data3 = {}
            for k3,v3 in v2[0].items():
                #print("\t\t\t", k3, v3[1])
                data3[k3] = v3[1]
                data4 = {}
                for k4,v4 in v3[0].items():
                    #print("\t\t\t\t", k4, v4)
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
