# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from functools import reduce
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
#import plotly.subplots as sp


########## Create Sunburst Figures ##########
def graphSunburst(tables):
    figs = {}
    for name,table in tables.items():
        table = table.copy()
        table.insert(0,'Type',name)
        sun = px.sunburst(
            table, path = ['Type','Level','Name'],
            values = 'Count',
            color = 'Count',
            color_continuous_scale = 'RdBu',
        )
        sun.update_traces(textfont=dict(size=[20]))
        figs[name] = sun

    return figs


######### Create PCA Graph ##########
def graphPCA(table_list):
    if len(table_list) < 3:
        print("NOTE: PCA Tables and Combined report created only when there are at least three samples.\n")
        return {}

    dfTables = {}    
    for sample,tables in table_list.items():
        for name,table in tables.items():
            X = table.drop(table[table['Level']<4].index, inplace=False).copy()
            row = dict(zip(X['Name'].tolist(), X['Count'].tolist()))
            row = pd.Series(row, name=sample)
            if name not in dfTables:
                dfTables[name] = pd.DataFrame()
            dfTables[name] = dfTables[name].append(row)

    # Run PCA and add to Plots
    figPCA = {}
    figs = {}
    for name,df in dfTables.items():
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
            labels={'x':'Principal Component', 'y':'Percent Variance Explained'}
        )
        figScree.update_xaxes(dtick=1)
        
        # Create 3D Plot
        labels = {str(i): f"PC {str(i+1)} ({var:.2f}%)"
            for i,var in enumerate(pca.explained_variance_ratio_ * 100)}

        if len(labels) > 2:
            fig3d = px.scatter_3d(
                X_pca, x=0, y=1, z=2, color=X.index,
                #title=data_type,
                labels=labels)
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
        figs[name]["PCA_Table"] = df.T.reset_index().rename(columns={'index':'KO'})
        continue

    return figs#figPCA


########## Create Bar Chart Figures ##########
def graphBarcharts(key, rollupFiles):
    #TODO: restructure code to avoid loading rollup files and counting twice (fist in parser.py)
    df_FOAM = pd.read_csv(rollupFiles[0], names=['Id','Count','Info'], delimiter='\t')
    df_KEGG = pd.read_csv(rollupFiles[1], names=['Id','Count','Info'], delimiter='\t')

    # Reformat data. This lambda method avoids chained indexing
    # Splits string into list, strips brackets and quotes
    helper = lambda x : [i.strip("'") for i in x.strip('[]').split("', ")]
    # call helper method to reformat 'FOAM' and 'KO' columns
    df_FOAM['Info'] = df_FOAM['Info'].apply(helper)
    df_KEGG['Info'] = df_KEGG['Info'].apply(helper)
    # Convert 'Count" column to numeric
    df_FOAM["Count"] = pd.to_numeric(df_FOAM["Count"])
    df_KEGG["Count"] = pd.to_numeric(df_KEGG["Count"])


    # Enumerate data
    # TODO: Refactor this
    def countLevels(df):
        dictCount = {}
        for row in range(len(df)):
            ko_id = df['Id'][row]
            for i,name in enumerate(df['Info'][row],1):
                if name == '':
                    continue
                if i == 4:
                    name = f"{ko_id}: {name}"
                if name not in dictCount:
                    dictCount[name] = 0
                dictCount[name] += df['Count'][row]
        return dictCount
    foamCounts = countLevels(df_FOAM)
    keggCounts = countLevels(df_KEGG)
    
    # FOAM
    dictFoam = {}
    for row in range(len(df_FOAM)):
        ko_id = df_FOAM['Id'][row]
        for i,name in enumerate(df_FOAM['Info'][row], 1):
            if name == '':
                continue
            if i == 4:
                name = f"{ko_id}: {name}"
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
                if level4 not in dictFoam[level1][0][level2][0][level3][0]:
                    dictFoam[level1][0][level2][0][level3][0][level4] = [{}, foamCounts[name]]
                else:
                    dictFoam[level1][0][level2][0][level3][0][level4][1] += foamCounts[name]
                    print("WARNING: duplicate line in rollup: FOAM: ", key, row, name, df_FOAM['Info'][row]) #TODO: Remove when bugs not found

    # KO
    dictKO = {}
    for row in range(len(df_KEGG)):
        ko_id = df_KEGG['Id'][row]
        for i,name in enumerate(df_KEGG['Info'][row], 1):
            if name == '':
                continue
            if i == 4:
                name = f"{ko_id}: {name}"
            if i == 1:
                level1 = name
                if name not in dictKO:
                    dictKO[level1] = {}, keggCounts[name]
            elif i == 2:
                level2 = name
                if name not in dictKO[level1][0]:
                    dictKO[level1][0][level2] = {}, keggCounts[name]
            elif i == 3:
                level3 = name
                if name not in dictKO[level1][0][level2][0]:
                    dictKO[level1][0][level2][0][level3] = {}, keggCounts[name]
            else:
                level4 = name
                if level4 not in dictKO[level1][0][level2][0][level3][0]:
                    dictKO[level1][0][level2][0][level3][0][level4] = [{}, keggCounts[name]]
                else:
                    dictKO[level1][0][level2][0][level3][0][level4][1] += keggCounts[name]
                    print("WARNING: duplicate line in rollup: KEGG: ", key, row, name, df_KEGG['Info'][row]) #TODO: Remove when bugs not found

    return createBarFigs(dictFoam), createBarFigs(dictKO), {"FOAM":dictFoam, "KEGG":dictKO}


##### Create Barchart Figures #####
def createBarFigs(data, level=1, name=""):
    chart = {}
    d = {}
    for k,v in data.items():
        #print("\t"*level, k, ' ', v[1], sep='')
        d[k] = v[1]
        chart.update(createBarFigs(v[0], level+1, k)) # updating from empty dic does nothing
    if len(d): #if no data at this level, just return the empty chart{}
        title = f"Level {level}: {name}".strip().strip(':')
        fig = go.Figure( # Create the figure of this level's data
            layout={'title':title,
                'yaxis_title':"KO Count"},
            data=[go.Bar(x=list(d.keys()), y=list(d.values()))])
        if max(d.values()) < 20: # to remove decimals from graph with low counts
            fig.update_yaxes(dtick=1)
        chart[title] = fig
    return chart
