"""
plots.py
This module is part of the visualisation tool of ANITA

This module contains all the functions for the plots except the network graph
"""

# ----- IMPORTS
import plotly.graph_objs as go
import pandas as pd
import json


# ----- HELPER FUNCTION
def check_exists(element, collection):
    """
    Simple function to check whether an element in collection
    :param element: a value to check in collection
    :param collection: collection is a set of list of elements
    :return: boolean, True if the element can be found in the collection
    """
    return element in collection


# ----- PLOT FUNCTIONS
def unique_bar_plot(x_values, y_values, text_values):
    """
    Creates the unique bar plots given the parameters
    :param x_values: list, values for x axis
    :param y_values: list, values for y axis
    :param text_values: list, values for hover function
    :return: go.Figure(), the plot
    """

    # Create the layout
    layout = dict(barmode='group',
                  plot_bgcolor="#F9F9F9",
                  paper_bgcolor="#F9F9F9",
                  title='Number of unique vendors per market in data',
                  xaxis={'title': 'Darknet markets'},
                  yaxis={'title': 'Number of unique vendors'},
                  autosize=True,
                  width=1050,
                  height=600, )

    # Create the data
    data = [go.Bar(x=x_values,
                   y=y_values,
                   text=text_values,
                   hovertemplate="<b>%{x}</b><br>" +
                                 "Unique vendors: %{y:.0f}<br>" +
                                 "Unique dump dates: %{text}<br>" +
                                 "<extra></extra>",
                   )]
    return go.Figure(data=data, layout=layout)


def trend_plot(df_selection, feature, name, market):
    df_selection['extraction_date'] = pd.to_datetime(df_selection['extraction_date'], unit='s')

    x = df_selection.sort_values('extraction_date', ascending=False)['extraction_date'].tolist()
    y = df_selection.sort_values('extraction_date', ascending=False)[feature].tolist()

    if feature == 'score_normalized':
        data = dict(x=x,
                    y=y,
                    text=df_selection.sort_values('extraction_date', ascending=False)['score'].tolist(),
                    hovertemplate="<b>%{x} </b><br>" +
                                  "Normalized score %{y}<br>" +
                                  "Score on market site %{text}<extra></extra>"
                    )
    if feature == 'sales':
        data = dict(x=x,
                    y=y,
                    text=df_selection.sort_values('extraction_date', ascending=False)['score'].tolist(),
                    hovertemplate="<b>%{x} </b><br>" +
                                  "Sales %{y}<br>" +
                                  "<extra></extra>"
                    )

    if feature == 'price_eur':
        text_y = df_selection.sort_values('extraction_date', ascending=False)['price'].tolist()

        if len(y[0]) > 20:
            values = {}
            json_dict = []
            for price in y:
                json_acceptable_string = price.replace("'", "\"")
                d = json.loads(json_acceptable_string)
                json_dict.append(d)
            for key in json_dict[0]:
                values[key] = 0
                for collection in json_dict[1:]:
                    if check_exists(key, collection):
                        values[key] += 1

            key_to_use = max(values, key=values.get)
            y = []
            for collection in json_dict:
                y.append(collection[key_to_use])

            text_y = ['This market provides different prices per grams / items, check above'] * len(y)

        data = dict(x=x,
                    y=y,
                    text=text_y,
                    hovertemplate="<b>%{x} </b><br>" +
                                  "Price %{y}<br>" +
                                  "Price on website: %{text}<br>" +
                                  "<extra></extra>"
                    )

    # Edit the layout
    layout = dict(title=f'Trend of {feature}',
                  xaxis_title='Time',
                  yaxis_title='Normalized score',
                  plot_bgcolor="#F9F9F9",
                  paper_bgcolor="#F9F9F9",
                  )

    if len(y) in [0, 1]:
        data = dict()
        layout = {
            'plot_bgcolor': "#F9F9F9",
            'paper_bgcolor': "#F9F9F9",
            "xaxis": {
                "visible": False
            },
            "yaxis": {
                "visible": False
            },
            "annotations": [
                {
                    "text": f"There is not enough data to show a trend for \"{name}\"",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 18
                    }
                }
            ]
        }

    if len(y) > 1:
        if (y[0] == None) and (y[1] == None):
            data = dict()
            layout = {
                'plot_bgcolor': "#F9F9F9",
                'paper_bgcolor': "#F9F9F9",
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": f" {market} does not collect data about {feature}",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }

    return go.Figure(data=data, layout=layout)
