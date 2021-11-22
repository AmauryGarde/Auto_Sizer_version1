import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from utils import upload_data, get_sizer_info

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
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
            id='check_list',
            options=[{
                'label': 'Not Running',
                'value': 'notrunning'
            },
                {
                    'label': 'Powered Off',
                    'value': 'poweredoff'
                }
            ],
            value=[],
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
            id='radio_items',
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
        dbc.Button('Click here to remove specific VM(s)', id='button', block=True, color='secondary'),
        html.Div(id='output_vm_off'),
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

content_first_row_bis = dbc.Row([
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(id='card_title_1', children=['Card Title 1'], className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_1', children=['Sample text.'], style=CARD_TEXT_STYLE),
                    ]
                )
            ]
        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4('Card Title 2', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Sample text.', style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Card Title 3', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Sample text.', style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Card Title 4', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Sample text.', style=CARD_TEXT_STYLE),
                    ]
                ),
            ]
        ),
        md=3
    )
])

content_second_row_bis = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1'), md=4
        ),
        dbc.Col(
            dcc.Graph(id='graph_2'), md=4
        ),
        dbc.Col(
            dcc.Graph(id='graph_3'), md=4
        )
    ]
)

content_third_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_4'), md=12,
        )
    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_5'), md=6
        ),
        dbc.Col(
            dcc.Graph(id='graph_6'), md=6
        )
    ]
)

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
    Input("input1", "value"),
    Input("dropdown1", "value"),
)
def update_output(input1, dropdown1):
    if dropdown1 == "ram":
        out = u'This will search for VM(s) using {} GiB of storage or more.'.format(input1)
    elif input1 is not None:
        val = 512 * input1 * 0.01
        out = u'This will search for VM(s) using {} GiB of storage or more.'.format(val)
    else:
        out = None
    return out


@app.callback(
    Output("output2", "children"),
    Input("input2", "value"),
    Input("dropdown2", "value"),
)
def update_output2(input2, dropdown2):
    if dropdown2 == "ram":
        out = u'This will search for VM(s) using {} GiB of RAM or more.'.format(input2)
    elif input2 is not None:
        val = 10618.88 * input2 * 0.01
        out = u'This will search for VM(s) using {} GiB of RAM or more.'.format(val)
    else:
        out = None
    return out


@app.callback(
    Output('output_vm_off', 'children'),
    [Input('button', 'n_clicks')])
def update_output(n_clicks):
    if n_clicks and n_clicks > 0:
        return [html.Br(),
                dcc.Dropdown(
                    options=[
                        {'label': 'New York City', 'value': 'NYC'},
                        {'label': 'Montreal', 'value': 'MTL'},
                        {'label': 'San Francisco', 'value': 'SF'}
                    ],
                    value=['MTL', 'NYC'],
                    multi=True
                )]


@app.callback([Output('output-data-upload', 'children')],
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            upload_data(c, n) for c, n in
            zip(list_of_contents, list_of_names)]

        return children


"""
@app.callback(Output('sizer_info', 'children'),
              [Input('submit_button', 'n_clicks')],
              [State('signal', 'data')])
def give_sizing_info(n_clicks, stored_db):
    df_vinfo = stored_db[0]
    df_vpartition = stored_db[1]
    df_vhost = stored_db[2]
    return get_sizer_info(df_vinfo, df_vpartition, df_vhost)
"""

app.run_server(debug=False)
