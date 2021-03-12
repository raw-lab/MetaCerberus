import os
from os.path import isfile, join
import sys
import csv
import subprocess
import csv
import pandas as pd
import plotly
import numpy as np
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash_table
import datetime
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import argparse 
from plotly.offline import plot
import webbrowser
from threading import Timer
import time


import plotly.graph_objs as go
from plotly.offline import plot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px
from sklearn.decomposition import PCA
from functools import reduce
import matplotlib.pyplot as plt 
# import plotly.graph_objs as go
import glob
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import os









app = dash.Dash(__name__)
def preprocess_data(path,file_name):
    file=file_name.split('/')[-1]
    f_name, f_ext = os.path.splitext(file)

    reader = csv.reader(open(file_name, "r"), delimiter="\t")
    df=pd.DataFrame(reader)
    if df.empty:
        return
    df.columns=['Id','Count','Foam','KO']
    dict1={}
    dict2={}
    for i in range(len(df['Foam'])):
        df['Count'][i]=int(df['Count'][i])
        df['Foam'][i] = df['Foam'][i].strip('][').split("', ")
        df['KO'][i] = df['KO'][i].strip('][').split("', ")
        for m in ['Foam','KO']:
            for j in range(len(df[m][i])):
                if df[m][i][j][-1]!="'":
                    df[m][i][j]=df[m][i][j][1:]
                    continue
                if df[m][i][j][0]!="'":
                    df[m][i][j]=df[m][i][j][:-1]
                    continue

                df[m][i][j]=df[m][i][j][1:-1]

    for i in range(len(df)):
        for j in range(len(df['Foam'][i])):
            dict1[df['Foam'][i][j]]=dict1.get(df['Foam'][i][j],["",0])
            n,m=dict1[df['Foam'][i][j]]
            dict1[df['Foam'][i][j]]=[j+1,m+df['Count'][i]]
        for j in range(len(df['KO'][i])):
            dict2[df['KO'][i][j]]=dict2.get(df['KO'][i][j],["",0])
            n,m=dict2[df['KO'][i][j]]
            dict2[df['KO'][i][j]]=[j+1,m+df['Count'][i]]
    a={'Type':'Foam','Name':list(dict1.keys()),'Layer':[x[0] for x in dict1.values()],'Count':[x[1] for x in dict1.values()]}
    FT=pd.DataFrame(data=a)

    a2={'Type':'KO','Name':list(dict2.keys()),'Layer':[x[0] for x in dict2.values()],'Count':[x[1] for x in dict2.values()]}
    KT=pd.DataFrame(data=a2)
    table=pd.concat([FT,KT])

    table.drop(table[table['Name']==''].index,inplace=True)
    table.drop(table[table['Name']=="'"].index,inplace=True)
    table.drop(table[table['Name']=='NA'].index,inplace=True)
    table_list.append([table,path,f_name])
    return table
