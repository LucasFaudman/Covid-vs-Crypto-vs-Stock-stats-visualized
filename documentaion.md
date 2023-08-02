####################################BEGIN shared.py DOCUMENTATION####################################
def is_covid_stat(plot_var):
    """Determines if a given variable is a Covid-19 statistic or not

    Arguments:
        plot_var {str} -- variable to check whether it is a Covid-19 stat or not

    Returns:
        {bool} -- True if plot_var is a Covid-19 stat False if plot_var is a crypto or stock
    """
    return plot_var in PLOTABLE_VARS["covid"]

def retry_or_breakpoint_on_execption(exception, retry_function,sleep_seconds=10, **kwargs):
    """Asks user if they would like to retry or breakpoint()

    Arguments:
        exception {Exception} -- the exception that tiggered this function
        retry_function {function} -- the function to call when retrying
        
    Keyword Arguments:
        sleep_seconds {int} -- # of seconds to sleep before calling retry_function (default: {10})
        **kwargs {dict} -- keyword args to pass to retry_function if called

    Returns:
        {tuple} -- a tuple of dicts that has both __iter__ and .items() methods
    """

class BaseDB:
    """Base class whose __init__ method is shared by both 
    DbGetter and DbProcessor subclasses.
    """
    def __init__(self, filepath):
        """Initializes sqlite connection and cursor to Db at filepath

        Arguments:
            filepath {str} -- path to .sqlite file
        """

####################################BEGIN get.py DOCUMENTATION######################################
def get_covid_data(keys_to_get=tuple(PLOTABLE_VARS["covid"].keys())):
    """Gets COVID-19 daily statistical data from covidtracking.com in JSON format.
    Accumulates a list of dicts with each dict containing a datetime.timestamp() and 
    values for each of the keys in keys_to_get. 

    Keyword Arguments:
        keys_to_get {tuple} -- list of keys to add to each dict in data_dicts (default: {list(PLOTABLE_VARS["covid"].keys())})

    Returns:
        data_dicts {list} -- list of dicts containing data for each key in keys_to_get and a timestamp
    """

def get_crypto_data(from_asset, to_asset="USD", exchange="CCCAGG", time_offset=None, limit=100,
                    keys_to_get=CANDLESTICK_COL_NAMES):
    """Gets daily cryptocurrency price data of from_asset measured in to_asset 
    from min-api.cryptocompare.com in JSON format. Accumulates a list of dicts with each dict 
    containing a datetime.timestamp() and values for each of the keys in keys_to_get. 

    Arguments:
        from_asset {str} -- symbol of asset to get data for

    Keyword Arguments:
        to_asset {str} -- symbol of asset to get data return data in (default: {"USD"})
        exchange {str} -- which exchange(s) or aggregator fetch price data from (default: {"CCCAGG"})
        time_offset {datetime.timestamp} -- offset used to get data from over 2000 days in the past (default: {None})
        limit {int} -- how many days backwards to search and how many records to return (default: {100})
        keys_to_get {tuple} -- list of keys to add to each dict in data_dicts (default: {CANDLESTICK_COL_NAMES})

    Returns:
        data_dicts {list} -- list of dicts containing data for each key in keys_to_get and a timestamp
    """

def get_stock_data(symbol,keys_to_get=CANDLESTICK_COL_NAMES):
    """Gets daily stock price data for the stock with symbol, measured in USD
    from alphavantage.co in JSON format. Accumulates a list of dicts with each dict 
    containing a datetime.timestamp() and values for each of the keys in keys_to_get. 

    Arguments:
        symbol {str} -- symbol of asset to get data for

    Keyword Arguments:
        keys_to_get {tuple} -- [description] (default: {CANDLESTICK_COL_NAMES})

    Returns:
       data_dicts {list} -- list of dicts containing data for each key in keys_to_get and a timestamp
    """

