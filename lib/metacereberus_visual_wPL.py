# -*- coding: utf-8 -*-
"""metacerberus_visual.py: Module for creating the plotly figures
"""

def warn(*args, **kwargs):
    #print("args", str(args))
    pass
import warnings
warnings.warn = warn

import re
import numpy as np
import pandas as pd
import polars as pl
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
    for dbName, table in tables.items():
        df: pl.DataFrame = pl.from_csv(table, delimiter='\t')

        # Filter top MAX_DEPTH
        try:
            levels = int(max(df[df['Level'] != 'Function']['Level']))
            dfLevels = []
            for i in range(1, levels+1):
                filter = df['Level'] == str(i)
                dfLevels.append(df[filter].sort('Count', reverse=True).head(SUN_LIMIT))
            filter = df['Level'] == 'Function'
            dfLevels.append(df[df['Level'] == 'Function'].sort('Count', reverse=True).head(SUN_LIMIT))
            df = pl.concat(dfLevels)
        except:
            continue

        # Add the Database Type for parent
        df = df.with_column('Type', pl.lazy(lambda df: np.repeat(dbName, len(df))))

        # Create Sunburst Figure
        sun = px.sunburst(
            df.to_pandas(), path=['Type', 'Level', 'Name'],
            values='Count',
            color='Count',
            color_continuous_scale='RdBu'
        )
        sun.update_traces(textfont=dict(family=['Arial Black', 'Arial'], size=[15]))
        figs[dbName] = sun

    return figs


######### Create PCA Graph ##########
def graphPCA(dfTables:dict):
    # Run PCA and add to Plots
    figs = {}
    for name,file in dfTables.items():
        df = pl.read_csv(file, delimiter='\t').set_index('KO', drop=True).transpose()
        if df.shape[0] == 0:
            continue
        df = df.fill_null(0).to_int()
        figs[name] = {}

        # Do PCA
        X = df.copy()

        # Sort and rename index (if appropriate)
        types = set()
        for x in X.index:
            types.add(re.match(r'([A-Za-z]+_)', x).groups(1))
        if len(types) == 1:
            X.index = df.index.map(lambda x: re.sub(r'([A-Za-z]+_)', '', x))

        X.sort_index(inplace=True)

        scaler = StandardScaler()
        scaler.fit(X)
        X_scaled = scaler.transform(X)

        pca = PCA()
        X_pca = pca.fit_transform(X_scaled)

        # Loadings table
        loadings = pl.DataFrame(
            pca.components_.T,
            columns=[f"PC{pc}" for pc in range(1, pca.n_components_+1)], index=df.columns)
        loadings.reset_index(drop=True, inplace=True) # Move index to column and re-index
        dfLoadings = pl.DataFrame()

        # Loading Matrix
        loadings_matrix = pl.DataFrame(
            pca.components_.T * np.sqrt(pca.explained_variance_),
            columns=[f"PC{pc}" for pc in range(1, pca.n_components_+1)], index=df.columns)
        loadings_matrix.reset_index(drop=True, inplace=True) # Move index to column and re-index
        dfLoadings_matrix = pl.DataFrame()

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
        continue

    return figs


########## Create Bar Chart Figures ##########
def graphBarcharts(rollup_files:dict, dfCounts):
    dfCounts = dfCounts.copy()

    # Set index for our dataframes
    for dbName, table in dfCounts.items():
        df = pl.read_csv(table, delimiter='\t')
        dfCounts[dbName] = df.set_index('Name', in_place=False)
    
    # Recursively add branches to tree    
    def buildTree(branch, cols, dbName):
        if cols:
            name = cols.pop(0)
            while not name:
                name = cols.pop(0)
            if name not in branch[0]:
                count = 0 if not name else dfCounts[dbName].loc[name, 'Count']
                branch[0][name] = ({}, count)
            buildTree(branch[0][name], cols, dbName)

    # Add rows to tree
    dbTrees = dict()
    for dbName, filepath in rollup_files.items():
        df = pl.read_csv(filepath, delimiter='\t')
        tree = [dict(), 0]
        for _, row in df.iterrows():
            cols = list()
            for colName, colData in row.items():
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
    for dbName, tree in dbTrees.items():
        figs[dbName] = createBarFigs(tree)

    return figs, dbTrees


##### Create Barchart Figures #####
def graphBarcharts(rollup_files: dict, dfCounts):
    dfCounts = dfCounts.copy()

    # Set index for our dataframes
    for dbName, table in dfCounts.items():
        df = pl.read_csv(table, delimiter='\t')
        dfCounts[dbName] = df.set_index('Name', keep=False)

    # Recursively add branches to tree    
    def buildTree(branch, cols, dbName):
        if cols:
            name = cols.pop(0)
            while not name:
                 name = cols.pop(0)
            if name not in branch[0]:
                branch[0][name] = ({}, 0) if not name else ({}, dfCounts[dbName].loc[name,'Count'])
            buildTree(branch[0][name], cols, dbName)

    # Add rows to tree
    dbTrees = dict()
    for dbName, filepath in rollup_files.items():
        df = pl.read_csv(filepath, delimiter='\t')
        tree = [dict(), 0]
        for _, row in df.iterrows():
            cols = list()
            for colName, colData in row.items():
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
    for dbName, tree in dbTrees.items():
        figs[dbName] = createBarFigs(tree)

    return figs, dbTrees


def createBarFigs(tree, level=1, name=""):
    chart = {}
    data = {}
    for k, v in tree.items():
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
