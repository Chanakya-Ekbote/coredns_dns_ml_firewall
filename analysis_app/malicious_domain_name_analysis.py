import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
from dash.dependencies import Input, Output, State
import copy
from elasticsearch import Elasticsearch
import plotly.express as px
import plotly.graph_objects as go

es = Elasticsearch()

app = dash.Dash(__name__)

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=0, r=0, b=6, t=30),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    # width=350,
    # height=170,
    legend=dict(font=dict(size=10), orientation="v"),
    mapbox=dict(style="light",
                # center=dict(lon=-78.05, lat=42.54),
                zoom=2,
                ),
)

app.layout = html.Div(children=[
    html.H1(children='Malicious Domain Name Analysis',
            style={
                'textAlign': 'center',
                'color': '#2e86c1'
            }),
    html.Div(
        [
            html.Div(
                [
                    html.Div([
                        html.Div([
                            html.P(
                                "Domain Name:",
                                style={'display': 'inline', 'color': '#2e86c1', 'font-size': '18px'},
                                className="control_label"
                            ),
                            dcc.Input(
                                placeholder='Enter a Domain Name',
                                type='text',
                                id='input_text',
                                className='dcc_control'
                            ),
                        ]),
                        html.Div(id='input_message', className="control_label"),
                        html.P("Enter the date range for the analysis:",
                               style={'color': '#2e86c1', 'font-size': '18px', 'border': '0px'},
                               className="control_label"),
                        dcc.DatePickerRange(
                            id='date_range',
                            min_date_allowed=dt(2020, 1, 5),
                            className="dcc_control",
                            style={'borderWidth': '0px'},
                        ),
                        html.Div(id='date_message', className="control_label", style={'margin-bottom': '10px'}),
                        html.Div([
                            html.Div([
                                html.P("Requests per:",
                                       style={'display': 'inline', 'color': '#2e86c1', 'font-size': '18px'},
                                       className="control_label", ),
                                dcc.RadioItems(
                                    id="requests_freq",
                                    options=[
                                        {"label": "Day ", "value": "Day"},
                                        {"label": "Hour ", "value": "Hour"},
                                        {"label": "Minute ", "value": "Minute"},
                                    ],
                                    labelStyle={"display": "inline-block"},
                                    style={'color': '#2e86c1'},
                                    className="dcc_control",
                                ),
                            ]),
                            html.Div(id='radio_button_message', className="control_label",
                                     style={'margin-bottom': '10px'}),
                            html.Div([
                                html.P(
                                    "Hour Range:",
                                    style={'display': 'inline', 'color': '#2e86c1', 'font-size': '18px'},
                                    className="control_label"
                                ),
                                dcc.Input(
                                    placeholder='',
                                    type='text',
                                    id='start_hour',
                                    className='dcc_control',
                                    size='1'
                                ),
                                html.P(
                                    "to",
                                    style={'display': 'inline', 'color': '#2e86c1', 'font-size': '18px'},
                                    className="control_label"
                                ),
                                dcc.Input(
                                    placeholder='',
                                    type='text',
                                    id='end_hour',
                                    className='dcc_control',
                                    size='1'
                                ),

                            ], id='hour_range'),
                            html.Div(id='hour_range_message', className="control_label", style={'margin-bottom': '10px'}),
                            html.Div([html.P("Submit the Queries:",
                                             style={'display': 'inline', 'color': '#2e86c1', 'font-size': '18px'},
                                             className="control_label", ),
                                      html.Button('Submit',
                                                  id='submit_input',
                                                  n_clicks=0,
                                                  style={'float': 'center', 'margin-left': '30px',
                                                         'color': '#2e86c1'}, ),
                                      ], ),
                        ]),
                    ], className='pretty_container'),

                    html.Div([
                        dcc.Graph(id='pie_graph')
                    ], className="pretty_container",
                        # style={'max-height': '50px'}
                    )
                ],
                className="four columns",
                id="pie",
            ),
            html.Div([
                dcc.Tabs(id='tabs-example', value='tab-1', children=[
                    dcc.Tab([html.Div([dcc.Graph(id='freq_graph', )]), ], label='Requests Plot', value='tab-1',
                            className='pretty_container'),
                    dcc.Tab([], label='Queries per IP Address', value='tab-3', className='pretty_container'),
                    dcc.Tab([], label='Top malicious domains queried', value='tab-2', className='pretty_container'),

                ]),

            ], className="pretty_container eight columns", style={'color': '#2e86c1', 'font-size': '16px'}),

        ],
        className="row flex-display",
    ),

])


# Control Messages


@app.callback(Output('input_message', 'children'),
              [Input('submit_input', 'n_clicks')],
              [State('input_text', 'value')])
def input_message(n_clicks, value):
    if value is None or value == '':
        return 'Please enter a Domain Name'
    else:
        return 'You have entered: ' + value