def new_visual():

    
    layout1 = go.Layout(
        title="My Dash Graph",
        height=1500,
#         paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,0,0,0)',
        # grid= dict(columns=2, rows=2)
        )
    fig2 =go.Figure(layout=layout1)
    column=0
    # rows=int((len(table_list)+1)/2)
    row=-1
    for t in table_list:
        if column==0:
            row+=1
        table=t[0]
        fig23=px.sunburst(table, path=['Type','Layer','Name'], values='Count',
                color='Count',
                color_continuous_scale='RdBu',
                color_continuous_midpoint=np.average(table['Count'], weights=table['Count'])*2,
                #   width=1800,
                #   height=900
                        )
        fig2.add_trace(go.Sunburst(
            labels=fig23['data'][0]['labels'].tolist(),
            parents=fig23['data'][0]['parents'].tolist(),
            values=fig23['data'][0]['values'].tolist(),
            ids=fig23['data'][0]['ids'].tolist(),
            domain=dict(column=column,row=row)
        
        ))
        column=abs(column-1)

    fig2.update_layout(
        grid= dict(columns=2, rows=row+1),
        margin = dict(t=0, l=0, r=0, b=0)
    )
    plot(fig2, filename=path+'/'+'sunburst_plot'+".html", auto_open=False)


    tables=[]
    options_bar=[]
    for i,t in enumerate(table_list):
        table=t[0]
        mn=t[1]
        f_name=t[2]
        FT=table[table['Type']=='Foam'].drop(['Type'],axis=1)
        KO=table[table['Type']=='KO'].drop(['Type'],axis=1)
        FT_main=FT.copy()
        KO_main=KO.copy()
        FT1=FT[FT['Layer']==1].sort_values(by=['Count'],ascending=False).head(10)
        FT2=FT[FT['Layer']==2].sort_values(by=['Count'],ascending=False).head(10)
        FT3=FT[FT['Layer']==3].sort_values(by=['Count'],ascending=False).head(10)
        FT4=FT[FT['Layer']==4].sort_values(by=['Count'],ascending=False).head(10)

        KO1=KO[KO['Layer']==1].sort_values(by=['Count'],ascending=False).head(10)
        KO2=KO[KO['Layer']==2].sort_values(by=['Count'],ascending=False).head(10)
        KO3=KO[KO['Layer']==3].sort_values(by=['Count'],ascending=False).head(10)
        KO4=KO[KO['Layer']==4].sort_values(by=['Count'],ascending=False).head(10)
        FT=pd.concat([FT1,FT2,FT3,FT4])
        KO=pd.concat([KO1,KO2,KO3,KO4])
        f_path=os.path.join(mn + os.sep,f_name+'_output.xlsx')
        csv_path=os.path.join(mn + os.sep, f_name+'_output')
        table.to_excel (f_path, index = False, header=True)
        table.to_csv (csv_path, index = False, header=True)
        tables.append([table,FT,FT_main,KO,KO_main])
        options_bar.append({"label": t[2], "value": i})
    app.layout = html.Div(
    #     style={'backgroundColor': colors['background']},
        children=[
        html.H1("Cerberus Outputs", style={'text-align': 'center'}),
        dcc.Graph(id='sunburst', figure=fig2),

        html.H3("Select Type and Layer from the below Dropdowns", style={'text-align': 'left'}),
        dcc.Dropdown(id="slct_number",
                    options=options_bar,
                    multi=False,
                    value=0,
                    style={'width': "40%"}
                    ),
        dcc.Dropdown(id="slct_Name",
                    options=[
                        {"label": "Foam", "value": 'Foam'},
                        {"label": "KO", "value": 'KO'}],
                    multi=False,
                    value='Foam',
                    style={'width': "40%"}
                    ),
        dcc.Dropdown(id="slct_Layer",
                    options=[
                        {"label": "Layer1", "value": 1},
                        {"label": "Layer2", "value": 2},
                        {"label": "Layer3", "value": 3},
                        {"label": "Layer4", "value": 4}],
                    multi=False,
                    value=1,
                    style={'width': "40%"}
                    ),
        html.Div(id='output_container', children=[]),
        html.Br(),
    #     dcc.Graph(id='pie_chart', figure={}),
        dcc.Graph(id='my_bee_map', figure={}),
        html.Br(),

    ])


    # ------------------------------------------------------------------------------
    # Connect the Plotly graphs with Dash Components
    @app.callback(
        [
            Output(component_id='output_container', component_property='children'),
    #      Output(component_id='pie_chart', component_property='figure'),
        Output(component_id='my_bee_map', component_property='figure')],
        [Input(component_id='slct_Name', component_property='value'),Input(component_id='slct_Layer', component_property='value'),Input(component_id='slct_number', component_property='value')]
    )
    def update_graph(x,y,z):
        table_val=tables[z]
        FT=table_val[1]
        FT_main=table_val[2]
        KO=table_val[3]
        KO_main=table_val[4]
        container = "The year chosen by user was: {} {}".format(x,y)
        if x=='Foam':
            dff=FT.copy()
            dff_main=FT_main.copy()
        
        if x=='KO':
            dff=KO.copy()
            dff_main=KO_main.copy()
        dff=dff[dff['Layer']==y]
        dff_main=dff_main[dff_main['Layer']==y]
    #     fig1 = go.Figure(data=[go.Pie(labels=dff_main['Name'], values=dff_main['Count'],hole=0.5)])
        layout = go.Layout(
            title="My Dash Graph",
            height=700,
    #         paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,0,0,0)'
            )
        fig=go.Figure(
            data=[go.Bar(y=dff['Count'],x=dff['Name'])],
            layout=layout
        )

        
        return container, fig



    # app = dash.Dash(__name__) 

    port = 8050 

    def open_browser():
        webbrowser.open_new("http://localhost:{}".format(port))

    Timer(1, open_browser).start()
    app.run_server(port=port)


