import sqlite3
from datetime import datetime, timedelta
from time import sleep

# Default Variables to store in Db and later plot
PLOTABLE_VARS = {
    "crypto": {
        "BTC": "Bitcoin (BTC)",
        "XMR": "Monero (XMR)",
        "LTC": "Litecoin (LTC)",
        "ETH": "Ethereum (ETH)",
        "BCH": "Bitcoin Cash (BCH)",
        "DASH": "Dash (DASH)",
        "XRP": "Ripple (XRP)",
     },
    "stock": {
        "DJI": "Dow Jones (DJI)",
        "VIX": "Volatility (VIX)",
        "AAPL": "Apple (AAPL)",
        "NFLX": "Netflix (NFLX)",
        "DPZ" : "Dominos Pizza (DPZ)"
    },
    "covid" : {
        "deathIncrease": "Daily Deaths",
        "hospitalizedIncrease": "Daily Hospitalizations",
        "positiveIncrease": "Daily Positive Tests",
        "negativeIncrease": "Daily Negative Tests",
        "totalTestResultsIncrease": "Daily Tests",
        "positive": "Total Positive Tests",
        "negative": "Total Negative Tests",
        "pending": "Total Pending Tests",
        "totalTestResults": "Total Tests",
        "death": "Total Deaths",
        "recovered": "Total Recovered",
        "hospitalizedCumulative": "# of Patients Hospitalized Overall",
        "hospitalizedCurrently": "# of Patients Hospitalized Currently",
        "inIcuCumulative": "# of Patients In Icu Overall",
        "inIcuCurrently": "# of Patients In Icu Currently",
        "onVentilatorCumulative": "# of Ventilators Used Overall",
        "onVentilatorCurrently": "# of Ventilators In Use Currently",
        "states": "# of States With Cases"
    }
}

# Col names used for generating Candlestick plots for crypto and stock data
CANDLESTICK_COL_NAMES = ("open", "close", "high", "low")

## MISC HELPER FUNCTIONS

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
    retry = input(f"ERROR: {exception}\nRetry [y/n]?").lower()
    if retry.startswith("y"):
        sleep(sleep_seconds)
        return retry_function(**kwargs)
    elif retry.startswith("b"):
        breakpoint()
    return ({"error":exception,"timestamp":0})

class BaseDB:
    """Base class whose __init__ method is shared by both 
    DbGetter and DbProcessor subclasses.
    """
    def __init__(self, filepath):
        """Initializes sqlite connection and cursor to Db at filepath

        Arguments:
            filepath {str} -- path to .sqlite file
        """
        self.filepath = filepath
        self.conn = sqlite3.connect(filepath)
        self.cur = self.conn.cursor()

