# import packages
import base64
import datetime
import io
import requests
import json

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
import plotly.express as px

import math

import dash_bootstrap_components as dbc

from v2_dev.api_test import input_post_metrics, response_to_dict

# POST template
template2_json = {
    "globalSpecs": {},
    "workloads": [
        {
            "profileName": "Workload Profile - 1",
            "vmProfile": {
                "vCpusPerCore": 4,
                "vCpusPerVM": 2,
                "vRAMPerVM": {
                    "value": 200
                },
                "vmdkSize": {
                    "value": 200
                },
                "vmsNum": 1000
            },
            "workloadType": "GPW_GVM"
        }
    ]
}


def read_rvtools(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    df_vinfo = pd.read_excel(io.BytesIO(decoded), "vInfo")
    df_vpartition = pd.read_excel(io.BytesIO(decoded), "vPartition")
    df_vhost = pd.read_excel(io.BytesIO(decoded), "vHost")

    return df_vinfo, df_vpartition, df_vhost


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
    # can put some filters
    return html.Div([
        html.H5(filename),

        dcc.Tabs([
            dcc.Tab(label='vInfo', children=[
                dash_table.DataTable(
                    data=df_vinfo.to_dict('records'),
                    columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in df_vinfo.columns],
                    style_cell={'textAlign': 'left'},
                    style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                    # filter_action="native",
                    # sort_action="native",
                    # sort_mode="multi",
                    # row_selectable="multi",
                    # row_deletable=True,
                    # selected_columns=[],
                    # selected_rows=[]
                )
            ]),
            dcc.Tab(label='vPartition', children=[
                dash_table.DataTable(
                    data=df_vpartition.to_dict('records'),
                    columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                             df_vpartition.columns],
                    style_cell={'textAlign': 'left'},
                    style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                    # filter_action="native",
                    # sort_action="native",
                    # sort_mode="multi",
                    # row_selectable="multi",
                    # row_deletable=True,
                    # selected_columns=[],
                    # selected_rows=[]
                )
            ]),
            dcc.Tab(label='vHost', children=[
                dash_table.DataTable(
                    data=df_vhost.to_dict('records'),
                    columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                             df_vhost.columns],
                    style_cell={'textAlign': 'left'},
                    style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                    # filter_action="native",
                    # sort_action="native",
                    # sort_mode="multi",
                    # row_selectable="multi",
                    # row_deletable=True,
                    # selected_columns=[],
                    # selected_rows=[]
                )
            ])
        ]),

    ])