def output_visual(path,f_name,FT,KO,FT_main,KO_main,table):
    df1 = table[table["Type"]=='Foam']
    df4=table[table["Type"]=='KO']
    df3=table
    fig23=px.sunburst(df1, path=['Type','Layer','Name'], values='Count',
                    color='Count',
                    color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df3['Count'], weights=df3['Count'])*2,
    #                   width=1800,
    #                   height=900
                            )
    # fig12=go.Figure(px.sunburst(lables = df1.Layer,
    #                         parents = df1.Name,
    #                             domain=dict(column=0)
    # #                   width=1800,
    # #                   height=900
    #               ))
    layout1 = go.Layout(
            title="My Dash Graph",
            height=700,
    #         paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,0,0,0)'
            )
    fig2 =go.Figure(layout=layout1)
    fig2.add_trace(go.Sunburst(
        labels=fig23['data'][0]['labels'].tolist(),
        parents=fig23['data'][0]['parents'].tolist(),
        values=fig23['data'][0]['values'].tolist(),
        ids=fig23['data'][0]['ids'].tolist(),
        domain=dict(column=0),
        
    ))
    fig23=px.sunburst(df4, path=['Type','Layer','Name'], values='Count',
                    color='Count',
                    color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df3['Count'], weights=df3['Count'])*2,
                    width=900,
                    height=450
                            )
    fig2.add_trace(go.Sunburst(
        labels=fig23['data'][0]['labels'].tolist(),
        parents=fig23['data'][0]['parents'].tolist(),
        values=fig23['data'][0]['values'].tolist(),
        ids=fig23['data'][0]['ids'].tolist(),
        domain=dict(column=1)
    ))
    fig2.update_layout(
        grid= dict(columns=2, rows=1),
        margin = dict(t=0, l=0, r=0, b=0)
    )
    plot(fig2, filename=path+'/'+'sunburst_plot'+".html", auto_open=False)
    # fig2.add_trace(px.sunburst(df3, path=['Type', 'Layer','Name'], values='Count',
    #                   color='Count',
    #                   color_continuous_scale='RdBu',
    #                   color_continuous_midpoint=np.average(df3['Count'], weights=df3['Count'])*2,
    # #                   width=1800,
    # #                   height=900
    #                           ))
    # fig2.update_layout(
    #     grid= dict(columns=2, rows=1),
    #     margin = dict(t=0, l=0, r=0, b=0)
    # )
    app.layout = html.Div(
    #     style={'backgroundColor': colors['background']},
        children=[
        html.H1("Cerberus Outputs", style={'text-align': 'center'}),
        dcc.Graph(id='sunburst', figure=fig2),

        html.H3("Select Type and Layer from the below Dropdowns", style={'text-align': 'left'}),
        dcc.Dropdown(id="slct_Name",
                    options=[
                        {"label": "Foam", "value": 'Foam'},
                        {"label": "KO", "value": 'KO'}],
                    multi=False,
                    value='Foam',
                    style={'width': "40%"}
                    ),
        dcc.Dropdown(id="slct_Layer",
                    options=[
                        {"label": "Layer1", "value": 1},
                        {"label": "Layer2", "value": 2},
                        {"label": "Layer3", "value": 3},
                        {"label": "Layer4", "value": 4}],
                    multi=False,
                    value=1,
                    style={'width': "40%"}
                    ),

        html.Div(id='output_container', children=[]),
        html.Br(),
    #     dcc.Graph(id='pie_chart', figure={}),
        dcc.Graph(id='my_bee_map', figure={}),
        html.Br(),
    #     dcc.Input(id="input1", type="text", placeholder="")
        
        dash_table.DataTable(
        columns=[
            {'name': 'Type', 'id': 'Type', 'type': 'text'},
            {'name': 'Name', 'id': 'Name', 'type': 'text'},
            {'name': 'Layer', 'id': 'Layer', 'type': 'numeric'},
            {'name': 'Count', 'id': 'Count', 'type': 'numeric'}
    #         {'name': 'Life Expectancy', 'id': 'lifeExp', 'type': 'numeric'},
    #         {'name': 'Mock Dates', 'id': 'Mock Date', 'type': 'datetime'}
        ],
        data=df3.to_dict('records'),
        filter_action='native',

        style_table={
            'height': 400,
        },
        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    )


    ])


    # ------------------------------------------------------------------------------
    # Connect the Plotly graphs with Dash Components
    @app.callback(
        [Output(component_id='output_container', component_property='children'),
    #      Output(component_id='pie_chart', component_property='figure'),
        Output(component_id='my_bee_map', component_property='figure')],
        [Input(component_id='slct_Name', component_property='value'),Input(component_id='slct_Layer', component_property='value')]
    )
    def update_graph(x,y):

        container = "The year chosen by user was: {} {}".format(x,y)
        if x=='Foam':
            dff=FT.copy()
            dff_main=FT_main.copy()
        
        if x=='KO':
            dff=KO.copy()
            dff_main=KO_main.copy()
        dff=dff[dff['Layer']==y]
        dff_main=dff_main[dff_main['Layer']==y]
    #     fig1 = go.Figure(data=[go.Pie(labels=dff_main['Name'], values=dff_main['Count'],hole=0.5)])
        layout = go.Layout(
            title="My Dash Graph",
            height=700,
    #         paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,0,0,0)'
            )
        fig=go.Figure(
            data=[go.Bar(y=dff['Count'],x=dff['Name'])],
            layout=layout
        )

        
        return container, fig



    # app = dash.Dash(__name__) 

    port = 8050 

    def open_browser():
        webbrowser.open_new("http://localhost:{}".format(port))

    Timer(1, open_browser).start()
    app.run_server(port=port)

