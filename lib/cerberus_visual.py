# -*- coding: utf-8 -*-
"""cerberus_visual.py: Module for creating the plotly figures
"""

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go

# global vars
BAR_LIMIT = 10
SUN_LIMIT = 15


########## Create Sunburst Figures ##########
def graphSunburst(tables):
    figs = {}
    for dbName,table in tables.items():
        df: pd.DataFrame = table.copy()

        # Filter top MAX_DEPTH
        try:
            levels = int(max(df[df.Level != 'Function'].Level))
            dfLevels = []
            for i in range(1,levels+1):
                filter = df['Level']==str(i)
                dfLevels.append( df[filter].sort_values(by='Count', ascending=False, inplace=False).head(SUN_LIMIT) )
            filter = df['Level']=='Function'
            dfLevels.append( df[df['Level']=='Function'].sort_values(by='Count', ascending=False, inplace=False).head(SUN_LIMIT) )
            df = pd.concat(dfLevels)
        except:
            continue

        # Add the Database Type for parent
        df['Type'] = dbName

        # Create Sunburst Figure
        sun = px.sunburst(
            df, path = ['Type','Level','Name'],
            values = 'Count',
            color = 'Count',
            color_continuous_scale = 'RdBu'
        )
        sun.update_traces(textfont=dict(family=['Arial Black', 'Arial'],size=[15]))
        figs[dbName] = sun

    return figs


######### Create PCA Graph ##########
def graphPCA(dfTables:dict):

    # Run PCA and add to Plots
    figs = {}
    for name,df in dfTables.items():
        if df.empty:
            continue
        df = df.fillna(0).astype(int)
        figs[name] = {}

        # Do PCA
        X = df.copy()
        scaler = StandardScaler()
        scaler.fit(X)
        X_scaled = scaler.transform(X)

        pca = PCA()
        X_pca = pca.fit_transform(X_scaled)

        # Loadings table
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=[f"PC{pc}" for pc in range(1, pca.n_components_+1)], index=df.columns)
        loadings.reset_index(inplace=True) # Move index to column and re-index
        dfLoadings = pd.DataFrame()
        dfLoadings[['KO-ID','Name']] = loadings['index'].str.split(':', n=1, expand=True)
        dfLoadings = pd.merge(dfLoadings, loadings, left_index=True, right_index=True)
        dfLoadings.drop(labels=['index'], axis=1, inplace=True)
        
        # Loading Matrix
        loadings_matrix = pd.DataFrame(
            pca.components_.T * np.sqrt(pca.explained_variance_),
            columns=[f"PC{pc}" for pc in range(1, pca.n_components_+1)], index=df.columns)
        loadings_matrix.reset_index(inplace=True) # Move index to column and re-index
        dfLoadings_matrix = pd.DataFrame()
        dfLoadings_matrix[['KO-ID','Name']] = loadings_matrix['index'].str.split(':', n=1, expand=True)
        dfLoadings_matrix = pd.merge(dfLoadings_matrix, loadings_matrix, left_index=True, right_index=True)
        dfLoadings_matrix.drop(labels=['index'], axis=1, inplace=True)

        # Create Scree Plot
        figScree = px.bar(
            x=range(1, pca.n_components_+1),
            y=np.round(pca.explained_variance_ratio_*100, decimals=2),
            labels={'x':'Principal Component', 'y':'Percent Variance Explained'},
            title="Scree Plot"
        )
        figScree.update_xaxes(dtick=1)
        
        # Create 3D Plot
        labels = {str(i): f"PC {str(i+1)} ({var:.2f}%)"
            for i,var in enumerate(pca.explained_variance_ratio_ * 100)}

        if len(labels) > 2:
            fig3d = px.scatter_3d(
                X_pca, x=0, y=1, z=2, color=X.index,
                labels=labels)
            fig3d.update_layout(scene = dict(
                    xaxis = dict(
                        backgroundcolor="White",
                        gridcolor="LightGray",
                        showbackground=False,
                        zerolinecolor="LightGray"
                        ),
                    yaxis = dict(
                        backgroundcolor="White",
                        gridcolor="LightGray",
                        showbackground=False,
                        zerolinecolor="LightGray"
                        ),
                    zaxis = dict(
                        backgroundcolor="White",
                        gridcolor="LightGray",
                        showbackground=False,
                        zerolinecolor="LightGray"
                        ),
                    #width=700,
                    #margin=dict(
                    #r=10, l=10,
                    #b=10, t=10
                  ))
        else:
            print("WARNING: Insufficient data in", name, "results for 3D PCA Plot")
            fig3d = None


        # Add Figures to Dictionary
        # (Key is displayed in the HTML Report and file names)
        if fig3d:
            figs[name]["PCA"] = fig3d
            figs[name]["Scree_Plot"] = figScree
        figs[name]["Loadings"] = dfLoadings
        figs[name]["Loading_Matrix"] = loadings_matrix
        figs[name]["Counts_Table"] = df.T.reset_index().rename(columns={'index':'KO'})
        continue

    return figs


########## Create Bar Chart Figures ##########
def graphBarcharts(dfRollup, dfCounts):
    dfCounts = dfCounts.copy()

    # Set index for our dataframes
    for dbName,df in dfCounts.items():
        dfCounts[dbName] = df.set_index('Name', inplace=False)
    
    # Recursively add branches to tree    
    def buildTree(branch, cols, dbName):
        if cols:
            name = cols.pop(0)
            while not name:
                 name = cols.pop(0)
            if name not in branch[0]:
                branch[0][name] = ({}, 0) if not name else ({}, dfCounts[dbName].loc[name,'Count'])
            #else:
                #print("WARNING: duplicate line in rollup: ", dbName, name, cols) #TODO: Remove when bugs not found
            buildTree(branch[0][name], cols, dbName)

    # Add rows to tree
    dbTrees = dict()
    for dbName,df in dfRollup.items():
        tree = [dict(), 0]
        for _,row in df.iterrows():
            cols = list()
            for colName,colData in row.iteritems():
                if colName.startswith('L'):
                    level = colName[1]
                    if colData:
                        cols.append(f"lvl{level}: {colData}")
            if row.Function:
                cols.append(f"{row.KO}: {row.Function}")
                buildTree(tree, cols, dbName)
        dbTrees[dbName] = tree[0]

    # Create Figures
    figs = dict()
    for dbName,tree in dbTrees.items():
        figs[dbName] = createBarFigs(tree)

    return figs, dbTrees


##### Create Barchart Figures #####
def createBarFigs(tree, level=1, name=""):
    chart = {}
    data = {}
    for k,v in tree.items():
        #print("\t"*level, k, ' ', v[1], sep='')
        data[k] = v[1]
        chart.update(createBarFigs(v[0], level+1, k)) # updating from empty dict does nothing
    if len(data): #if no data at this level, just return the empty chart{}
        title = f"Level {level}: {name}".strip().strip(':')
        data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True)[:BAR_LIMIT])
        fig = go.Figure( # Create the figure of this level's data
            layout={'title':title,
                'yaxis_title':"KO Count"},
            data=[go.Bar(x=list(data.keys()), y=list(data.values()))]
            )
        if max(data.values()) < 20: # to remove decimals from graph with low counts, let plotly decide tick marks otherwise
            fig.update_yaxes(dtick=1)
        fig.update_layout(dict(plot_bgcolor='White', paper_bgcolor='White'))
        fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
        fig.update_yaxes( showline=True, linewidth=2, linecolor='black',
                                    showgrid=True, gridwidth=1, gridcolor='LightGray')
        chart[title] = fig
    return chart
