"""
app.py
This is the main file for the dashboard of ANITA

This module contains the layout and callback functions for the dashboard
"""

# ----- Imports
import dash
import pandas as pd
from datetime import datetime
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import time
import plotly.graph_objs as go
import importlib
from math import sqrt
import numpy as np

# import own modules
network_graph = importlib.import_module('networkgraph')
plots = importlib.import_module('plots')

# Setup the server of DASH
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# ------ Data
df_product = pd.read_csv('data/df_product.csv')
df_vendor = pd.read_csv('data/df_vendor.csv')


# ------ (helper) Functions
def get_market_list():
    """
    :return: list of unique markets in dataset df_product and df_vendor
    """
    markets = df_product.market.unique().tolist() + df_vendor.market.unique().tolist()
    return list(set(markets))


def get_date_list():
    """
    Combines all dump dates of the df_product and df_vendor datasets and returns them, including the max and min
    :return: date_dict, a dict containing all the dump dates in the data
    :return: min_date, the min dump date
    :return: max_date, the max dump date
    """
    # Get unix dates
    unix_dates = df_product.extraction_date.unique().tolist() + df_vendor.extraction_date.unique().tolist()
    unix_dates = sorted(list(set(unix_dates)))

    # Create date dict {datetime_object : unix_date}
    date_dict = {datetime.fromtimestamp(date).date(): date for date in unix_dates}

    # Find min_date
    min_date_unix = min(unix_dates)
    min_date = (min_date_unix, datetime.fromtimestamp(min_date_unix).date())

    # Find max_date
    max_date_unix = max(unix_dates)
    max_date = (max_date_unix, datetime.fromtimestamp(max_date_unix).date())

    return date_dict, min_date, max_date


def filter_df(df, market_list, start_date, end_date):
    """
    Filters the DF based on given parameters
    :param df: the DF to filter (can be df_vendor or df_product, or a df with same column names)
    :param market_list: a list of the markets (e.g. ['berlusconi', 'agartha'])
    :param start_date: date as datetime object
    :param end_date: date as datetime object
    :return: df, the filtered df
    """
    # get the unix values for the start and end date
    start_date_unix = time.mktime(start_date.timetuple())
    end_date_unix = time.mktime(end_date.timetuple())

    # Filter actions
    df = df[df['market'].isin(market_list)]
    df = df[df['extraction_date'] >= start_date_unix]
    df = df[df['extraction_date'] <= end_date_unix]

    return df


def filter_df_market(df, market_list):
    """
    Filters the DF, similar ot filter DF, but only filters on market list
    :param df: the DF to filter (can be df_vendor or df_product, or a df with same column names)
    :param market_list: a list of the markets (e.g. ['berlusconi', 'agartha'])
    :return: df, the filtered df
    """
    return df[df['market'].isin(market_list)]


def get_duplicate(df, column):
    """
    Get the duplicate values for a given column over the different markets.
    Thus if column = 'name' it will return all the values for 'name' that are duplicate over the different markets
    :param df: the DF to use (can be df_vendor or df_product, or a df with same column names)
    :param column: str, the column name to look for duplicates
    :return: set of the duplicate values
    """
    # Initiate a list to store duplicates
    duplicate = []
    for index in df.groupby(['market', column]).count().index:
        duplicate.append(index[1])
    # return only values that are stored more than once in the list
    return set([value for value in duplicate if duplicate.count(value) > 1])


def check_value(value):
    """
    Check the value and returns 'not available' if the value is an empty or non value. To make the output more beautiful
    :param value: the value to check
    :return:
    """

    # If the value is a list in string format, change
    if type(value) == str:
        if value[0] == '[':
            value = value.replace('[', '').replace(']', '').replace("/'", "")

    # The value is unavaible if the value is none or other mentioned below
    if value in ['', 'Nan', np.nan]:
        return 'Not available'
    if value is None:
        return 'Not available'

    # If the value was not missing, just return value
    else:
        return value