def visual(table_value):
    table=table_value[0]
    path=table_value[1]
    f_name=table_value[2]
    # file=file_name.split('/')[-1]
    # f_name, f_ext = os.path.splitext(file)

    # reader = csv.reader(open(file_name, "r"), delimiter="\t")
    # df=pd.DataFrame(reader)
    # df.columns=['Id','Count','Foam','KO']
    # table=preprocess_data(df)
    print(table)
    FT=table[table['Type']=='Foam'].drop(['Type'],axis=1)
    KO=table[table['Type']=='KO'].drop(['Type'],axis=1)
    FT_main=FT.copy()
    KO_main=KO.copy()
    FT1=FT[FT['Layer']==1].sort_values(by=['Count'],ascending=False).head(10)
    FT2=FT[FT['Layer']==2].sort_values(by=['Count'],ascending=False).head(10)
    FT3=FT[FT['Layer']==3].sort_values(by=['Count'],ascending=False).head(10)
    FT4=FT[FT['Layer']==4].sort_values(by=['Count'],ascending=False).head(10)

    KO1=KO[KO['Layer']==1].sort_values(by=['Count'],ascending=False).head(10)
    KO2=KO[KO['Layer']==2].sort_values(by=['Count'],ascending=False).head(10)
    KO3=KO[KO['Layer']==3].sort_values(by=['Count'],ascending=False).head(10)
    KO4=KO[KO['Layer']==4].sort_values(by=['Count'],ascending=False).head(10)
    FT=pd.concat([FT1,FT2,FT3,FT4])
    KO=pd.concat([KO1,KO2,KO3,KO4])
    f_path=os.path.join(path + os.sep,f_name+'_output.xlsx')
    csv_path=os.path.join(path + os.sep, f_name+'_output')
    table.to_excel (f_path, index = False, header=True)
    table.to_csv (csv_path, index = False, header=True)
    output_visual(path,f_name,FT,KO,FT_main,KO_main,table)


