# import packages
import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign
import pandas as pd
from collections import OrderedDict

import plotly.graph_objs as go

import pandas as pd
import math

# import functions
from main import vinfo_summary

app = dash.Dash()

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'overflowY': 'auto',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload')
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        df_vinfo = pd.read_excel(io.BytesIO(decoded), "vInfo")
        df_vpartition = pd.read_excel(io.BytesIO(decoded), "vPartition")
        df_vhost = pd.read_excel(io.BytesIO(decoded), "vHost")
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    # get values of rvtools
    value_dict = vinfo_summary(df_vinfo, df_vpartition, df_vhost)

    # arrange for sizer metrics
    units_to_display = ['VM(s)', 'CPU(s)', 'RAM (GiB)', 'Consumed Storage (Gib)']
    df_typing_formatting = pd.DataFrame(OrderedDict([
        ('units', units_to_display),
        ('values', [value_dict[i] for i in ["VM(s)", "CPU(s)", "RAM", "Consumed Storage"]])
    ]))

    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            data=df_vinfo.to_dict('records'),
            columns=[{'name': i, 'id': i, "deletable": True, "selectable": True} for i in df_vinfo.columns],
            style_cell={'textAlign': 'left'},
            style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[]
        ),

        html.Hr(),  # horizontal line

        html.Div([
            html.H5(
                ["Sizing Metrics"], className="subtitle padded"
            ),

            dash_table.DataTable(
                id='typing_formatting_1',
                data=df_typing_formatting.to_dict('records'),
                columns=[{
                    'id': 'units',
                    'name': 'Unit',
                    'type': 'text'
                }, {
                    'id': 'values',
                    'name': 'Value',
                    'type': 'numeric'
                }],
                style_cell={'textAlign': 'left', 'padding': '5px'},
                style_table={'height': '200px', "width": '250px', 'overflowY': 'auto', 'overflowX': 'auto'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'center'
                    } for c in ['Value']
                ],
            )
        ]),
        html.Div(
            [
                html.H6(
                    "Storage Consumed vs. Capacity",
                    className="subtitle padded",
                ),
                dcc.Graph(
                    id="graph-1",
                    figure={
                        "data": [
                            go.Bar(
                                x=[
                                    "Storage (MiB)",
                                ],
                                y=[
                                    str(value_dict["Capacity Storage"])
                                ],
                                marker={
                                    "color": "#97151c",
                                    "line": {
                                        "color": "rgb(255, 255, 255)",
                                        "width": 2,
                                    },
                                },
                                name="Capacity",
                            ),
                            go.Bar(
                                x=[
                                    "Consumed",
                                ],
                                y=[
                                    str(value_dict["Consumed Storage"])
                                ],
                                marker={
                                    "color": "#dddddd",
                                    "line": {
                                        "color": "rgb(255, 255, 255)",
                                        "width": 2,
                                    },
                                },
                                name="Consumed",
                            ),
                        ],
                        "layout": go.Layout(
                            autosize=False,
                            bargap=0.35,
                            font={"family": "Raleway", "size": 10},
                            height=200,
                            hovermode="closest",
                            legend={
                                "x": -0.0228945952895,
                                "y": -0.189563896463,
                                "orientation": "h",
                                "yanchor": "top",
                            },
                            margin={
                                "r": 0,
                                "t": 20,
                                "b": 10,
                                "l": 10,
                            },
                            showlegend=True,
                            title="",
                            width=330,
                            xaxis={
                                "autorange": True,
                                "range": [-0.5, 4.5],
                                "showline": True,
                                "title": "",
                                "type": "category",
                            },
                            yaxis={
                                "autorange": True,
                                "range": [0, math.ceil(value_dict["Capacity Storage"] / 100) * 100],
                                "showgrid": True,
                                "showline": True,
                                "title": "",
                                "type": "linear",
                                "zeroline": False,
                            },
                        ),
                    },
                    config={"displayModeBar": False},
                ),
            ],
            className="two columns",
        ),
    ],
        className="row",
        style={"margin-bottom": "35px"},
    )


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            update_output(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        return children


if __name__ == '__main__':
    app.run_server(debug=False)
