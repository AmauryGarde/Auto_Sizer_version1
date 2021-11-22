import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from v1_ready.utils_v2 import upload_data, get_sizer_info, read_rvtools
import dash_table

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa',
    'overflowY': 'scroll'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'top': 0,
    'padding': '20px 10px'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}
controls = dbc.FormGroup(
    [
        html.P('Upload RVtools Excel', style={
            'textAlign': 'center'
        }),
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
        html.P('Exclude VM(s):', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='exclude_vm',
            options=[{
                'label': 'Not Running',
                'value': 'notrunning'
            },
                {
                    'label': 'Powered Off',
                    'value': 'poweredoff'
                }
            ],
            value=["notrunning", "poweredoff"],
            inline=True,
            style={
                'margin': 'auto'
            },
        )]),
        html.Br(),
        html.P('Choose Storage Unit:', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.RadioItems(
            id='choose_sto_unit',
            options=[{
                'label': 'Gibibyte (Gib)',
                'value': 'gib'
            },
                {
                    'label': 'Tebibyte (TiB)',
                    'value': 'tib'
                }
            ],
            value='gib',
            style={
                'margin': 'auto'
            },
            inline=True
        )]),
        html.Hr(),
        html.H4('Remove Top VM(s) by spec.', style={
            'textAlign': 'center'
        }),
        html.Div(
            [
                html.I(
                    "Choose number of VM(s) to remove by RAM ranking."),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dcc.Input(id="input3", type="number", placeholder="Input value"),
                    ],
                        width={'order': 'first',
                               'size': 'auto'}
                    ),
                    dbc.Col([
                        dcc.Markdown('''
                        most RAM consuming VM(s) will be removed.
                        '''),
                    ])
                ], align='center'
                ),
                html.Br(),
                html.I(
                    "Choose number of VM(s) to remove by storage ranking."),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dcc.Input(id="input4", type="number", placeholder="Input value"),
                    ],
                        width={'order': 'first',
                               'size': 'auto'}
                    ),
                    dbc.Col([
                        dcc.Markdown('''
                        most storage consuming VM(s) will be removed.
                        '''),
                    ])
                ], align='center'
                ),
            ],
        ),
        html.Hr(),
        html.H4('VM(s) Search by Spec.', style={
            'textAlign': 'center'
        }),
        html.Div(
            [
                html.I(
                    "Choose maximum percent (%) of host RAM a single VM is allowed to use or the maximum value of RAM \
                    in GiB."),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dcc.Input(id="input1", type="number", placeholder="Input value"),
                    ],
                        width={'order': 'first',
                               'size': 'auto'}
                    ),
                    dbc.Col([
                        dcc.Dropdown(
                            id='dropdown1',
                            options=[
                                {'label': '% of host RAM', 'value': 'percent'},
                                {'label': 'GiB of RAM', 'value': 'ram'}
                            ],
                            value='percent',
                            searchable=False,
                            clearable=False),
                    ])
                ], align='center'
                ),
                html.Div(id='output'),
                html.Br(),
                html.I(
                    "Choose maximum percent (%) of host storage a single VM is allowed to use or the maximum value of \
                    storage in GiB."),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dcc.Input(id="input2", type="number", placeholder="Input value"),
                    ],
                        width={'order': 'first',
                               'size': 'auto'}
                    ),
                    dbc.Col([
                        dcc.Dropdown(
                            id='dropdown2',
                            options=[
                                {'label': '% of host Storage', 'value': 'percent'},
                                {'label': 'GiB of Storage', 'value': 'sto'}
                            ],
                            value='percent',
                            searchable=False,
                            clearable=False),
                    ])
                ], align='center'
                ),
            ],
        ),
        html.Div(id="output2"),
        html.Hr(),
        html.H4('Remove VM(s) by name', style={
            'textAlign': 'center'
        }),
        html.Br(),
        dcc.Dropdown(
            id='out_vm',
            # options=[
            #    {'label': str(i), 'value': str(i)} for i in options
            # ],
            value=[],
            multi=True
        ),
        # dbc.Button('Click here to remove specific VM(s)', id='button', block=True, color='secondary'),
        # html.Div(id='output_vm_off'),
        html.Hr(),
        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Submit',
            color='primary',
            block=True
        )
    ]
)

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