def get_args():
    version="1.0"
    parser = argparse.ArgumentParser(description='Cerberus is used for versatile functional ontology assignments for metagenomes via HMM searching with environmental focus of shotgun meta-omics data')
    parser.add_argument('-i', type=str, required=True, help='path to file or directory \n <accepted formats {.faa,.fna,.ffn,.rollup} , for visualisation : {.rollup }>')
    parser.add_argument('--version','-v', action='version',
                        version='Cerberus: \n version: {} December 24th 2020'.format(version),
                        help='show the version number and exit')
    
    args = parser.parse_args()

    return parser, args

def get_file_list(args):
    in_file_path = args.i
    if os.path.isfile(in_file_path):
        if isfile(join(os.getcwd(), in_file_path)):
            path, file = os.path.split(join(os.getcwd(), in_file_path))
        else:
            path, file = os.path.split(in_file_path)
        file_list = [file]
    if os.path.isdir(in_file_path):
        if os.path.isdir(join(os.getcwd(), in_file_path)):
            path = join(os.getcwd(), in_file_path)
            file_list = [f for f in os.listdir(path) if isfile(join(path, f))]
        else:
            path = in_file_path
            file_list = [f for f in os.listdir(in_file_path) if isfile(join(in_file_path, f))]
    return path, file_list

# def fq_processing(fq_path, path, f_name):
#     fna_name = path + f_name + ".fna"
#     fna_path = open(fna_name, "w")
#     reader = csv.reader(open(fq_path, "r"), delimiter="\t")
#     for line in reader:
#         if line[0][0] != "@": continue
#         label = line[0]
#         try:
#             seq = next(reader)[0]
#         except IndexError:
#             continue
#         fna_path.write(label + "\n")
#         fna_path.write(seq + "\n")
#     return fna_path

def fastq_processing(fq_path, path, f_name,file):
    trim_path=path+'/'+f_name+"_trim.fastq"
    cmd1="fastp -i "+fq_path+" -o " + trim_path
    cmd2="fastqc "+trim_path
    trim_fna=path+'/'+f_name+"_trim.fna"
    cmd3="sed -n '1~4s/^@/>/p;2~4p' "+trim_path+"  > "+trim_fna
    subprocess.call(cmd1,shell=True)
    subprocess.call(cmd2,shell=True)
    subprocess.call(cmd3,shell=True)
    return trim_fna

def fna_processing(fna_path, path, f_name,file):
    name="/prokka_results_"+f_name
    prokka_outdir = path + name+"/"
    prokka_cmd = "prokka %s --outdir %s --prefix %s --centre clean --compliant --metagenome" %(fna_path, prokka_outdir, f_name)
    subprocess.call(prokka_cmd, shell=True)
    faa_path = prokka_outdir + f_name + ".faa"
    return faa_path,path+name