class DbGetter(BaseDB):
    """Object to facalitate setting up and inserting data into sqlite database.

    Arguments:
        BaseDB {object} -- Base Class for DbGetter so it inherits __init__ which
        initializes sqlite connection and cursor to Db at filepath
    """
    def setup_tables(self, setup_params=PLOTABLE_VARS,candlestick_setup_params=CANDLESTICK_COL_NAMES):
        """Creates a dict of template data based on setup_params and candlestick_setup_params. 
        Then creates tables in Db that are able to hold the produced template data

        Arguments:
            self {DbGetter} -- The DbGetter instance to modify

        Keyword Arguments:
            setup_params {dict} -- Desired crypto + stock table names and Covid column names
            candlestick_setup_params {dict} -- Desired crypto + stock column names to contain candlestick data
        """
  
    def _get_date_id(self, timestamp):
        """Internal method for converting timestamp to date_id based on current Db contents. 
        If a timestamp has been assigned a date_id then it is returned. Otherwise, the timestamp
        is added to the dates table and the newly created date_id is returned. 

        Arguments:
            self {DbGetter} -- The DbGetter instance to modify
            timestamp {int or float} -- timestamp to get or create date_id for

        Returns:
            date_id[0] {int} -- date_id of timestamp in Db.dates 
        """
 
    def _insert_data(self, table_name, data_dict):
        """Internal method for inserting a row of data into table_name. 
        Each key value pair in data_dict corresponds to a column name in the Db and the value for the row to be inserted. 
        The timestamp of each data_dict is removed and its date_id is used instead to prevent duplicate timestamps.

        Arguments:
            self {DbGetter} -- The DbGetter instance to modify
            table_name {str} -- Name of table to insert data into
            data_dict {dict} -- dict containing column names and a row of data

        """

    def insert_newest_data(self, table_name, data_dicts, max_inserts=1):
        """Inserts at most max_inserts rows of new data into table name. 
        Counts number of successful inserts.
        Arguments:
            self {DbGetter} -- The DbGetter instance to modify
            table_name {str} -- Name of table to insert data into
            data_dicts {dict} -- list of dicts containing column names and a row of data
        
        Keyword Arguements:
            max_inserts {int} -- Max number of inserts allowed from a given invocation

        Returns:
            num_inserts {int} -- Number of inserts that completed without error
        """

####################################BEGIN process.py DOCUMENTATION######################################
class DbProcessor(BaseDB):
    """Object to facalitate selecting data from an sqlite database, processing the data
    and writing to a file.

    Arguments:
        BaseDB {object} -- Base Class for DbGetter so it inherits __init__ which
        initializes sqlite connection and cursor to Db at filepath
    """
    def get_timeseries(self, plot_var, begin_timestamp, end_timestamp, candlestick_col_names=CANDLESTICK_COL_NAMES):
        """Determines table_names and cols_names based on wether plot_var is a covid stat or a
        crypto/stock asset. Selects timestamps and all data in col_names by joining dates and table_name
        between begin_timestamp and end_timestamp. Then calculates timeseries data for plot_var and accumulates
        in timeseries_dict. Then writes timeseries_dict to <plot_var>-calculations.json in JSON format and returns timeseries_dict.

        Arguments:
            self {DbProcessor} -- The DbGetter instance to modify
            plot_var {str} -- key of variable to be plotted by creating a timeseries
            begin_timestamp {int or float} -- first timestamp in the timeseries
            end_timestamp {int or float} -- last timestamp in the timeseries

        Keyword Arguements:
            candlestick_col_names {dict} -- Desired crypto + stock column names to contain candlestick data

        Returns:
            timeseries_dict {defaultdict(list)} -- dict of lists containing data from each column
        """

####################################BEGIN visualize.py DOCUMENTATION######################################
def make_dash_compatible_dicts(d):
    """Converts dict d to list of dicts in dash compatible format:
    {"value": <key>, "label": <val>}
    Arguments:
        d {dict} -- dict to convert

    Returns:
        {list} -- list of dash compatible dicts
    """

def get_2020_datetimes():
    """Generator of datetime objects from Jan 1 2020 
    up to current date.

    Yields:
        date {datetime} -- datetime object for a given date
    """

@app.callback(Output('left_dropdown', 'options'),
              [Input('left_category', 'value')])
def update_left_options(category):
    """Updates dropdown options when left category is changed

    Arguments:
        category {str} -- "crypto" "stocks" or "covid"

    Returns:
        {dict} -- dash compatible dict of options for a given category
    """

@app.callback(Output('right_dropdown', 'options'),
              [Input('right_category', 'value')])
def update_right_options(category):
    """Updates dropdown options when right category is changed

    Arguments:
        category {str} -- "crypto" "stocks" or "covid"

    Returns:
        {dict} -- dash compatible dict of options for a given category
    """

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