# ------ App lay-out
app.layout = html.Div([

    # Div for the header of the page
    html.Div(
        [
            # Left side of header
            html.Div(
                [
                    html.H5("LOGO PLACEHOLDER")
                ],
                className="one-third column",
            ),
            # Mid of header
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "ANITA DASHBOARD",
                                style={"margin-bottom": "0px"},
                            ),
                        ]
                    )
                ],
                className="one-half column",
                id="title",
            ),
            # Right of header
            html.Div(
                [
                    html.A(
                        html.Button("ANITA PROJECT", id="learn-more-button"),
                        href="https://www.anita-project.eu",
                    )
                ],
                className="one-third column",
                id="button",
            ),
        ],
        id="header",
        className="row flex-display",
        style={"margin-bottom": "0px"},
    ),

    # Top tabs (Descriptives, Network, Specifics)
    dcc.Tabs([

        # Fist tab
        dcc.Tab(label='Descriptives', children=[
            html.Div([

                # Filters
                html.Div([
                    html.H5('Data Filter'),
                    html.B('Pick a date range:'),
                    dcc.DatePickerRange(
                        id='dp_export_date_tab1',
                        month_format='MMMM Y',
                        end_date_placeholder_text='MMMM Y',
                        start_date=get_date_list()[1][1],  # min_date
                        end_date=get_date_list()[2][1],  # max_date
                    ),
                    html.B('Choose markets to include:'),
                    dcc.Dropdown(
                        id='dd_market_tab1',
                        options=[{'label': key, 'value': key} for key in
                                 get_market_list()],
                        value=get_market_list(),
                        multi=True,
                    ),
                ],
                    className="pretty_container three columns"
                ),

                # Graphs
                html.Div([
                    html.Div([
                        # Callback function fills this children with mini containers
                        # function: update_mini_containers()
                    ],
                        className="row container-display",
                        id="mini_containers"
                    ),

                    # Sub tabs
                    html.Div([
                        dcc.Tabs([
                            dcc.Tab(label='Unique vendors', children=[
                                # Callback function fills this with first graph about unique vendors
                                # function: create_graph_unique()
                                dcc.Graph(id='graph_unique_vendors')
                            ],
                                    className='subtab'
                                    ),
                            dcc.Tab(label='Unique products', children=[
                                # Callback function fills this with first graph about unique products
                                dcc.Graph(id='graph_unique_products')
                            ],
                                    className='subtab',
                                    ),
                        ], ),
                    ],
                        id='unique_vendor_graph',
                        className="row flex-display",
                    ),

                ],
                    className="pretty_container nine columns",
                ),

            ],
                className="row flex-display",
            ),
        ], ),

        # Second tab
        dcc.Tab(label='Network', children=[
            html.Div([

                # Filters
                html.Div([
                    html.H5('Data Filter'),
                    html.B('Choose markets to include:'),
                    dcc.Dropdown(
                        id='dd_market_tab2',
                        options=[{'label': key, 'value': key} for key in
                                 get_market_list()],
                        value=get_market_list(),
                        multi=True,
                    ),

                    html.H6('Duplicates'),
                    html.P(id='duplicate_name'),  # Filled using callback, function: get_number_of_duplicates()
                    html.P(id='duplicate_pgp'),  # Filled using callback, function: get_number_of_duplicates()

                    html.B('Select a value to investigate'),
                    dcc.RadioItems(
                        id='ri_name_pgp_tab2',
                        options=[{'label': i, 'value': i} for i in ['Name', 'PGP']],
                        value='Name'
                    ),
                    dcc.Dropdown(
                        id='dd_duplicate_tab2',
                        options=[{'label': key, 'value': key} for key in
                                 get_market_list()],  # Filled using callback, function: update_duplicate_dropdown()
                        value='no selection',
                        multi=False,
                    ),
                    html.Br(),
                    dcc.Checklist(
                        # This checklist makes the products visible in the network graph or not
                        # Function: create_network_graph()
                        options=[
                            {'label': 'Show products', 'value': 'ShowProduct'},
                        ],
                        value=[],
                        id='check_show_product_tab2',
                    )

                ],
                    className="pretty_container three columns"
                ),
                html.Div([
                    # The graph will be built using an callback function
                    dcc.Graph(id='network-graph'),
                ],
                    className="pretty_container nine columns",
                ),

            ],
                className="row flex-display",
            ),
            html.Div([
                html.Div([],
                         # This div will be filled with more information using an callback function
                         # Function: show_more_information()
                         id='more_information_tab2',
                         ),

            ],
                className="pretty_container twelve columns"
            ),
        ], ),

        # Third tab
        dcc.Tab(label='Specifics', children=[
            html.Div([
                html.Div([

                    # Filters
                    html.H5('Data Filter'),
                    html.B('Pick a date range:'),
                    dcc.DatePickerRange(
                        id='dp_export_date_tab3',
                        month_format='MMMM Y',
                        end_date_placeholder_text='MMMM Y',
                        start_date=get_date_list()[1][1],
                        end_date=get_date_list()[2][1],
                    ),
                    html.B('Choose markets to include:'),
                    dcc.Dropdown(
                        id='dd_market_tab3',
                        options=[{'label': key, 'value': key} for key in
                                 get_market_list()],
                        value=get_market_list(),
                        multi=True,
                    ),

                ],
                    className="pretty_container three columns"
                ),

                # Right part of page
                html.Div([
                    # Subtabs (vendor & product)
                    dcc.Tabs([
                        dcc.Tab(label='Vendor', children=[
                            html.B('Search for vendor to select:'),
                            html.Div([
                                html.Div([
                                    dcc.Dropdown(
                                        id='market_search_vendor',
                                        options=[],  # Will be defined using function: callback update_market_search()
                                        value='non selected',
                                        placeholder='select a market...'
                                    ),
                                ], className='one column',
                                    style={'width': '30%'}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='vendor_search',
                                        options=[],  # Will be defined using callback function: update_vendor_dropdown()
                                        value='non selected',
                                        placeholder='select a vendor...'
                                    ),
                                ], className='one column',
                                    style={'width': '30%'}),
                            ],
                                className='row'),
                            html.Div([
                                html.Div([
                                    html.P('Select a dump date:')
                                ],
                                    style={'width': '29.5%',
                                           'float': 'left',
                                           'margin-top': '8px',
                                           'margin-left': '1%', }),
                                html.Div([
                                    dcc.Dropdown(
                                        id='dump_vendor',
                                        options=[],  # Will be defined using callback,
                                        # function: update_date_dropdown_vendor()
                                        value='non selected',  # Will be defined using callback,
                                        # function: update_date_dropdown_vendor
                                        placeholder='select a dump date...'
                                    ),
                                ], className='one column',
                                    style={'width': '30%',
                                           'float': 'left'}),

                            ],
                                className='row',
                                style={'margin-top': '1%', }
                            ),
                            html.Hr(),
                            html.Div([
                                # Will be filled using callback function: update_vendor_info_div()
                            ],
                                id='vendor_information'
                            ),
                            html.Div([
                                html.H6('Trend analysis'),
                                html.B('Select a feature to see the trend:'),
                                dcc.Dropdown(
                                    id='vendor_feature',
                                    options=[{'label': 'score', 'value': 'score'},
                                             {'label': 'sales', 'value': 'sales'}, ],
                                    value='non selected',
                                    style={'width': '40%'}
                                ),
                            ],
                                style={'display': 'None'},  # Will be set to visible using callback,
                                                            # function: show_feature_selection_vendor()
                                id='show_vendor_feature',
                            ),
                            html.Div([
                            ],
                                # Plot will be returned using callback function, function: create_vendor_trend_plot()
                                id='vendor_trend'
                            ),
                        ],
                                className='subtab', ),

                        dcc.Tab(label='Product', children=[
                            html.B('Search for product to select:'),
                            html.Div([
                                html.Div([
                                    dcc.Dropdown(
                                        id='market_search_product',
                                        options=[],  # Will be defined using function: callback update_market_search()
                                        value='non selected',
                                        placeholder='select a market to filter...',
                                    ),
                                ], className='one column',
                                    style={'width': '30%'}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='vendor_search_product',
                                        options=[],     # Will be defined using callback,
                                                        # function: update_vendor_dropdown_product()
                                        value='all',
                                        placeholder='select a vendor to filter...',
                                    ),
                                ], className='one column',
                                    style={'width': '30%'}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='product_search',
                                        options=[],
                                        value='non selected',   # Will be defined using callback,
                                                                # function: update_vendor_dropdown()
                                        placeholder='select a product...',
                                    ),
                                ], className='one column',
                                    style={'width': '30%'}),
                            ],
                                className='row'),
                            html.Div([
                                html.Div([
                                    html.P('Select a dump date:')
                                ],
                                    style={'width': '29.5%',
                                           'float': 'left',
                                           'margin-top': '8px',
                                           'margin-left': '1%', }),
                                html.Div([
                                    dcc.Dropdown(
                                        id='dump_product',
                                        options=[],         # Will be defined using callback,
                                                            # function: update_product_dump_dropdown()
                                        value='non selected',   # Will be defined using callback,
                                                                # Function: update_product_dump_dropdown()
                                        placeholder='select a dump date...'
                                    ),
                                ], className='one column',
                                    style={'width': '30%',
                                           'float': 'left'}),
                            ],
                                className='row',
                                style={'margin-top': '1%', }
                            ),
                            html.Hr(),
                            html.Div([
                                # Will be filled using a callback function: update_product_div()
                            ],
                                id='product_information'
                            ),
                            html.Div([
                                html.H6('Trend analysis for the price'),
                            ],
                                style={'display': 'None'},  # Will be made visible using callback
                                id='show_product_feature',
                            ),
                            html.Div([
                                # Will be filled with graph using callback
                            ],
                                id='product_trend'
                            ),
                        ],
                                className='subtab', ),

                    ], ),

                ],
                    className="pretty_container nine columns"
                ),

            ],
                className="row flex-display"),

        ], ),

    ], )
],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"}
)