def roll_up(KO_ID_dict, rollup_file):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    FOAM_file = os.path.join(script_dir, "osf_Files/FOAM-onto_rel1.tsv")
    FOAM_dict = {}
    reader = csv.reader(open(FOAM_file, "r"), delimiter="\t")
    header = next(reader)
    for line in reader:
        KO_ID = line[4]
        FOAM_info = line[0:4]
        FOAM_dict[KO_ID] = FOAM_info

    KEGG_file = os.path.join(script_dir, "osf_Files/KO_classification.txt")
    KEGG_dict = {}
    reader = csv.reader(open(KEGG_file, "r"), delimiter="\t")
    for line in reader:
        if line[0] != "":
            tier_1 = line[0]
            continue
        if line[1] != "":
            tier_2 = line[1]
            continue
        if line[2] != "":
            pathway = line[3]
            continue
        KO_ID = line[3]
        KEGG_info = [tier_1, tier_2, pathway] + line[4:]
        KEGG_dict[KO_ID] = KEGG_info

    KO_ID_list = [key for key in KO_ID_dict]
    KO_ID_list.sort()

    outfile = open(rollup_file, "w")
    for KO_ID in KO_ID_list:
        try:
            FOAM_info = FOAM_dict[KO_ID]
        except KeyError:
            FOAM_info = ["NA"]
        try:
            KEGG_info = KEGG_dict[KO_ID]
        except KeyError:
            KEGG_info = ["NA"]
        outline = "\t".join([str(s) for s in [KO_ID, KO_ID_dict[KO_ID], FOAM_info, KEGG_info]])
        outfile.write(outline + "\n")
    return rollup_file

def faa_processing(faa_path,path,f_name):
    output_path=path+os.sep+f_name+"_output"
    os.makedirs(output_path)
    output_path=os.path.join(output_path + os.sep, f_name)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    hmm_file = os.path.join(script_dir, "osf_Files/FOAM-hmm_rel1a.hmm.gz")
    hmm_cmd = "hmmsearch --domtblout %s.FOAM.out %s %s" %(output_path, hmm_file, faa_path)
    subprocess.call(hmm_cmd, shell=True)

    BH_dict = {}
    BS_dict = {}
    minscore = 25
    reader = open(output_path + ".FOAM.out", "r").readlines()
    for line in reader:
        if line[0] == "#": continue
        line = line.split()
        score = float(line[13])
        if score < minscore: continue
        query = line[0]
        try:
            best_score = BS_dict[query]
        except KeyError:
            BS_dict[query] = score
            BH_dict[query] = line
            continue
        if score > best_score:
            BS_dict[query] = score
            BH_dict[query] = line

    KO_ID_dict = {}
    for BH in BH_dict:
        line = BH_dict[BH]
        KO_IDs = [KO_ID.split(":")[1].split("_")[0] for KO_ID in line[3].split(",") if "KO:" in KO_ID]
        for KO_ID in KO_IDs:
            try:
                KO_ID_dict[KO_ID] += 1
            except KeyError:
                KO_ID_dict[KO_ID] = 1
    
    rollup_file = "%s.FOAM.out.sort.BH.KO.rollup" %(output_path)
    return roll_up(KO_ID_dict, rollup_file)
def PCA1():
#     m='/home/taouk/Desktop/robo/data/prokka_results_N139.ffn/N139_output/N139.FOAM.out.sort.BH.KO_output'
#     z='/home/taouk/Desktop/robo/data/N139_output/N139.FOAM.out.sort.BH.KO_output'
#     x='/home/taouk/Desktop/robo/data/input_dir/prokka_results_Agro_10k_R1.fastq/Agro_10k_R1_output/Agro_10k_R1.FOAM.out.sort.BH.KO_output'
#     parent_dir = s
#     y='/home/taouk/Desktop/robo/data/input_dir/prokka_results_Agro_10k_R2.fastq/Agro_10k_R2_output/Agro_10k_R2.FOAM.out.sort.BH.KO_output'
# #     subject_dirs=s
#     subject_dirs = [os.path.join(parent_dir, dir) for dir in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, dir))]
#     csv_files=[x,y,z,m]
    filelist = []
