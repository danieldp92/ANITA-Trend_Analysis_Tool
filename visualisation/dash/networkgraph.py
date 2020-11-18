"""
networkgraph.py
This module is part of the visualisation tool of ANITA

This module contains all the functions for the creation of the network graph
"""


##### NETWORK GRAPH
import networkx as nx
import plotly.graph_objs as go

# Specific colors used for the different nodes
# This colors are also used for reversed finding of vendor-product combinations
node_colors = {
    'product': 'red',
    'vendor': 'blue',
    'market': 'green',
    'pgp': 'orange',
}


def get_nodes_and_edges(df_vendor, df_product, name_pgp, value, products=False):
    """
    Based on parameters and using networkx (nx) package it finds and returns the edges and nodes.
    :param df_vendor: df, df of vendor used in app.py
    :param df_product: df, df, of product used in app.py
    :param name_pgp: str, value of ratio item choosing between 'Name' and 'PGP'
    :param value: value: str, name or pgp selected in dropdown
    :param products: boolean, True is products should be included
    :return: list of nodes
    :return: list of edges
    """

    # Find the duplicate values in the df
    global df_product_selection
    if name_pgp == 'Name':
        # Create DF based on same name
        df_selection = df_vendor[df_vendor['name'] == value]
        # Add vendors with same pgp
        for pgp in df_selection.pgp.tolist():
            if pgp is not None:
                df_pgp = df_vendor[df_vendor['pgp'] == pgp]
                if len(df_pgp) > 0:
                    df_selection = df_selection.append(df_pgp).drop_duplicates(subset=['name', 'market', 'pgp'],
                                                                               keep="first")

    if name_pgp == 'PGP':
        # Create DF based on same PGP
        df_selection = df_vendor[df_vendor['pgp'] == value]
        # Add vendors with same name
        for name in df_selection.name.tolist():
            if name is not None:
                df_name = df_vendor[df_vendor['name'] == name]
                if len(df_name) > 0:
                    df_selection = df_selection.append(df_name).drop_duplicates(subset=['name', 'market', 'pgp'],
                                                                                keep="first")

    # CREATE NODES
    # Name nodes
    node_name = [(name, 'vendor') for name in df_selection.name.unique()]
    # Market nodes
    node_market = [(market, 'market') for market in df_selection.market.unique()]
    # Pgp nodes
    node_pgp = [(pgp, 'pgp') for pgp in df_selection.pgp.unique()]

    # CREATE EDGES
    edges = {}

    tuples = list({tuple(x) for x in df_selection[['name', 'market', 'pgp']].to_numpy()})
    tuples_new = []
    for index, item in enumerate(tuples):
        tuples_new.append(((item[0], 'vendor'), (item[1], 'market'), (item[2], 'pgp')))

    # connect nodes
    temporary_pgp_edges = []
    temporary_name_edges = []

    for item in tuples_new:
        # Connect vendor_name to market
        if item[0] not in edges:
            edges[item[0]] = [item[1]]
        else:
            if edges[item[0]] != [item[1]]:
                edges[item[0]] = edges[item[0]] + [item[1]]

        # Add pgp and name nodes ot temporary lists to check whether nodes for this should be made
        if item[2][0] is not None:
            temporary_pgp_edges.append(item[2])
            temporary_name_edges.append(item[0])

    # Add pgp to edges
    for index, pgp in enumerate(temporary_pgp_edges):
        if temporary_pgp_edges.count(pgp) > 1:
            if pgp not in edges:
                edges[pgp] = [temporary_name_edges[index]]
            else:
                if edges[pgp] != [temporary_name_edges[index]]:
                    edges[pgp] = edges[pgp] + [temporary_name_edges[index]]

    # Connect market nodes to products
    if products is True:
        for vendor_name in node_name:
            df_product_selection = df_product[df_product['vendor'] == vendor_name[0]].drop_duplicates(
                subset='product_id', keep="first")

        product_edge = dict
        for market in node_market:
            edges[market] = [(product, 'product') for product in
                             set(df_product_selection[df_product_selection['market'] == market[0]]['name'].tolist())]

    # Get all the nodes from the edges
    nodes = []
    for key in edges:
        nodes.append(key)
        for name in edges[key]:
            nodes.append(name)
    nodes = list(set(nodes))
    return nodes, edges