# ----- CALL-BACK FUNCTIONS

# filters tab1 -> mini container values
@app.callback(
    Output("mini_containers", "children"),
    [
        Input("dp_export_date_tab1", "start_date"),
        Input("dp_export_date_tab1", "end_date"),
        Input("dd_market_tab1", "value"),
    ],
)
def update_mini_containers(start_date, end_date, market_list):
    """
    Takes the filter parameters and returns a div containing the values for some descriptives about the data:
        - # unique dump dates
        - # unique vendors
        - # unique products
        - # unique markets
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :return: html.Div(): return a Div element containing the different containers showing the information
    """

    # Reformat the datepicker str format into datetime objects
    dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Filter both data sets:
    df_selection_product = filter_df(df_product, market_list, dt_start_date, dt_end_date)
    df_selection_vendor = filter_df(df_vendor, market_list, dt_start_date, dt_end_date)

    unique_dumps = list(set(
        df_selection_product.extraction_date.unique().tolist() + df_selection_vendor.extraction_date.unique().tolist()))
    unique_markets = list(set(
        df_selection_product.market.unique().tolist() + df_selection_vendor.market.unique().tolist()))

    return html.Div(
        [html.H6(), html.P(
            # Number of dump dates
            f"{len(unique_dumps)}  unique dump dates")],
        id="container1",
        className="mini_container",
    ), html.Div(
        # Number of unique vendors
        [html.H6(), html.P(f"{df_selection_vendor.name.nunique()} unique vendors")],
        id="container2",
        className="mini_container",
    ), html.Div(
        # Number of unique products
        [html.H6(), html.P(f"{df_selection_product.product_id.nunique()} unique products")],
        id="container3",
        className="mini_container",
    ), html.Div(
        [html.H6(), html.P(
            # Number of unique markets
            f"{len(unique_markets)} unique markets")],
        id="container4",
        className="mini_container",
    )


# filters tab1 -> graph unique vendors & graph unique product
@app.callback(
    [Output("graph_unique_vendors", "figure"),
     Output("graph_unique_products", "figure"), ],
    [
        Input("dp_export_date_tab1", "start_date"),
        Input("dp_export_date_tab1", "end_date"),
        Input("dd_market_tab1", "value"),
    ],
)
def create_graph_unique(start_date, end_date, market_list):
    """
    Creates the unique vendor graph. This function filters data and uses the plots.unique_bar_plot() function to
    create the bar plot.
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :return: go.Figure(), the bar plot
    """
    # Reformat the datepicker str format into datetime objects
    dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Filter data sets
    df_selection_vendor = filter_df(df_vendor, market_list, dt_start_date, dt_end_date)
    df_selection_product = filter_df(df_product, market_list, dt_start_date, dt_end_date)

    # Find the x, y and text (for hover) data
    x_values_vendor = df_selection_vendor.groupby('market').count().index
    y_values_vendor = df_selection_vendor.groupby('market')['name'].nunique().tolist()
    text_values_vendor = df_selection_vendor.groupby('market')['extraction_date'].nunique().tolist()

    x_values_product = df_selection_product.groupby('market').count().index
    y_values_product = df_selection_product.groupby('market')['product_id'].nunique().tolist()
    text_values_product = df_selection_product.groupby('market')['extraction_date'].nunique().tolist()

    # return two plots
    return plots.unique_bar_plot(x_values_vendor, y_values_vendor, text_values_vendor), \
           plots.unique_bar_plot(x_values_product, y_values_product, text_values_product)


