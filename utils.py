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

import math

import dash_bootstrap_components as dbc


def upload_data(contents, filename):
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

    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            data=df_vinfo.to_dict('records'),
            columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in df_vinfo.columns],
            style_cell={'textAlign': 'left'},
            style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
            #filter_action="native",
            #sort_action="native",
            #sort_mode="multi",
            #row_selectable="multi",
            #row_deletable=True,
            #selected_columns=[],
            #selected_rows=[]
        )
    ])


# recap function
def vinfo_summary(vinfo_db, vpartition_db, vhost_db,
                  metrics=""):
    # get number of total VMs (rows)
    vm = vinfo_db.shape[0]

    # get number of VMs with "Guest state" values
    # todo store name and specs of VMs not running for analysis
    temp = vinfo_db["Guest state"].unique()
    if "running" in temp and "notRunning" in temp:
        vm_running = vinfo_db["Guest state"].value_counts()["running"]
        vm_notrunning = vinfo_db["Guest state"].value_counts()["notRunning"]
    elif "notRunning" in temp:
        vm_notrunning = vinfo_db["Guest state"].value_counts()["notRunning"]
        vm_running = None
    else:
        vm_running = vinfo_db["Guest state"].value_counts()["running"]
        vm_notrunning = None

    # get number of VMs with "Powerstate" values
    # todo store name and specs of VMs not running for analysis
    temp = vinfo_db["Powerstate"].unique()
    if "poweredOn" in temp and "poweredOff" in temp:
        vm_on = vinfo_db["Powerstate"].value_counts()["poweredOn"]
        vm_off = vinfo_db["Powerstate"].value_counts()["poweredOff"]
    elif "poweredOff" in temp:
        vm_off = vinfo_db["Powerstate"].value_counts()["poweredOff"]
        vm_on = None
    else:
        vm_off = None
        vm_on = vinfo_db["Powerstate"].value_counts()["poweredOn"]

    # get CPUs count
    # todo add option of choosing to take out VMs of scope (ie poweredOff)
    cpu = vinfo_db.CPUs.sum()

    # get memory count rounded up
    ram = math.ceil(vinfo_db.Memory.sum() / 1024)

    # get consumed storage rounded up (in GiB or TiB)
    # todo: add option to have consumed for running and in use for notrunning VMs
    consumed_sto = math.ceil(vpartition_db["Consumed MB"].sum() / 1024)

    # get consumed storage rounded up (in GiB or TiB)
    # todo: add option to have consumed for running and in use for notrunning VMs
    capacity_sto = math.ceil(vpartition_db["Capacity MB"].sum() / 1024)

    # get in use storage rounded up (in GiB or TiB)
    # todo: add option to have consumed for running and in use for notrunning VMs
    in_use_sto = math.ceil(vinfo_db["In Use MB"].sum() / 1024)

    # change to TiB if asked
    # if metrics["storage_metric"] == "TiB":
    #    consumed_sto = math.ceil(consumed_sto / 1024)

    # count hosts
    host_count = vhost_db.shape[0]

    # count cores of hosts
    host_cores = vhost_db["# Cores"].sum()

    # get host models & count of each
    host_models = vhost_db.Model.value_counts()

    # get host ESX versions
    host_esx = vhost_db["ESX Version"].value_counts()

    # get cluster names & size
    host_clusters = vhost_db.Cluster.value_counts()

    # get number of clusters
    count_clusters = len(host_clusters["Host Cluster(s)"].keys())

    # get OS (config file) counts
    vm_os = vinfo_db["OS according to the configuration file"].value_counts()

    # aggregate results for test
    output_list = {"VM(s)": vm,
                   "CPU(s)": cpu,
                   "RAM": ram,
                   "Consumed Storage": consumed_sto,
                   "Capacity Storage": capacity_sto,
                   "In Use Storage": in_use_sto,
                   "Host Count": host_count,
                   "Host Cores": host_cores,
                   "Host Models": host_models,
                   "Host ESX Versions": host_esx,
                   "Host Cluster(s)": host_clusters,
                   "Host Cluster Count": count_clusters,
                   "VM OS count(s)": vm_os,
                   "VM notRunning": vm_notrunning,
                   "VM poweredOff": vm_off}

    return output_list


def get_sizer_info(df_vinfo, df_vpartition, df_vhost):
    """content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        df_vinfo = pd.read_excel(io.BytesIO(decoded), "vInfo")
        df_vpartition = pd.read_excel(io.BytesIO(decoded), "vPartition")
        df_vhost = pd.read_excel(io.BytesIO(decoded), "vHost")
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])"""
    # get values of rvtools
    value_dict = vinfo_summary(df_vinfo, df_vpartition, df_vhost)

    # arrange for sizer metrics
    units_to_display = ['VM(s)', 'CPU(s)', 'RAM (GiB)', 'Consumed Storage (Gib)']
    df_typing_formatting = pd.DataFrame(OrderedDict([
        ('units', units_to_display),
        ('values', [value_dict[i] for i in ["VM(s)", "CPU(s)", "RAM", "Consumed Storage"]])
    ]))

    # arrange host metrics
    units_to_display2 = ['Host Count', 'Total Cores', 'Cluster Count', 'VM(s) notRunning', 'VM(s) poweredOff']
    count_clusters = len(value_dict["Host Cluster(s)"].keys())
    df_host_formating = pd.DataFrame(OrderedDict([
        ('units', units_to_display),
        ('values', [value_dict[i] for i in ['Host Count', 'Host Cores', 'Host Cluster Count', 'VM notRunning',
                                            'VM poweredOff']])
    ]))

    return dbc.Row(
        [
            dbc.Col(
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
                ]), md=4
            ),
            dbc.Col(
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
                                    go.Bar(
                                        x=[
                                            "In Use",
                                        ],
                                        y=[
                                            str(value_dict["In Use Storage"])
                                        ],
                                        marker={
                                            "color": "#dddddd",
                                            "line": {
                                                "color": "rgb(255, 255, 255)",
                                                "width": 2,
                                            },
                                        },
                                        name="In Use",
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
                ), md=4
            ),
            dbc.Col(
                html.Div([
                    html.H5(
                        ["Host Information"], className="subtitle padded"
                    ),

                    dash_table.DataTable(
                        id='host_info',
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
                ]), md=4
            )
        ]
    )
