import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from get import *
from shared import *
from process import *

def make_dash_compatible_dicts(d):
    """Converts dict d to list of dicts in dash compatible format:
    {"value": <key>, "label": <val>}
    Arguments:
        d {dict} -- dict to convert

    Returns:
        {list} -- list of dash compatible dicts
    """
    return [{"value":key, "label":val} for key,val in d.items()]

def get_2020_datetimes():
    """Generator of datetime objects from Jan 1 2020 
    up to current date.

    Yields:
        date {datetime} -- datetime object for a given date
    """
    date = datetime(year=2020,month=1,day=1)
    today = datetime.today()
    while date <= today:
        yield date
        date += timedelta(days=1)

OPTIONS = {key : make_dash_compatible_dicts(d) for key, d in PLOTABLE_VARS.items()}

TRACE_TYPES = make_dash_compatible_dicts({
    "candlestick" : "Candlestick",
    "scatter" : "Line"
})

CATEGORIES = make_dash_compatible_dicts({
     "crypto" : "Cryptocurrency",
    "stock" : "Stock",
    "covid": "COVID-19 Statistics"
})
DATERANGE = [{"label" : dt.strftime("%m/%d/%Y"), "value" : dt.timestamp()} for dt in get_2020_datetimes()]

# Launch Dash Applicationa and define initial layout for the webpage
app = dash.Dash()
app.layout = html.Div([
    html.Div([
        html.H2("SI 206 Final Project - Visualize"),
        html.P("By Lucas Faudman")
    ],
        style={
        'backgroundColor': '#3aaab2'}),
    html.Div([
        html.P([
            html.B("Category (Left):"),
            dcc.RadioItems(id="left_category",
                           options=CATEGORIES,
                           value=CATEGORIES[1]["value"],
                           style={"display": "flex",
                                  "flex-wrap": "wrap",
                                  "justify-content": "flex-start"}
                           ),
            html.B("Selection (Left):"),
            dcc.Dropdown(id='left_dropdown', options=OPTIONS["stock"], multi=False, clearable=False,
                         value=OPTIONS["stock"][0]["value"]),
            html.B("Chart Type (Left):"),
            dcc.RadioItems(id="left_trace_type",
                           options=TRACE_TYPES,
                           value=TRACE_TYPES[0]["value"],
                           )

        ], style={'width': '400px'}),

        html.P([
            html.B("Category (Right):"),
            dcc.RadioItems(id="right_category",
                           options=CATEGORIES,
                           value=CATEGORIES[2]["value"],
                           style={"display": "flex",
                                  "flex-wrap": "wrap",
                                  "justify-content": "flex-start"}
                           ),
            html.B("Selection (Right):"),
            dcc.Dropdown(id='right_dropdown', options=OPTIONS["covid"], multi=False, clearable=False,
                         value=OPTIONS["covid"][0]["value"]),
            html.B("Chart Type (Right):"),
            dcc.RadioItems(id="right_trace_type",
                           options=TRACE_TYPES,
                           value=TRACE_TYPES[1]["value"],
                           )

        ], style={'width': '400px'}),

        html.P([
            html.B("Begin Date:"),
            dcc.Dropdown(id='begin_date', options=DATERANGE, multi=False, clearable=False,
                         value=DATERANGE[0]["value"]),
            html.B("End Date:"),
            dcc.Dropdown(id='end_date', options=DATERANGE, multi=False, clearable=False,
                         value=DATERANGE[-1]["value"]),    

        ], style={'width': '400px'}),
    ],
        style={
        'fontSize': '20px',
        'padding-left': '50px',
        "display": "flex",
        "flex-wrap": "wrap",
        "justify-content": "space-evenly",
    }),
    dcc.Graph(id='plot', figure=make_subplots(specs=[[{"secondary_y": True}]]), style={
        "height": "600px"
    }),
])

# Add App Callback functions that correspond to the initial layout.
@app.callback(Output('left_dropdown', 'options'),
              [Input('left_category', 'value')])