# Market selection -> textual number of duplicate values (names, pgp)
@app.callback([Output('duplicate_name', 'children'),
               Output('duplicate_pgp', 'children'),
               ],
              [Input('dd_market_tab2', 'value')])
def get_number_of_duplicates(market_list):
    """
    Returns the number of duplicates based on 'name' and 'pgp' in the data
    :param market_list: list of strings of market names
    :return: Str: For the different html.P values
    """
    df_selection_vendor = filter_df_market(df_vendor, market_list)

    return f"{len(get_duplicate(df_selection_vendor, 'name'))} duplicate names found", \
           f"{len(get_duplicate(df_selection_vendor, 'pgp'))} duplicate pgp's found"


# Radio Item PGP/Name & Market selection -> dropdown options
@app.callback(
    Output('dd_duplicate_tab2', 'options'),
    [Input('ri_name_pgp_tab2', 'value'),
     Input('dd_market_tab2', 'value')]
)
def update_duplicate_dropdown(value, market_list):
    """
    Updates the dropdown menu options based on duplicate pgp or names of vendors
    :param value: str, value of ratio item choosing between 'Name' and 'PGP'
    :param market_list: list of strings of market names
    :return: list of dicts, options for dropdown
    """
    df_selection_vendor = filter_df_market(df_vendor, market_list)
    if value == 'Name':
        return [{'label': i, 'value': i} for i in get_duplicate(df_selection_vendor, 'name')]
    if value == 'PGP':
        return [{'label': df_vendor[df_vendor['pgp'] == i]['name'].unique()[0], 'value': i} for i in
                get_duplicate(df_selection_vendor, 'pgp')]


# PGP/Name & Market selection &  visibility product -> network graph
@app.callback(
    Output('network-graph', 'figure'),
    [Input('ri_name_pgp_tab2', 'value'),
     Input('dd_duplicate_tab2', 'value'),
     Input('check_show_product_tab2', 'value')], )
def create_network_graph(name_pgp, value, show_product):
    """
    Creates the network graph using functions in networkgraph module.
    :param name_pgp: str, value of ratio item choosing between 'Name' and 'PGP'
    :param value: str, name or pgp selected in dropdown
    :param show_product: list, ['ShowProduct'] when products should be included
    :return: go.figure() Network graph
    """
    # If no network graph to be shown, show text to make selection
    if (value == 'no selection') or (len(value) < 100 and name_pgp == 'PGP') or (
            len(value) > 100 and name_pgp == 'Name'):
        # Empty plot
        layout = go.Layout(
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            xaxis={'showgrid': False, 'zeroline': False},  # no gridlines
            yaxis={'showgrid': False, 'zeroline': False},  # no gridlines
            showlegend=False,
            title='Select a PGP or vendor Name to get started',
        )
        fig = go.Figure(layout=layout)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        return fig

    if show_product == ['ShowProduct']:
        show_product_boolean = True
    else:
        show_product_boolean = False

    # Get the nodes and edges
    nodes, edges = network_graph.get_nodes_and_edges(df_vendor, df_product, name_pgp, value,
                                                     products=show_product_boolean)

    return network_graph.create_network_graph(nodes, edges)


# Click on network graph -> more information div
@app.callback(Output('more_information_tab2', 'children'),
              [Input('network-graph', 'clickData')],
              [State('network-graph', 'figure')])
