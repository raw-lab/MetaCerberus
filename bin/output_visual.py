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


def output_visual(path,f_name,FT,KO,FT_main,KO_main,table):
    app = dash.Dash(__name__)
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