# recap function
def vinfo_summary(vinfo_db, vpartition_db, vhost_db,
                  no_run, pow_off, sto_unit,
                  filter1, filter12, filter2, filter22, no_vm, top_ram, top_sto):
    temp_sto = 0

    # stock removed vm for visualisation
    # todo : add all the filtered VMs to this and remove all at the end & copy to diff df for dashtable
    # todo : remove redundant list hereafter
    if no_vm is not None:
        vm_to_remove = no_vm
    else:
        vm_to_remove = list()

    # get number of VMs with "Guest state" values
    # todo store name and specs of VMs not running for analysis
    temp = vinfo_db["Guest state"].unique()
    if "running" in temp and "notRunning" in temp:
        vm_running = vinfo_db["Guest state"].value_counts()["running"]
        vm_notrunning = vinfo_db["Guest state"].value_counts()["notRunning"]
    elif "notRunning" in temp:
        vm_notrunning = vinfo_db["Guest state"].value_counts()["notRunning"]
        vm_running = 0
    else:
        vm_running = vinfo_db["Guest state"].value_counts()["running"]
        vm_notrunning = 0

    # get number of VMs with "Powerstate" values
    # todo store name and specs of VMs not running for analysis
    temp = vinfo_db["Powerstate"].unique()
    if "poweredOn" in temp and "poweredOff" in temp:
        vm_on = vinfo_db["Powerstate"].value_counts()["poweredOn"]
        vm_off = vinfo_db["Powerstate"].value_counts()["poweredOff"]
    elif "poweredOff" in temp:
        vm_off = vinfo_db["Powerstate"].value_counts()["poweredOff"]
        vm_on = 0
    else:
        vm_off = 0
        vm_on = vinfo_db["Powerstate"].value_counts()["poweredOn"]

    # first remove out of scope
    if top_ram is not None and top_sto is not None:
        vm_to_remove += vinfo_db.sort_values('Memory', ascending=False)[:top_ram]['VM'].to_list()
        temp_sto_df = vpartition_db[['VM', 'Consumed MB']].groupby(['VM'], as_index=False).sum()
        vm_to_remove += temp_sto_df.sort_values('Consumed MB', ascending=False)[:top_sto]['VM'].to_list()

        # vinfo_db = vinfo_db[~vinfo_db['VM'].isin(drop_vms_ram)]
        # vpartition_db = vpartition_db[~vpartition_db['VM'].isin(drop_vms_ram)]

        # vinfo_db = vinfo_db[~vinfo_db['VM'].isin(drop_vms_sto)]
        # vpartition_db = vpartition_db[~vpartition_db['VM'].isin(drop_vms_sto)]

    elif top_ram is not None:

        vm_to_remove += vinfo_db.sort_values('Memory', ascending=False)[:top_ram]['VM'].tolist()

        # vinfo_db = vinfo_db[~vinfo_db['VM'].isin(drop_vms_ram)]
        # vpartition_db = vpartition_db[~vpartition_db['VM'].isin(drop_vms_ram)]

    elif top_sto is not None:
        temp_sto_df = vpartition_db[['VM', 'Consumed MB']].groupby(['VM'], as_index=False).sum()
        vm_to_remove += temp_sto_df.sort_values('Consumed MB', ascending=False)[:top_sto]['VM'].to_list()

        # vinfo_db = vinfo_db[~vinfo_db['VM'].isin(drop_vms_sto)]
        # vpartition_db = vpartition_db[~vpartition_db['VM'].isin(drop_vms_sto)]

    # if no_vm is not None:
    #    vinfo_db = vinfo_db[~vinfo_db['VM'].isin(no_vm)]
    #    vpartition_db = vpartition_db[~vpartition_db['VM'].isin(no_vm)]

    removed_vinfo = vinfo_db[vinfo_db['VM'].isin(vm_to_remove)]
    removed_vpartition = vpartition_db[vpartition_db['VM'].isin(vm_to_remove)]

    vinfo_db = vinfo_db[~vinfo_db['VM'].isin(vm_to_remove)]
    vpartition_db = vpartition_db[~vpartition_db['VM'].isin(vm_to_remove)]

    if no_run == "notrunning":
        vinfo_db = vinfo_db[vinfo_db["Guest state"] != "notRunning"]
    else:
        # include In use sto as sto for these
        temp_sto += vinfo_db[vinfo_db["Guest state"] == "notRunning"]["In Use MB"].sum()

    if pow_off == "poweredoff":
        vinfo_db = vinfo_db[vinfo_db["Powerstate"] != "poweredOff"]
    else:
        temp_sto += vinfo_db[vinfo_db["Powerstate"] == "poweredoff"]["In Use MB"].sum()

    # get number of total VMs (rows)
    vm = vinfo_db.shape[0]

    # get CPUs count
    # todo add option of choosing to take out VMs of scope (ie poweredOff)
    cpu = vinfo_db.CPUs.sum()

    # get memory count rounded up
    ram = math.ceil(vinfo_db.Memory.sum() / 1024)

    # get consumed storage rounded up (in GiB or TiB)
    # todo: add option to have consumed for running and in use for notrunning VMs
    consumed_sto = math.ceil((vpartition_db["Consumed MB"].sum() + temp_sto) / 1024)
    consumed_stog = consumed_sto

    # get consumed storage rounded up (in GiB or TiB)
    # todo: add option to have consumed for running and in use for notrunning VMs
    capacity_sto = math.ceil((vpartition_db["Capacity MB"].sum() + temp_sto) / 1024)

    # get in use storage rounded up (in GiB or TiB)
    # todo: add option to have consumed for running and in use for notrunning VMs
    in_use_sto = math.ceil(vinfo_db["In Use MB"].sum() / 1024)

    # change to TiB if asked
    if sto_unit == "tib":
        consumed_stog = consumed_sto
        consumed_sto = math.ceil(consumed_sto / 1024)

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
    count_clusters = len(host_clusters.keys())

    # get OS (config file) counts
    vm_os = vinfo_db["OS according to the configuration file"].value_counts()

    # find vm filter
    if filter2 is not None:
        if filter22 == "percent":
            val = 10618.88 * filter2 * 0.01
        else:
            val = filter2

        temp_vms_sto = list()
        for vms in vinfo_db.VM:
            if math.floor(vpartition_db[vpartition_db["VM"] == vms]["Consumed MB"].sum() / 1024) > val:
                temp_vms_sto.append(vms)

        temp_df_sto_vinfo = vinfo_db[vinfo_db['VM'].isin(temp_vms_sto)]

    if filter1 is not None:
        if filter12 == "percent":
            val = 512 * filter1 * 0.01 * 1024
        else:
            val = filter1 * 1024

        temp_df_ram_vinfo = vinfo_db[vinfo_db['Memory'] > val]

    # aggregate results for test
    output_list = {"VM(s)": vm,
                   "CPU(s)": cpu,
                   "RAM": ram,
                   "Consumed Storage": consumed_sto,
                   "Consumed Storage Graph": consumed_stog,
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

    if filter1 is not None and filter2 is not None:
        return output_list, temp_df_sto_vinfo, temp_df_ram_vinfo, removed_vinfo, removed_vpartition
    elif filter1 is not None:
        return output_list, temp_df_ram_vinfo, removed_vinfo, removed_vpartition
    elif filter2 is not None:
        return output_list, temp_df_sto_vinfo, removed_vinfo, removed_vpartition
    else:
        return output_list, removed_vinfo, removed_vpartition


def get_sizer_info(df_vinfo, df_vpartition, df_vhost, exclude_vm, filter1, filter12, filter2, filter22, sto_unit,
                   out_vm, top_ram, top_sto):
    row_3 = None

    if len(exclude_vm) > 1:
        no_run, pow_off = exclude_vm
    elif len(exclude_vm) == 1:
        no_run = exclude_vm[0]
        pow_off = exclude_vm[0]
    else:
        no_run = None
        pow_off = None

    # get values of rvtools
    if filter1 is not None and filter2 is not None:
        value_dict, df_sto, df_ram, df_rem_info, df_rem_sto = vinfo_summary(df_vinfo, df_vpartition, df_vhost, no_run,
                                                                            pow_off, sto_unit, filter1, filter12,
                                                                            filter2, filter22, out_vm, top_ram, top_sto)
        row_3 = html.Div([
            html.H5("Filtered VM(s)"),

            dcc.Tabs([
                dcc.Tab(label='Storage Filter', children=[
                    dash_table.DataTable(
                        data=df_sto.to_dict('records'),
                        columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                 df_sto.columns],
                        style_cell={'textAlign': 'left'},
                        style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                        # filter_action="native",
                        # sort_action="native",
                        # sort_mode="multi",
                        # row_selectable="multi",
                        # row_deletable=True,
                        # selected_columns=[],
                        # selected_rows=[]
                    )
                ]),
                dcc.Tab(label='RAM Filter', children=[
                    dash_table.DataTable(
                        data=df_ram.to_dict('records'),
                        columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                 df_ram.columns],
                        style_cell={'textAlign': 'left'},
                        style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                        # filter_action="native",
                        # sort_action="native",
                        # sort_mode="multi",
                        # row_selectable="multi",
                        # row_deletable=True,
                        # selected_columns=[],
                        # selected_rows=[]
                    )
                ])
            ])
        ])
    elif filter2 is not None:
        value_dict, df_ram, df_rem_info, df_rem_sto = vinfo_summary(df_vinfo, df_vpartition, df_vhost, no_run, pow_off,
                                                                    sto_unit, filter1, filter12, filter2, filter22,
                                                                    out_vm, top_ram, top_sto)
        row_3 = html.Div([
            html.H5("Filtered RAM VM(s)"),

            dash_table.DataTable(
                data=df_ram.to_dict('records'),
                columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                         df_ram.columns],
                style_cell={'textAlign': 'left'},
                style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                # filter_action="native",
                # sort_action="native",
                # sort_mode="multi",
                # row_selectable="multi",
                # row_deletable=True,
                # selected_columns=[],
                # selected_rows=[]
            )
        ])
    elif filter1 is not None:
        value_dict, df_sto, df_rem_info, df_rem_sto = vinfo_summary(df_vinfo, df_vpartition, df_vhost, no_run, pow_off,
                                                                    sto_unit, filter1, filter12, filter2, filter22,
                                                                    out_vm, top_ram, top_sto)
        row_3 = html.Div([
            html.H5("Filtered Storage VM(s)"),

            dash_table.DataTable(
                data=df_sto.to_dict('records'),
                columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                         df_sto.columns],
                style_cell={'textAlign': 'left'},
                style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                # filter_action="native",
                # sort_action="native",
                # sort_mode="multi",
                # row_selectable="multi",
                # row_deletable=True,
                # selected_columns=[],
                # selected_rows=[]
            )
        ])
    else:
        value_dict, df_rem_info, df_rem_sto = vinfo_summary(df_vinfo, df_vpartition, df_vhost, no_run, pow_off,
                                                            sto_unit, filter1, filter12, filter2, filter22, out_vm,
                                                            top_ram, top_sto)

    # arrange for sizer metrics
    units_to_display = ['VM(s)', 'CPU(s)', 'RAM (GiB)', 'Consumed Storage (Gib)']
    df_typing_formatting = pd.DataFrame(OrderedDict([
        ('units', units_to_display),
        ('values', [value_dict[i] for i in ["VM(s)", "CPU(s)", "RAM", "Consumed Storage"]])
    ]))

    # arrange host metrics
    units_to_display2 = ['Host Count', 'Total Cores', 'Cluster Count', 'VM(s) notRunning', 'VM(s) poweredOff']
    df_host_formatting = pd.DataFrame(OrderedDict([
        ('units', units_to_display2),
        ('values', [value_dict[i] for i in ['Host Count', 'Host Cores', 'Host Cluster Count', 'VM notRunning',
                                            'VM poweredOff']])
    ]))

    # arrange OS metrics
    ms_licenses = ['Microsoft Windows Server 2012 (64 bits)',
                   'Microsoft Windows Server 2016 ou version ultérieure (64 bits)',
                   'Microsoft Windows Server 2008 R2 (64 bits)', 'Microsoft Windows Server 2016 or later (64-bit)',
                   'Microsoft Windows Server 2012 (64-bit)']
    # rv_ms_licenses = [i for i in value_dict['VM OS count(s)'].keys().tolist() and ms_licenses]
    rv_ms_licenses = list(set(value_dict['VM OS count(s)'].keys().tolist()).intersection(ms_licenses))

    df_os_formatting = pd.DataFrame(OrderedDict([
        ('server_version', rv_ms_licenses),
        ('count', [value_dict['VM OS count(s)'][i] for i in rv_ms_licenses])
    ]))

    # create cluster pie chart
    labels = value_dict["Host Cluster(s)"].keys().tolist()
    values = value_dict["Host Cluster(s)"].values.tolist()

    # create OS pie chart
    labels1 = value_dict["VM OS count(s)"].keys().tolist()
    values1 = value_dict["VM OS count(s)"].values.tolist()

    # create ESX pie chart
    labels2 = value_dict["Host ESX Versions"].keys().tolist()
    values2 = value_dict["Host ESX Versions"].values.tolist()

    # get sizer information
    post = input_post_metrics(template2_json, value_dict['VM(s)'], value_dict['CPU(s)'], value_dict['RAM'],
                              value_dict['Consumed Storage Graph'])


    headers = {'content-type': 'application/json'}

    response = requests.post("https://vmc.vmware.com/api/sizer/v4/recommendation?cloudProviderType=VMC_ON_AWS",
                             json=post, headers=headers)

    out_gen = response_to_dict(response)['genericResponse']

    # arrange sizer metrics
    units_to_display3 = ['I3 Host Count', 'Total Cores', 'Total Memory', 'Total Storage', 'FTT & FTM']
    df_sizer = pd.DataFrame(OrderedDict([
        ('units', units_to_display3),
        ('values', [out_gen['sddcInformation']['nodesSize'], out_gen['sddcInformation']['provisionedCores'],
                    out_gen['sddcInformation']['provisionedMemory']['value'],
                    out_gen['sddcInformation']['provisionedStorage']['value'],
                    out_gen['sddcInformation']['fttAndftm']])
    ]))

    # arrange sizer graph
    x_data = [[out_gen['cpuCoresUsage']['consumed'], out_gen['cpuCoresUsage']['free']],
              [out_gen['memoryUsage']['consumed']['value'], out_gen['memoryUsage']['free']['value']],
              [out_gen['diskSpaceUsage']['consumedStorage']['value'],
               out_gen['diskSpaceUsage']['consumedSystemStorage']['value'],
               out_gen['diskSpaceUsage']['freeStorage']['value']]]

    hover_data = ['Consumed', 'Free', 'Consumed', 'Free', 'Consumed by workloads', 'Consumed by system', 'Free']

    if row_3 is not None:
        return [
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Sizing Metrics"], className="subtitle padded"
                            ),

                            dash_table.DataTable(
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
                                style_table={'height': 'auto', "width": 'auto', 'overflowY': 'auto',
                                             'overflowX': 'auto'},
                                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'center'
                                    } for c in ['Value']
                                ],
                            )
                        ])
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H5(
                                    "Storage Comparison",
                                    className="subtitle padded",
                                ),
                                dcc.Graph(
                                    id="graph-1",
                                    figure={
                                        "data": [
                                            go.Bar(
                                                x=[
                                                    "Capacity (MiB)",
                                                ],
                                                y=[
                                                    str(value_dict["Capacity Storage"])
                                                ],
                                                marker={
                                                    "color": "rgb(64, 149, 206)",
                                                    "line": {
                                                        "color": "rgb(255, 255, 255)",
                                                        "width": 2,
                                                    },
                                                },
                                                name="Capacity",
                                            ),
                                            go.Bar(
                                                x=[
                                                    "Consumed (MiB)",
                                                ],
                                                y=[
                                                    str(value_dict["Consumed Storage Graph"])
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
                                                    "In Use (MiB)",
                                                ],
                                                y=[
                                                    str(value_dict["In Use Storage"])
                                                ],
                                                marker={
                                                    "color": "rgb(236, 157, 66)",
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
                        )
                    ),
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Host Information"], className="subtitle padded"
                            ),

                            dcc.Tabs([
                                dcc.Tab(label='Overview', children=[

                                    dash_table.DataTable(
                                        id='host_info',
                                        data=df_host_formatting.to_dict('records'),
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
                                        style_table={'height': 'auto', "width": 'auto', 'overflowY': 'auto',
                                                     'overflowX': 'auto'},
                                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': c},
                                                'textAlign': 'center'
                                            } for c in ['Value']
                                        ],
                                    )
                                ]),
                                dcc.Tab(label='Cluster Pie', children=[
                                    dcc.Graph(figure=go.Figure(data=go.Pie(labels=labels, values=values)))
                                ])
                            ])

                        ])
                    )
                ]
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["OS Pie"], className="subtitle padded"
                            ),
                            dcc.Graph(figure=go.Figure(data=go.Pie(labels=labels1, values=values1),
                                                       layout={}))
                        ])
                    ),
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Host ESX Versions"], className="subtitle padded"
                            ),

                            # VMware license table
                            # tab VMware VM's ??
                            dcc.Graph(figure=go.Figure(data=go.Pie(labels=labels2, values=values2),
                                                       layout={}))

                        ])
                    )
                ]
            ),
            html.Div(
                [
                    html.H5(
                        "MS Licenses",
                        className="subtitle padded",
                    ),
                    # table with MS Os
                    dash_table.DataTable(
                        data=df_os_formatting.to_dict('records'),
                        columns=[{
                            'id': 'server_version',
                            'name': 'Server Version',
                            'type': 'text'
                        }, {
                            'id': 'count',
                            'name': 'Count',
                            'type': 'numeric'
                        }],
                        style_cell={'textAlign': 'left', 'padding': '5px'},
                        style_table={'height': 'auto', "width": 'auto', 'overflowY': 'auto',
                                     'overflowX': 'auto'},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        style_cell_conditional=[
                            {
                                'if': {'column_id': c},
                                'textAlign': 'center'
                            } for c in ['Value']
                        ],
                    )
                ],
                className="two columns",
            ),
            html.Br(),
            row_3,
            html.Br(),
            html.Div([
                html.H5('VM(s) Removed from Scope'),

                dcc.Tabs([
                    dcc.Tab(label='vInfo', children=[
                        dash_table.DataTable(
                            data=df_rem_info.to_dict('records'),
                            columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                     df_rem_info.columns],
                            style_cell={'textAlign': 'left'},
                            style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                            # filter_action="native",
                            # sort_action="native",
                            # sort_mode="multi",
                            # row_selectable="multi",
                            # row_deletable=True,
                            # selected_columns=[],
                            # selected_rows=[]
                        )
                    ]),
                    dcc.Tab(label='vPartition', children=[
                        dash_table.DataTable(
                            data=df_rem_sto.to_dict('records'),
                            columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                     df_rem_sto.columns],
                            style_cell={'textAlign': 'left'},
                            style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                            # filter_action="native",
                            # sort_action="native",
                            # sort_mode="multi",
                            # row_selectable="multi",
                            # row_deletable=True,
                            # selected_columns=[],
                            # selected_rows=[]
                        )
                    ])
                ]),

            ])
        ]
    else:
        return [
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Sizing Metrics"], className="subtitle padded"
                            ),

                            dash_table.DataTable(
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
                                style_table={'height': 'auto', "width": 'auto', 'overflowY': 'auto',
                                             'overflowX': 'auto'},
                                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'center'
                                    } for c in ['Value']
                                ],
                            )
                        ])
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H5(
                                    "Storage Comparison",
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
                                                    "color": "rgb(64, 149, 206)",
                                                    "line": {
                                                        "color": 'rgb(255, 255, 255)',
                                                        "width": 2,
                                                    },
                                                },
                                                name="Capacity",
                                            ),
                                            go.Bar(
                                                x=[
                                                    "Consumed (MiB)",
                                                ],
                                                y=[
                                                    str(value_dict["Consumed Storage Graph"])
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
                                                    "In Use (MiB)",
                                                ],
                                                y=[
                                                    str(value_dict["In Use Storage"])
                                                ],
                                                marker={
                                                    "color": "rgb(236, 157, 66)",
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
                        )
                    ),
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Host Information"], className="subtitle padded"
                            ),

                            dcc.Tabs([
                                dcc.Tab(label='Overview', children=[

                                    dash_table.DataTable(
                                        id='host_info',
                                        data=df_host_formatting.to_dict('records'),
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
                                        style_table={'height': 'auto', "width": 'auto', 'overflowY': 'auto',
                                                     'overflowX': 'auto'},
                                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': c},
                                                'textAlign': 'center'
                                            } for c in ['Value']
                                        ],
                                    )
                                ]),
                                dcc.Tab(label='Cluster Pie', children=[
                                    dcc.Graph(figure=go.Figure(data=go.Pie(labels=labels, values=values)))
                                ])

                            ])

                        ])
                    )
                ]
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Sizing Metrics"], className="subtitle padded"
                            ),

                            dash_table.DataTable(
                                data=df_sizer.to_dict('records'),
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
                                style_table={'height': 'auto', "width": 'auto', 'overflowY': 'auto',
                                             'overflowX': 'auto'},
                                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'center'
                                    } for c in ['Value']
                                ],
                            )
                        ])
                    ),
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Total Cores"], className="subtitle padded"
                            ),

                            # VMware license table
                            # tab VMware VM's ??
                            dcc.Graph(figure=go.Figure(data=go.Pie(labels=['Consumed', 'Free'], values=x_data[0]),
                                                       layout={}))

                        ]),

                    ),
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Total Memory"], className="subtitle padded"
                            ),

                            # VMware license table
                            # tab VMware VM's ??
                            dcc.Graph(figure=go.Figure(data=go.Pie(labels=['Consumed', 'Free'], values=x_data[1]),
                                                       layout={}))

                        ]),
                    ),
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Total Storage"], className="subtitle padded"
                            ),

                            # VMware license table
                            # tab VMware VM's ??
                            dcc.Graph(figure=go.Figure(
                                data=go.Pie(labels=['Consumed by workloads', 'Consumed by system', 'Free'],
                                            values=x_data[2]),
                                layout={})
                            )
                        ]),
                    )
                ]
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["OS Pie"], className="subtitle padded"
                            ),
                            dcc.Graph(figure=go.Figure(data=go.Pie(labels=labels1, values=values1),
                                                       layout={}))
                        ])
                    ),
                    dbc.Col(
                        html.Div([
                            html.H5(
                                ["Host ESX Versions"], className="subtitle padded"
                            ),

                            # VMware license table
                            # tab VMware VM's ??
                            dcc.Graph(figure=go.Figure(data=go.Pie(labels=labels2, values=values2),
                                                       layout={}))

                        ])
                    )
                ]
            ),
            html.Div(
                [
                    html.H5(
                        "MS Licenses",
                        className="subtitle padded",
                    ),
                    # table with MS Os
                    dash_table.DataTable(
                        data=df_os_formatting.to_dict('records'),
                        columns=[{
                            'id': 'server_version',
                            'name': 'Server Version',
                            'type': 'text'
                        }, {
                            'id': 'count',
                            'name': 'Count',
                            'type': 'numeric'
                        }],
                        style_cell={'textAlign': 'left', 'padding': '5px'},
                        style_table={'height': 'auto', "width": 'auto', 'overflowY': 'auto',
                                     'overflowX': 'auto'},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        style_cell_conditional=[
                            {
                                'if': {'column_id': c},
                                'textAlign': 'center'
                            } for c in ['Value']
                        ],
                    )
                ],
                className="two columns",
            ),
            html.Br(),
            html.Div([
                html.H5('VM(s) Removed from Scope'),

                dcc.Tabs([
                    dcc.Tab(label='vInfo', children=[
                        dash_table.DataTable(
                            data=df_rem_info.to_dict('records'),
                            columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                     df_rem_info.columns],
                            style_cell={'textAlign': 'left'},
                            style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                            # filter_action="native",
                            # sort_action="native",
                            # sort_mode="multi",
                            # row_selectable="multi",
                            # row_deletable=True,
                            # selected_columns=[],
                            # selected_rows=[]
                        )
                    ]),
                    dcc.Tab(label='vPartition', children=[
                        dash_table.DataTable(
                            data=df_rem_sto.to_dict('records'),
                            columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                     df_rem_sto.columns],
                            style_cell={'textAlign': 'left'},
                            style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto'},
                            # filter_action="native",
                            # sort_action="native",
                            # sort_mode="multi",
                            # row_selectable="multi",
                            # row_deletable=True,
                            # selected_columns=[],
                            # selected_rows=[]
                        )
                    ])
                ]),

            ])
        ]