def show_more_information(clickdata, figure):
    """
    Creates a div with more information to show beneath the network graph
    :param clickdata: json format, data when clicked on the graph
    :param figure: json format, data about the plot itself, needed to re-engineer relations
    :return: html.Div() containing the information to show
    """
    # When no data
    if clickdata is None:
        return html.H6('Click on a node in the graph to get information.')
    info_html = html.H6('Click on a node in the graph to get information.')

    # We use the color to identify the type of object
    # Initiate lists in order to find relations (re-engineer)
    inv_node_colors = {v: k for k, v in network_graph.node_colors.items()}
    vendor_list = []
    market_list = []
    x_coord = []  # for finding accompanying market to product
    y_coord = []  # for finding accompanying market to product
    text_list = []
    type_list = []

    # fill lists to use for re-engineering
    if len(figure['data']) > 1:
        for part in figure['data']:
            if 'hoverinfo' in part:
                for index, color in enumerate(part['marker']['color']):
                    if inv_node_colors[color] == 'vendor':
                        vendor_list.append(part['text'][index])
                        type_list.append('vendor')
                    if inv_node_colors[color] == 'market':
                        market_list.append(part['text'][index])
                        type_list.append('market')
                    if inv_node_colors[color] == 'pgp':
                        type_list.append('pgp')
                    if inv_node_colors[color] == 'product':
                        type_list.append('product')
                for index, coord in enumerate(part['x']):
                    x_coord.append(coord)
                    y_coord.append(part['y'][index])
                    text_list.append(part['text'][index])
    vendor_list = [vendor[:-1] for vendor in vendor_list]  # For some reason a ' ' is added, thus removed here
    market_list = [market[:-1] for market in market_list]  # For some reason a ' ' is added, thus removed here
    text_list = [text[:-1] for text in text_list]  # For some reason a ' ' is added, thus removed here

    # Fill Div based on type
    if clickdata is not None:
        # Get the type of data based on marker color
        node_type = inv_node_colors[clickdata['points'][0]['marker.color']]
        point_text = clickdata['points'][0]['text'][:-1]

        # VENDOR
        if node_type == 'vendor':
            market_string = ', '.join(market_list)

            # Get all the data to show
            extraction_date_list = []
            score_list = []
            vendor_since_list = []
            vendor_since_deviation_list = []
            last_login_list = []
            last_login_deviation_list = []
            sales_list = []
            info_list = []
            pgp_list = []

            for market in market_list:
                try:
                    # Get the data per market, the vendor can be attached to multiple markets (duplicate)
                    data_row = \
                        df_vendor[(df_vendor['name'] == point_text) & (df_vendor['market'] == market)].sort_values(
                            'extraction_date').iloc[0]
                except IndexError:
                    continue
                try:
                    extraction_date_list.append(datetime.fromtimestamp(data_row['extraction_date']).date())
                except ValueError:
                    extraction_date_list.append('Not available')
                try:
                    score_list.append(check_value(data_row['score_normalized']))
                except ValueError:
                    score_list.append('Not available')
                try:
                    vendor_since_list.append(datetime.fromtimestamp(data_row['registration_date']).date())
                except ValueError:
                    vendor_since_list.append('Not available')
                try:
                    vendor_since_deviation_list.append(check_value(data_row['registration_date_deviation']))
                except ValueError:
                    vendor_since_deviation_list.append('Not available')
                try:
                    last_login_list.append(datetime.fromtimestamp(data_row['last_login']).date())
                except ValueError:
                    last_login_list.append('Not available')
                try:
                    last_login_deviation_list.append(check_value(data_row['last_login_deviation']))
                except ValueError:
                    last_login_deviation_list.append('Not available')
                try:
                    sales_list.append(check_value(data_row['sales']))
                except ValueError:
                    sales_list.append('Not available')
                try:
                    info_list.append(check_value(data_row['info']))
                except ValueError:
                    info_list.append('Not available')
                try:
                    pgp_list.append(check_value(data_row['pgp']))
                except ValueError:
                    pgp_list.append('Not available')

            # Create the html format
            info_html = html.Div([
                html.B(f'{node_type}'),
                html.H6(f'{point_text}'),
                dcc.Markdown(f"**Active on markets:** {market_string}"),
                html.Hr(),

                html.Div([
                    html.Div([
                        html.H6(f"Market : {market}"),
                        html.Div([
                            html.Div([
                                dcc.Markdown(f"**Most recent dump of data** : {extraction_date_list[index]}"),
                                dcc.Markdown(f"**Score (between 0 and 1)** : {score_list[index]} "),
                                dcc.Markdown(
                                    f"**Vendor since (around)**: {vendor_since_list[index]}" +
                                    "(*Precision: {vendor_since_deviation_list[index]})*"),
                                dcc.Markdown(
                                    f"**Vendor last login (around)** : {last_login_list[index]}" +
                                    "(*Precision: {last_login_deviation_list[index]})*"),
                                dcc.Markdown(f"**Sales by vendor** : {sales_list[index]} "),
                                html.B('PGP:'),
                                html.Div([
                                    html.P(pgp_list[index])
                                ],
                                    style={'word-break': 'break-all',
                                           "overflow-y": "scroll",
                                           "height": "200px",
                                           }),
                            ],
                                className="pretty_container six columns", ),
                            html.Div([
                                html.B('Info on page:'),
                                html.Div([
                                    html.P(info_list[index])
                                ],
                                    style={'word-break': 'break-all',
                                           "overflow-y": "scroll",
                                           "height": "400px"}),
                            ],
                                className="pretty_container six columns", ),
                        ],
                            className="row flex-display",
                        ),
                        html.Hr(),
                    ],
                    )
                    # Loop over the different markets
                    for index, market in enumerate(market_list)
                ],

                )
            ])

        # PRODUCT
        if node_type == 'product':
            # Find the accompanying market
            # The network graph does not give information about what is connected to what when you click on it
            # Thus we connect the market to the product based on closeness. THe closest market is the market belonging
            # to that product
            market_to_check = []
            market_to_check_index = []
            product_index = text_list.index(point_text)
            product_coord = (x_coord[product_index], y_coord[product_index])
            for index, item_type in enumerate(type_list):
                if item_type == 'market':
                    if product_coord[0] > x_coord[index]:
                        x_value = product_coord[0] - x_coord[index]
                    else:
                        x_value = x_coord[index] - product_coord[0]
                    if product_coord[1] > y_coord[index]:
                        y_value = product_coord[1] - y_coord[index]
                    else:
                        y_value = y_coord[index] - product_coord[1]
                    pythagoras = sqrt(x_value * x_value + y_value * y_value)
                    market_to_check.append(pythagoras)
                    market_to_check_index.append(index)

            # Get the re-engineerd market
            market = text_list[market_to_check_index[market_to_check.index(min(market_to_check))]]
            max_export_date = df_product[(df_product['market'] == market) & (df_product['name'] == point_text)][
                'extraction_date'].max()
            latest_product = \
                df_product[(df_product['market'] == market) & (df_product['name'] == point_text)].sort_values(
                    'extraction_date', ascending=False).iloc[0]

            # Create HTML format
            info_html = html.Div([
                html.B(f'{node_type}'),
                html.H6(f'{point_text}'),
                html.Hr(),
                html.Div([
                    html.Div([
                        dcc.Markdown(f"**Market** : {market}"),
                        dcc.Markdown(f"**Last dump date** : {datetime.fromtimestamp(max_export_date).date()}"),
                        dcc.Markdown(f"**Vendor** : {latest_product['vendor']}"),
                        dcc.Markdown(f"**Ships from** : {check_value(latest_product['ships_from'])}"),
                        dcc.Markdown(f"**Ships to** : {check_value(latest_product['ships_to'])}"),
                        dcc.Markdown(f"**Price** : {check_value(latest_product['price'])} *(as stated on page)*"),
                        dcc.Markdown(
                            f"**Price in euros** : {check_value(latest_product['price_eur'])} *(can be converted)*"),
                        dcc.Markdown(f"**Macro category** : {check_value(latest_product['macro_category'])}"),
                        dcc.Markdown(f"**Micro category** : {check_value(latest_product['micro_category'])}"),
                    ],
                        className="pretty_container six columns", ),
                    html.Div([
                        html.B('Info on page:'),
                        html.Div([
                            html.P(f"{check_value(latest_product['info'])}")
                        ],
                            style={'word-break': 'break-all',
                                   "overflow-y": "scroll",
                                   "height": "400px"}),
                    ],
                        className="pretty_container six columns", ),
                ],
                    className="row flex-display",
                ),
                html.Hr(),
            ])

        # MARKET
        if node_type == 'market':
            market = point_text
            min_export_unix = min(df_vendor[df_vendor['market'] == market]['extraction_date'].min(),
                                  df_product[df_product['market'] == market]['extraction_date'].min())
            max_export_unix = max(df_vendor[df_vendor['market'] == market]['extraction_date'].max(),
                                  df_product[df_product['market'] == market]['extraction_date'].max())

            # Create HTML
            info_html = html.Div([
                html.B(f'{node_type}'),
                html.H6(f'{point_text}'),
                html.Hr(),
                dcc.Markdown(f"**Last export** : {datetime.fromtimestamp(max_export_unix).date()}"),
                dcc.Markdown(f"**First export** : {datetime.fromtimestamp(min_export_unix).date()}"),
                dcc.Markdown(
                    f"**Number of exports** : {check_value(df_vendor[df_vendor['market'] == market].extraction_date.nunique())}"),
                dcc.Markdown(
                    f"**Number of unique products** : {check_value(df_product[df_product['market'] == market].product_id.nunique())}"),
                dcc.Markdown(
                    f"**Number of unique vendors** : {check_value(df_vendor[df_vendor['market'] == market].name.nunique())}"),
            ])

        # PGP
        if node_type == 'pgp':
            pgp_list = []
            for vendor in vendor_list:
                pgp_list += df_vendor[df_vendor['name'] == vendor]['pgp'].unique().tolist()

            info_html = html.Div([
                html.B(f'{node_type}'),
                html.H6(f' PGP of {vendor_list[0]}'),
                html.Div([
                    html.P(pgp)
                    for pgp in pgp_list
                ],
                    style={'word-break': 'break-all'}),
            ],
                className="pretty_container twelve columns",
            )

    return info_html