content_first_row = html.Div(id='output-data-upload')

content_second_row = html.Div(id='sizer_info')

content = html.Div(
    [
        html.H2('Sizer Automation Prototype', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_second_row
    ],
    style=CONTENT_STYLE
)

sidebar = html.Div(
    [
        html.H2('Parameters', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([sidebar, content])


@app.callback(
    Output("output", "children"),
    [Input("input1", "value"),
     Input("dropdown1", "value")])
def update_output(input1, dropdown1):
    if dropdown1 == "ram" and input1 is not None:
        return u'This will search for VM(s) using {} GiB of RAM or more.'.format(input1)
    elif dropdown1 == 'percent' and input1 is not None:
        val = 512 * input1 * 0.01
        return u'This will search for VM(s) using {} GiB of RAM or more.'.format(val)



@app.callback(
    Output("output2", "children"),
    [Input("input2", "value"),
     Input("dropdown2", "value")])
def update_output2(input2, dropdown2):
    if dropdown2 == "sto" and input2 is not None:
        return u'This will search for VM(s) using {} GiB of storage or more.'.format(input2)
    elif dropdown2 == 'percent' and input2 is not None:
        val = 10618.88 * input2 * 0.01
        return u'This will search for VM(s) using {} GiB of storage or more.'.format(val)



@app.callback([Output('output-data-upload', 'children'),
               Output('out_vm', 'options')],
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output4(contents, filename):
    if contents is not None:
        dbs = [read_rvtools(c, n) for c, n in zip(contents, filename)]
        # children = [
        #    upload_data(c, n) for c, n in
        #    zip(list_of_contents, list_of_names)]
        #
        # print(type(children[0]))

        out1 = html.Div([
            html.H5(filename),

            dcc.Tabs([
                dcc.Tab(label='vInfo', children=[
                    dash_table.DataTable(
                        data=dbs[0][0].to_dict('records'),
                        columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                 dbs[0][0].columns],
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
                        data=dbs[0][1].to_dict('records'),
                        columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                 dbs[0][1].columns],
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
                        data=dbs[0][2].to_dict('records'),
                        columns=[{'name': i, 'id': i, "deletable": False, "selectable": False} for i in
                                 dbs[0][2].columns],
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

        vm_name = dbs[0][0].VM.values
        out2 = [
            {'label': str(i), 'value': str(i)} for i in vm_name
        ]

        return [out1, out2]
    else:
        return ['', '']


@app.callback(Output('sizer_info', 'children'),
              Input('submit_button', 'n_clicks'),
              [State('upload-data', 'contents'),
               State('upload-data', 'filename'),
               State('input1', 'value'),
               State('dropdown1', 'value'),
               State('input2', 'value'),
               State('dropdown2', 'value'),
               State('choose_sto_unit', 'value'),
               State('exclude_vm', 'value'),
               State('out_vm', 'value'),
               State('input3', 'value'),
               State('input4', 'value')])
# State('out_vm', 'value')])
def give_sizing_info(n_clicks, contents, filename, filter1, filter12, filter2, filter22, sto_unit, exclude_vm, out_vm,
                     top_ram, top_sto):
    if contents is not None:
        dbs = [read_rvtools(c, n) for c, n in zip(contents, filename)]

        return get_sizer_info(dbs[0][0], dbs[0][1], dbs[0][2], exclude_vm, filter1, filter12, filter2, filter22,
                              sto_unit, out_vm, top_ram, top_sto)


app.run_server(debug=False)