@app.callback(Output('date_message', 'children'),
              [Input('submit_input', 'n_clicks'),
               Input('requests_freq', 'value'),
               Input('date_range', 'start_date'),
               Input('date_range', 'end_date')])
def date_message(n_clicks, freq, start_date, end_date):
    if start_date is None or end_date is None:
        return 'Please enter the date range'
    elif freq == 'Hour' or freq == 'Minute':
        start = int(start_date.split('-')[2])
        end = int(start_date.split('-')[2])
        if (end - start) == 1:
            return 'Data from {} to {}'.format(start_date, end_date)
        else:
            return 'For hours or minutes please two consecutive days'

    else:
        print(type(start_date))
        print(start_date)
        return 'Data from {} to {}'.format(start_date, end_date)


@app.callback(Output('radio_button_message', 'children'),
              [Input('submit_input', 'n_clicks'),
               Input('requests_freq', 'value')])
def radio_button_message(n_clicks, value):
    if value is None:
        return 'Please select an option'
    else:
        return 'You have selected: ' + value


@app.callback(Output('hour_range_message', 'children'),
              [Input('requests_freq', 'value'),
               Input('start_hour', 'value'),
               Input('end_hour', 'value')])
def hour_range_message(freq, start, end):
    if freq is None or freq == 'Day':
        return html.Div([])
    elif start is None or start is '' or end is None or end is '':
        return 'Enter an integer hour range (0 to 24)'
    else:
        try:
            start_ = int(start)
            end_ = int(end)
            diff = end_ - start_
            if 0 <= start_ <= 24 and 0 <= end_ <= 24 and diff > 0:
                if freq == 'Minute':
                    if diff > 1:
                        return 'The difference between the ranges should be 1'
                    else:
                        return 'Hour range from {} to {}'.format(start_, end_)
                else:
                    return 'Hour range from {} to {}'.format(start_, end_)
            else:
                return 'Please enter relevant integer values (0 to 24) '
        except:
            return 'Please enter integer values (0 to 24)'


# Graphs and Div Updates


@app.callback(Output('hour_range', 'style'),
              [Input('requests_freq', 'value')])
def display_hour_range(value):
    if value is None or value == 'Day':
        return {'display': 'none'}
    else:
        return {'display': 'unset'}


@app.callback(Output('pie_graph', 'figure'),
              [Input('submit_input', 'n_clicks')],
              [State('input_text', 'value')])
def update_pie_graph(n_clicks, value):
    layout_pie = copy.deepcopy(layout)
    layout_pie["title"] = 'Prediction'
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(font=dict(color="#777777", size="10"), orientation="v", bgcolor="rgba(0,0,0,0)")
    layout_pie["width"] = '350'
    layout_pie["height"] = '150'
    if value is None or value is '':
        data = [
            dict(
                type="pie",
                labels=["Benign", "Malicious"],
                values=[0.5, 0.5],
                textinfo="label+percent+name",
                hole=0.5,
                marker=dict(colors=["#3498db", "#f5b041 ", "#f39c12", "#92d8d8"]),
                domain={"x": [0.2, 0.9], "y": [0.2, 0.9]},
            )]
        figure = dict(data=data, layout=layout_pie)
        return figure
    else:
        pred = float(es.get(index=value, id=1)['_source']['status'])
        data = [
            dict(
                type="pie",
                labels=["Benign", "Malicious"],
                values=[1-pred, pred],
                textinfo="label+percent+name",
                hole=0.5,
                marker=dict(colors=["#3498db", "#f5b041 "]),
                domain={"x": [0.2, 0.9], "y": [0.2, 0.9]},
            )]
        figure = dict(data=data, layout=layout_pie)
        return figure


@app.callback(Output('freq_graph', 'figure'),
              [Input('submit_input', 'n_clicks')],
              [State('input_text', 'value'),
               State('date_range', 'start_date'),
               State('date_range', 'end_date'),
               State('requests_freq', 'value')])
def update_input(n_clicks, input_value, start_date, end_date, freq_value):
    layout_count = copy.deepcopy(layout)
    layout_count['title'] = "Requests"
    layout_count['xaxis'] = {'title': 'Requests per'}
    layout_count['yaxis'] = {'title': 'Number of Requests'}
    layout_count['autosize'] = True
    layout_count['margin'] = dict(l=0, r=0, b=20, t=30),
    if input_value is None or input_value == '' or start_date is None or end_date is None or freq_value is None:
        data = [
            dict(
                type="line",
                # mode="markers",
                x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                y=[2, 5, 6, 10, 23, 23, 2, 1, 3, 2],
                # opacity=0,
                hoverinfo="skip",
            )]
        figure = dict(data=data, layout=layout_count)
        return figure


if __name__ == '__main__':
    app.run_server(debug=True)