def make_edge(x, y):
    """
    # Custom function to create an edge between node x and node y, with a given text and width
    :param x: x coordinates
    :param y: y coordinates
    :return: go.Scatter(), the line between edges
    """
    return go.Scatter(x=x,
                      y=y,
                      line=dict(width=1,
                                color='grey'),
                      mode='lines')

def create_network_graph(nodes, edges, colordict = node_colors):
    """
    Create and return the network graph
    :param nodes: list of nodes
    :param edges:  list of edges
    :param colordict: dict of colors to use for the nodes
    :return: go.Figure(), the network graph
    """
    # Determine color and size in network graph
    color_dict = {}
    size_dict = {}
    for item in nodes:
        if item[1] == 'product':
            color_dict[item[0]] = colordict['product']  # red'
            size_dict[item[0]] = 5
        if item[1] == 'vendor':
            color_dict[item[0]] = colordict['vendor']  # 'blue'
            size_dict[item[0]] = 20
        if item[1] == 'market':
            color_dict[item[0]] = colordict['market']  # 'green'
            size_dict[item[0]] = 15
        if item[1] == 'pgp':
            color_dict[item[0]] = colordict['pgp']  # 'orange'
            size_dict[item[0]] = 15

    # Create network
    network = nx.Graph()

    # Add to the network graph
    for node in nodes:
        network.add_node(node[0], size=5)  # 5 is a placeholder

    # Add edges to the network graph
    for node1 in edges:
        for node2 in edges[node1]:
            network.add_edge(node1[0], node2[0],
                             type=node2[1])

    # Get positions for the nodes in the network
    pos_ = nx.kamada_kawai_layout(network)

    # For each edge, make an edge_trace, append to list
    edge_trace = []
    for edge in network.edges():
        char_1 = edge[0]
        char_2 = edge[1]
        x0, y0 = pos_[char_1]
        x1, y1 = pos_[char_2]
        trace = make_edge([x0, x1, None], [y0, y1, None])
        edge_trace.append(trace)

    # Make a (empty) node trace
    node_trace = go.Scatter(x=[],
                            y=[],
                            text=[],
                            textposition="top center",
                            textfont_size=10,
                            mode='markers',
                            hoverinfo='text',
                            marker=dict(color=[],
                                        size=[],
                                        line=None))

    # For each node in the network, get the position and size and add to the node_trace
    for node in network.nodes():
        x, y = pos_[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['marker']['color'] += tuple([color_dict[node]])
        node_trace['marker']['size'] += tuple([size_dict[node]])
        #     node_trace['text'] will be determined when dealing with annotations

    # Creating the annotations, that will display the node name on the figure
    annotations = []

    # hover text and color group
    for node, adjacencies in enumerate(network.adjacency()):

        # setting the text that will be display on hover, thus shorter names
        node_info = '{} '.format(
            adjacencies[0],
        )

        # For the pgp, don't show the full PGP
        if len(node_info) > 100:
            node_trace['text'] += tuple(['Same PGP'])
        else:
            node_trace['text'] += tuple([node_info])

        if len(adjacencies[0]) < 20:
            notation_text = adjacencies[0]
        if len(adjacencies[0]) > 100:
            notation_text = 'Same PGP'
        else:
            notation_text = adjacencies[0][0:12] + '...'

        # Annotations is a list of dictionaries with every needed parameter for each node annotation
        annotations.append(
            dict(x=pos_[adjacencies[0]][0],
                 y=pos_[adjacencies[0]][1],
                 text=notation_text,  # node name that will be displayed
                 xanchor='left',
                 xshift=2,
                 yshift=10,
                 font=dict(color='black', size=12),
                 showarrow=False, arrowhead=1, ax=-20, ay=-10)
        )

    # Customize layout
    layout = go.Layout(
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        xaxis={'showgrid': False, 'zeroline': False},  # no gridlines
        yaxis={'showgrid': False, 'zeroline': False},  # no gridlines
        title='Network graph of the vendor',
    )

    # Create figure
    fig = go.Figure(layout=layout)
    # Add all edge traces
    for trace in edge_trace:
        fig.add_trace(trace)
    # Add node trace
    fig.add_trace(node_trace)
    # Remove legend
    fig.update_layout(showlegend=False)
    # Add annotations
    fig.update_layout(annotations=annotations)
    # Remove tick labels
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return fig