# Filters tab 3 -> market selection
@app.callback(
    [Output("market_search_vendor", "options"),
     Output("market_search_product", "options"), ],
    [
        Input("dp_export_date_tab3", "start_date"),
        Input("dp_export_date_tab3", "end_date"),
        Input("dd_market_tab3", "value"),
    ],
)
def update_market_search(start_date, end_date, market_list):
    """
    Creates and returns the options for the the market options for vendor and product subtabs
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :return: 2x list of dicts containing the options for the market dropdown menus
    """
    dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df_selection_vendor = filter_df(df_vendor, market_list, dt_start_date, dt_end_date)
    df_selection_product = filter_df(df_product, market_list, dt_start_date, dt_end_date)

    return [{'label': i, 'value': i} for i in df_selection_vendor.market.unique().tolist()], \
           [{'label': i, 'value': i} for i in df_selection_product.market.unique().tolist()]


# Filter vendor market and dates -> vendor name dropdown
@app.callback(
    Output("vendor_search", "options"),
    [
        Input("dp_export_date_tab3", "start_date"),
        Input("dp_export_date_tab3", "end_date"),
        Input("market_search_vendor", "value"),
    ],
)
def update_vendor_dropdown(start_date, end_date, market_list):
    """
    Updates the vendor dropdown menu for the vendor tab
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :return: list of dicts containing options for the vendor dropdown menu
    """
    dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df_selection_vendor = filter_df(df_vendor, [market_list], dt_start_date, dt_end_date)

    return [{'label': i, 'value': i} for i in df_selection_vendor.name.unique().tolist()]


# Filters vendor market, dates, vendor selection -> dump selection options & last dump
@app.callback(
    [Output("dump_vendor", "options"),
     Output("dump_vendor", "value")],
    [
        Input("vendor_search", "value"), ],
    [
        State("dp_export_date_tab3", "start_date"),
        State("dp_export_date_tab3", "end_date"),
        State("market_search_vendor", "value"),
    ],
)
def update_date_dropdown_vendor(vendor, start_date, end_date, market_list):
    """
    Retrieves the dump dates and returns them as options for the dropdown, and also returns the max dump date
    and automatically selects this value as default.
    :param vendor:
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :return: list of dicts with options to select from
    :return: max dump date in data
    """
    if vendor == 'non selected':
        return [], None

    dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df_selection_vendor = filter_df(df_vendor, [market_list], dt_start_date, dt_end_date)
    df_selection_vendor = df_selection_vendor[df_selection_vendor['name'] == vendor]

    return [{'label': datetime.fromtimestamp(i).date(), 'value': i} for i in
            df_selection_vendor.extraction_date.unique().tolist()], df_selection_vendor.extraction_date.unique().max()


