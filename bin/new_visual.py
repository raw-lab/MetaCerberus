import os
from os.path import isfile, join
import sys
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
from plotly.offline import plot
import webbrowser
from threading import Timer
import matplotlib.pyplot as plt





def new_visual(path,table_list):

    app = dash.Dash(__name__)
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