def update_left_options(category):
    """Updates dropdown options when left category is changed

    Arguments:
        category {str} -- "crypto" "stocks" or "covid"

    Returns:
        {dict} -- dash compatible dict of options for a given category
    """
    return OPTIONS[category]

@app.callback(Output('right_dropdown', 'options'),
              [Input('right_category', 'value')])
def update_right_options(category):
    """Updates dropdown options when right category is changed

    Arguments:
        category {str} -- "crypto" "stocks" or "covid"

    Returns:
        {dict} -- dash compatible dict of options for a given category
    """
    return OPTIONS[category]

@app.callback(Output('plot', 'figure'),
            [Input('left_dropdown', 'value'),
            Input('left_trace_type', 'value'),
            Input('right_dropdown', 'value'),
            Input('right_trace_type', 'value'),
            Input('begin_date', "value"),
            Input('end_date', 'value')])
def update_figure(left_selection, left_trace_type, right_selection, right_trace_type, begin_date, end_date):
    """Initializes new DbProcessor in the current thread. Queries Db and updates the plot based on current inputs. 

    Arguments:
        left_selection {str} -- option selected from left dropdown
        left_trace_type {str} -- option selected from left radio buttons ("candlestick" or "scatter")
        right_selection {str} -- option selected from right dropdown
        right_trace_type {str} -- option selected from right radio buttons ("candlestick" or "scatter")
        begin_date {int} -- begin timestamp passed to DbProcessor.get_timeseries
        end_date {int} -- end timestamp passed to DbProcessor.get_timeseries

    Returns:
        fig {Figure} -- A plot updated with data corresponding to current inputs
    """

    # Init new DbProcessor in current thread
    db = DbProcessor("db.sqlite")
    # Init new Figure with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig_title = ""
    num_candlesticks = 0
    for selection, trace_type, secondary_y in ((left_selection, left_trace_type, False), (right_selection, right_trace_type,True)):
        # Query Db to get timeseries of data for selected option between begin_date and end_date 
        timeseries_dict = db.get_timeseries(selection, begin_date, end_date)

        # Determine params to create trace and labels based on if item is a covid stat or a crypto/stock 
        if is_covid_stat(selection):
            scatter_ykey = selection
            allow_candlesticks = False
            yaxis_label = PLOTABLE_VARS["covid"][selection]
            legend_label = yaxis_label
        else:
            scatter_ykey = "close"
            allow_candlesticks = True
            yaxis_label = f"USD per {selection}"
            legend_label = PLOTABLE_VARS["stock"].get(selection, PLOTABLE_VARS["crypto"].get(selection))

        # Create a Candlestick trace or Scatter trace depending on user selection and nature of data
        if trace_type == "candlestick" and allow_candlesticks:
            trace = go.Candlestick(
                name = legend_label,
                x = [datetime.fromtimestamp(timestamp) for timestamp in timeseries_dict["timestamp"]],
                open = timeseries_dict["open"],
                close = timeseries_dict["close"],
                high = timeseries_dict["high"],
                low = timeseries_dict["low"],
                increasing_line_color= 'cyan' if num_candlesticks > 0 else "green", 
                decreasing_line_color= 'gray' if num_candlesticks > 0 else "red" )
            num_candlesticks += 1
        else:
            trace = go.Scatter(
                name=legend_label,
                x = [datetime.fromtimestamp(timestamp) for timestamp in timeseries_dict["timestamp"]],
                y=timeseries_dict[scatter_ykey],
                line=dict(color='darkblue' if selection == right_selection else "black")
        )  

        # Add trace to fig and update y-axis with new label
        fig.add_trace(trace, secondary_y=secondary_y)
        fig.update_yaxes(title_text=f"<b>{yaxis_label}</b>", secondary_y=secondary_y)
        if fig_title != "":
            fig_title += " vs. "
        fig_title += legend_label

    # Update plot title
    fig.update_layout(title_text=f"<b>{fig_title}</b>")
    return fig

if __name__ == '__main__':
    # Run App
    app.run_server(debug=False)