# filter selections -> more information on the vendor
@app.callback(
    Output("vendor_information", "children"),
    [
        Input("dump_vendor", "value"),
        Input("vendor_search", "value"),
    ],
    [
        State("dp_export_date_tab3", "start_date"),
        State("dp_export_date_tab3", "end_date"),
        State("market_search_vendor", "value"),
    ],
)
def update_vendor_info_div(dump, vendor, start_date, end_date, market_list):
    """
    Creates and returns a DIV containing more information about selected vendor for a specific dump date
    :param dump: str, date of the selected dump
    :param vendor: str, name of the selected vendor
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :return: html.Div with information about the vendor
    """

    # If none selected
    if market_list == 'non selected' or vendor == 'non selected':
        html_info = html.Div([
            html.H6('Please select a vendor above')
        ])

    # If vendor selected
    else:

        dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        df_selection = filter_df(df_vendor, [market_list], dt_start_date, dt_end_date)
        df_selection_recent = \
            df_selection[(df_selection['extraction_date'] == dump) & (df_selection['name'] == vendor)].iloc[0]

        # Try to receive available information
        try:
            score = check_value(df_selection_recent['score_normalized'])
        except ValueError:
            score = 'Not available'
        try:
            vendor_since = datetime.fromtimestamp(df_selection_recent['registration_date']).date()
        except ValueError:
            vendor_since = 'Not available'
        try:
            vendor_since_deviation = check_value(df_selection_recent['registration_date_deviation'])
        except ValueError:
            vendor_since_deviation = 'Not available'
        try:
            last_login = datetime.fromtimestamp(df_selection_recent['last_login']).date()
        except ValueError:
            last_login = 'Not available'
        try:
            last_login_deviation = check_value(df_selection_recent['last_login_deviation'])
        except ValueError:
            last_login_deviation = 'Not available'
        try:
            sales = check_value(df_selection_recent['sales'])
        except ValueError:
            sales = 'Not available'
        try:
            info = check_value(df_selection_recent['info'])
        except ValueError:
            info = 'Not available'
        try:
            pgp = check_value(df_selection_recent['pgp'])
        except ValueError:
            pgp = 'Not available'

        # The Div to return
        html_info = html.Div([
            html.H6(f'Textual information about vendor: {vendor}'),
            html.B(f'Dump of {datetime.fromtimestamp(dump).date()} used'),
            html.Br(),
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Markdown(
                            f"**Most recent dump of data** : {datetime.fromtimestamp(df_selection['extraction_date'].max()).date()}"),
                        dcc.Markdown(f"**Score (between 0 and 1)** : {score} "),
                        dcc.Markdown(
                            f"**Vendor since (around)**: {vendor_since} (*Precision: {vendor_since_deviation})*"),
                        dcc.Markdown(
                            f"**Vendor last login (around)** : {last_login} (*Precision: {last_login_deviation})*"),
                        dcc.Markdown(f"**Sales by vendor** : {sales} "),
                        html.B('PGP:'),
                        html.Div([
                            html.P(pgp)
                        ],
                            style={'word-break': 'break-all',
                                   "overflow-y": "scroll",
                                   "height": "200px",
                                   }),

                    ],
                        className="pretty_container six columns", ),

                    html.Div([
                        html.B('Info on page:'),
                        html.Div([
                            html.P(info)
                        ],
                            style={'word-break': 'break-all',
                                   "overflow-y": "scroll",
                                   "height": "400px"}),
                    ],
                        className="pretty_container six columns", ),
                ],
                    className="row flex-display",
                ),
                html.Hr(),
            ],
            ),
        ])
    return html_info

# filters -> trend plot for vendor
@app.callback(
    Output("vendor_trend", "children"),
    [
        Input("vendor_search", "value"),
        Input("vendor_feature", "value"),
    ],
    [
        State("dp_export_date_tab3", "start_date"),
        State("dp_export_date_tab3", "end_date"),
        State("market_search_vendor", "value"),
    ],
)
def create_vendor_trend_plot(vendor, feature, start_date, end_date, market_list):
    """
    Creates and returns vendor trend plot for given feature, using trend_plot() function in module plots
    :param vendor: str, name of the vendor selected
    :param feature: str, the feature selected
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :return: html.Div with the trend graph
    """
    if market_list == 'non selected' or vendor == 'non selected':
        html_info = html.Div([
        ])

    elif feature in ['non selected', [], None]:
        html_info = html.Div([
            html.B('select a feature')
        ])

    else:
        dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        df_selection = filter_df(df_vendor, [market_list], dt_start_date, dt_end_date)
        df_selection = df_selection[df_selection['name'] == vendor]

        if feature == 'score':
            feature = 'score_normalized'
        html_info = dcc.Graph(
            id='trend_id',
            figure=plots.trend_plot(df_selection,  feature, vendor, market_list)),

    return html_info

# vendor_search -> show block feature selection
@app.callback(
    Output("show_vendor_feature", "style"),
    [
        Input("vendor_search", "value"),
    ],
)
def show_feature_selection_vendor(value):
    """
    Determines whether the dropdown menu should be visible
    :param value: str, vendor name
    :return: style for div to show ('block') or not
    """
    if value != 'non selected':
        return {'display': 'block'}
    else:
        return {'display': 'None'}


# filters -> vendor (product sub page) dropdown menu options
@app.callback(
    Output("vendor_search_product", "options"),
    [
        Input("dp_export_date_tab3", "start_date"),
        Input("dp_export_date_tab3", "end_date"),
        Input("market_search_product", "value"),
    ],
)
def update_vendor_dropdown_product(start_date, end_date, market_list):
    """
    returns the options for vendors to select from based on given parameters
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :return: list of dicts with vendors to filter on
    """
    dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df_selection_product = filter_df(df_product, [market_list], dt_start_date, dt_end_date)

    return [{'label': 'all vendors', 'value': 'all'}] + [{'label': i, 'value': i} for i in
                                                         df_selection_product.vendor.unique().tolist()]

# filters and dropdown -> options vendor dropdown
@app.callback(
    Output("product_search", "options"),
    [
        Input("dp_export_date_tab3", "start_date"),
        Input("dp_export_date_tab3", "end_date"),
        Input("market_search_product", "value"),
        Input("vendor_search_product", "value"),
    ],
)
def update_vendor_dropdown(start_date, end_date, market_list, vendor):
    """
    Provides all the options of vendors to select from in dropdown
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market_list: list of strings of market names
    :param vendor: name of the vendor selected
    :return: list of dicts containing the vendors to select from in drop down
    """
    dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df_selection_product = filter_df(df_product, [market_list], dt_start_date, dt_end_date)

    if vendor != 'all':
        df_selection_product = df_selection_product[df_selection_product['vendor'] == vendor]

    return [{'label': i, 'value': i} for i in df_selection_product.name.unique().tolist()]

