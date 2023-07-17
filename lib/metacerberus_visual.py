# -*- coding: utf-8 -*-
"""metacerberus_visual.py: Module for creating the plotly figures
"""

def warn(*args, **kwargs):
    #print("args", str(args))
    pass
import warnings
warnings.warn = warn

from pathlib import Path
import numpy as np
import pandas as pd
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
        if not Path(table).exists():
            continue
        df: pd.DataFrame = pd.read_csv(table, sep='\t')

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
    for name,file in dfTables.items():
        df = pd.read_csv(file, sep='\t').set_index('ID', drop=True).T
        if df.empty:
            continue
        df = df.fillna(0).astype(int)
        figs[name] = {}

        # Do PCA
        X = df.copy()

        X.sort_index(inplace=True)

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
        
        # Loading Matrix
        loadings_matrix = pd.DataFrame(
            pca.components_.T * np.sqrt(pca.explained_variance_),
            columns=[f"PC{pc}" for pc in range(1, pca.n_components_+1)], index=df.columns)
        loadings_matrix.reset_index(inplace=True) # Move index to column and re-index
        dfLoadings_matrix = pd.DataFrame()

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
#        figs[name]["Counts_Table"] = df.T.reset_index().rename(columns={'index':'KO'})
        continue

    return figs


########## Create Barchart Figures ##########
def graphBarcharts(rollup_files:dict, dfCounts):
    dfCounts = dfCounts.copy()

    # Set index for our dataframes
    for dbName,table in dfCounts.items():
        if not Path(table).exists():
            continue
        df = pd.read_csv(table, sep='\t')
        dfCounts[dbName] = df.set_index('Name', inplace=False)
    
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
    for dbName,filepath in rollup_files.items():
        try:
            df = pd.read_csv(filepath, sep='\t')
            tree = [dict(), 0]
            for _,row in df.iterrows():
                cols = list()
                for colName,colData in row.items():
                    if colName.startswith('L'):
                        level = colName[1]
                        if colData:
                            cols.append(f"lvl{level}: {colData}")
                if row.Function:
                    cols.append(f"{row.KO}: {row.Function}")
                    buildTree(tree, cols, dbName)
            dbTrees[dbName] = tree[0]
        except: pass

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
        data[k] = v[1]
        chart.update(createBarFigs(v[0], level+1, k)) # updating from empty dict does nothing
    if len(data): #if no data at this level, just return the empty chart{}
        title = f"Level {level}: {name}".strip().strip(':')
        data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True)[:BAR_LIMIT])
        fig = go.Figure( # Create the figure of this level's data
            layout={'title':title,
                'yaxis_title':"KO Count"}, # TODO: Remove KO References from code
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
