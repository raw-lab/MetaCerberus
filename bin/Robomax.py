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
app = dash.Dash(__name__)
def preprocess_data(df):
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
    return table
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
        html.H1("Robomax Outputs", style={'text-align': 'center'}),
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
        print(x,'sdfsdds')
        print(y)

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

def visual(path,file_name):
    file=file_name.split('/')[-1]
    f_name, f_ext = os.path.splitext(file)

    reader = csv.reader(open(file_name, "r"), delimiter="\t")
    df=pd.DataFrame(reader)
    df.columns=['Id','Count','Foam','KO']
    table=preprocess_data(df)
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
    parser = argparse.ArgumentParser(description='RoboMax is used for versatile functional ontology assignments for metagenomes via HMM searching with environmental focus of shotgun meta-omics data')
    parser.add_argument('-i', type=str, required=True, help='path to file or directory \n <accepted formats {.faa,.fna,.ffn,.rollup} , for visualisation : {.rollup }>')
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

def fq_processing(fq_path, path, f_name):
    fna_name = path + f_name + ".fna"
    fna_path = open(fna_name, "w")
    reader = csv.reader(open(fq_path, "r"), delimiter="\t")
    for line in reader:
        if line[0][0] != "@": continue
        label = line[0]
        try:
            seq = next(reader)[0]
        except IndexError:
            continue
        fna_path.write(label + "\n")
        fna_path.write(seq + "\n")
    return fna_path

def fna_processing(fna_path, path, f_name,file):
    name="/prokka_results_"+file
    prokka_outdir = path + name+"/"
    prokka_cmd = "prokka %s --outdir %s --prefix %s" %(fna_path, prokka_outdir, f_name)
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

def main(path, file):
    f_name, f_ext = os.path.splitext(file)
    f_name=f_name.split('.')[0]
    fq_list = [".fq", ".fastq"]
    fna_list = [".fa",".fna", ".fasta", ".ffn"]
    output_path=path+os.sep+f_name+"_output"
    if f_ext in fq_list:
        fq_path = os.path.join(path + os.sep, file)
        fna_path = fq_processing(fq_path, path, f_name)
        faa_path,path = fna_processing(fna_path, path, f_name,file)
        output_path=path+os.sep+f_name+"_output"
        rollup_file=faa_processing(faa_path,path,f_name)
        visual(output_path,rollup_file)
    elif f_ext in fna_list:
        fna_path = os.path.join(path + os.sep, file)
        faa_path,path = fna_processing(fna_path, path, f_name,file)
        output_path=path+os.sep+f_name+"_output"
        rollup_file=faa_processing(faa_path,path,f_name)
        visual(output_path,rollup_file)
    elif f_ext == ".faa":
        faa_path = os.path.join(path + os.sep, file)
        rollup_file=faa_processing(faa_path,path,f_name)
        visual(output_path,rollup_file)
    elif f_ext == ".rollup":
        # os.makedirs(path+os.sep+file)
        # print(path)
        visual(path,os.path.join(path + os.sep, file))
        # visual(file)
    else:
        print("File extension \" %s \" not recognized. Please name file(s) appropriately." %(f_ext))

if __name__ == "__main__":
    parser, args = get_args()
    path, file_list = get_file_list(args)
    print(parser,args)
    for f in file_list:
        main(path, f)