# market, vendor, product selections -> options dump date dropdown
@app.callback(
    [Output("dump_product", "options"),
     Output("dump_product", "value")

     ],
    [
        Input("product_search", "value"),
    ],
    [State("dp_export_date_tab3", "start_date"),
     State("dp_export_date_tab3", "end_date"),
     State("market_search_product", "value"), ]
)
def update_product_dump_dropdown(product, start_date, end_date, market):
    """
    Updates the options for the dump dropdown, and the max value to be automatically selected
    :param product: str, name of the product selected
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market: str selected market name
    :return: options for the dump dropdown and the max value for the dropdown
    """
    if product == 'non selected':
        return [], None
    dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df_selection_product = filter_df(df_product, [market], dt_start_date, dt_end_date)
    df_selection_product = df_selection_product[df_selection_product['name'] == product]

    return [{'label': datetime.fromtimestamp(i).date(), 'value': i} for i in
            df_selection_product.extraction_date.unique().tolist()], df_selection_product.extraction_date.unique().max()


# product & vendor selection -> update product div more information
@app.callback(
    Output("product_information", "children"),
    [
        Input("product_search", "value"),
        Input("dump_product", "value"),
    ],
    [
        State("dp_export_date_tab3", "start_date"),
        State("dp_export_date_tab3", "end_date"),
        State("market_search_product", "value"),
    ],
)
def update_product_div(product, dump, start_date, end_date, market):
    """

    :param product: str, name of the product
    :param dump: str (yyyy-mm-dd) date of the dump
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market: str selected market name
    :return:
    """

    if market == 'non selected' or product == 'non selected':
        html_info = html.Div([
            html.H6('Please select a product above')
        ])

    else:
        dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        df_selection = filter_df(df_product, [market], dt_start_date, dt_end_date)
        df_selection_recent = df_selection[df_selection['extraction_date'] == dump]
        df_selection_recent = df_selection_recent[df_selection['name'] == product].iloc[0]

        # Try to retrieve all information
        try:
            vendor = check_value(df_selection_recent['vendor'])
        except ValueError:
            vendor = 'Not available'
        try:
            ships_from = check_value(df_selection_recent['ships_from'])
        except ValueError:
            ships_from = 'Not available'
        try:
            ships_to = check_value(df_selection_recent['ships_to'])
        except ValueError:
            ships_to = 'Not available'
        try:
            price = check_value(df_selection_recent['price'])
        except ValueError:
            price = 'Not available'
        try:
            price_eur = check_value(df_selection_recent['price_eur'])
        except ValueError:
            price_eur = 'Not available'
        try:
            info = check_value(df_selection_recent['info'])
        except ValueError:
            info = 'Not available'
        try:
            macro_category = check_value(df_selection_recent['macro_category'])
        except ValueError:
            macro_category = 'Not available'
        try:
            micro_category = check_value(df_selection_recent['micro_category'])
        except ValueError:
            micro_category = 'Not available'

        html_info = html.Div([
            html.H6(f'Textual information about product: \"{product}\"'),
            html.B(f'Dump of {datetime.fromtimestamp(dump).date()} used'),
            html.Br(),

            html.Div([
                html.Div([

                    dcc.Markdown(f"**Market** : {market}"),
                    dcc.Markdown(
                        f"**Most recent dump of data** : {datetime.fromtimestamp(df_selection['extraction_date'].max()).date()}"),
                    dcc.Markdown(f"**Vendor** : {vendor}"),
                    dcc.Markdown(f"**Ships from** : {ships_from}"),
                    dcc.Markdown(f"**Ships to** : {ships_to}"),
                    dcc.Markdown(f"**Price** : {price} *(as stated on page)*"),
                    dcc.Markdown(
                        f"**Price in euros** : {price_eur} *(converted)*"),
                    dcc.Markdown(f"**Macro category** : {macro_category}"),
                    dcc.Markdown(f"**Micro category** : {micro_category}"),
                ],
                    className="pretty_container six columns", ),

                html.Div([
                    html.B('Info on page:'),
                    html.Div([
                        html.P(f"{info}")
                    ],
                        style={'word-break': 'break-all',
                               "overflow-y": "scroll",
                               "height": "400px"}),
                ],
                    className="pretty_container six columns", ),
            ],
                className="row flex-display",
            ),
            html.Hr(),

        ])
    return html_info

# select product -> show vendor selection block
@app.callback(
    Output("show_product_feature", "style"),
    [
        Input("product_search", "value"),
    ],
)
def show_feature_selection(value):
    """
    If no vendor is selected, don't show the block
    :param value: str, the selected vendor
    :return: style for product selection block
    """
    if value != 'non selected':
        return {'display': 'block'}
    else:
        return {'display': 'None'}

# product selection -> trend plot
@app.callback(
    Output("product_trend", "children"),
    [
        Input("product_search", "value"),
    ],
    [
        State("dp_export_date_tab3", "start_date"),
        State("dp_export_date_tab3", "end_date"),
        State("market_search_product", "value"),
    ],
)
def update_vendor_graph(product, start_date, end_date, market):
    """
    Uses the parameters to return a trend plot using the trend_plot function from the plots module
    :param product: str, name of the product
    :param start_date: str (yyyy-mm-dd), start date in the datepicker
    :param end_date: str (yyyy-mm-dd), end date in the datepicker
    :param market: str selected market name
    :return: dcc.Graph() with the trend plot
    """
    if market == 'non selected' or product == 'non selected':
        html_info = html.Div([
        ])

    else:
        dt_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        dt_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        df_selection = filter_df(df_product, [market], dt_start_date, dt_end_date)
        df_selection = df_selection[df_selection['name'] == product]
        html_info = dcc.Graph(
            id='trend_id',
            figure=plots.trend_plot(df_selection, 'price_eur', product, market)),

    return html_info


# Main
if __name__ == "__main__":
    app.run_server(debug=False) # Can be made true to view errors and callback graph