#     for dir in subject_dirs:
#         csv_files = [os.path.join(dir, csv) for csv in os.listdir(dir) if os.path.isfile(os.path.join(dir, csv)) and csv.endswith('_OUTPUT.XLSX.csv')]
    for file in table_list:
        a=file[0]
        y=file[2]
        # base=os.path.basename(file)
        # y=os.path.splitext(base)[0]
        # y = y.replace('_nucleotide_summary','').replace('_protein_summary','')
        a = a[['Name','Count']]
        a = a.rename(columns={'Count':y })
        filelist.append(a)
            
    print(filelist)
    df_merged2 = reduce(lambda  left,right: pd.merge(left,right,on=['Name'],
                                                how='outer'), filelist)
    result=df_merged2.replace(np.nan, 0)
    pivoted=result.T
    res=pivoted.rename(columns=pivoted.iloc[0])
    res1=res.drop(res.index[0])
    pca = PCA(n_components=3,svd_solver='randomized')
    X_train= pca.fit_transform(res1)
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
                            zerolinecolor="black",),),
                    
                    )
    # fig.show()
    plot(fig, filename=path+'/'+'PCA_plot'+".html", auto_open=True)
def main(path, file):
    f_name, f_ext = os.path.splitext(file)
    f_name=f_name.split('.')[0]
    fq_list = [".fq",".fastq"]
    fna_list = [".fa",".fna" ,".fasta",".ffn"]
    output_path=path+os.sep+f_name+"_output"
    if f_ext in fq_list:
        fq_path = os.path.join(path + os.sep, file)
        fna_path = fastq_processing(fq_path, path, f_name,file)
        faa_path,path = fna_processing(fna_path, path, f_name,file)
        output_path=path+os.sep+f_name+"_output"
        rollup_file=faa_processing(faa_path,path,f_name)
        preprocess_data(output_path,rollup_file)
    elif f_ext in fna_list:
        fna_path = os.path.join(path + os.sep, file)
        faa_path,path = fna_processing(fna_path, path, f_name,file)
        output_path=path+os.sep+f_name+"_output"
        rollup_file=faa_processing(faa_path,path,f_name)
        preprocess_data(output_path,rollup_file)
    elif f_ext in  [".faa"]:
        faa_path = os.path.join(path + os.sep, file)
        rollup_file=faa_processing(faa_path,path,f_name)
        preprocess_data(output_path,rollup_file)
    elif f_ext == ".rollup":
        # os.makedirs(path+os.sep+file)
        # print(path)
        preprocess_data(path,os.path.join(path + os.sep, file))
        # visual(file)
    elif f_ext == '.html':
        pass
    else:
        print("File extension \" %s \" not recognized. Please name file(s) appropriately." %(f_ext))
def time_graph():
    time_list.sort()
    x = [i[0] for i in time_list]
    y = [i[1] for i in time_list]
    fig = go.Figure(data=go.Scatter(x=x, y=y))
    fig.update_layout(
        title="Memory-Time Graph",
        xaxis_title="Size of the Genome (in MB's)",
        yaxis_title="Time taken (in min)",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )
    plot(fig, filename=path+'/'+'time_graph'+".html", auto_open=True)
if __name__ == "__main__":
    parser, args = get_args()
    path, file_list = get_file_list(args)
    # print(parser,args)
    # return
    # print(file_list)
    table_list=[]
    time_list=[]
    for f in file_list:
        start_time = time.time()
        size=os.path.getsize(path+os.sep+f)
        size=round(size / (1024 * 1024), 2)
        main(path, f)
        time_taken=time.time() - start_time
        time_taken=round(time_taken / (60), 2)
        time_list.append((time_taken,size))
    # print("--- %s seconds ---" % (time.time() - start_time))
    len_tab=len(table_list)
    time_graph()
    if len_tab==1:
        visual(table_list[0])
    elif len_tab<=3:
        # new_visual()
        # PCA1()
        new_visual()
    elif len_tab<=6:
        PCA1()
        new_visual()
        
    elif len_tab>6:
        PCA1()
    
