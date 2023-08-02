from json import dump
from collections import defaultdict
from os import mkdir
from os.path import isdir
from shared import *
    
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

        if is_covid_stat(plot_var):
            table_name = "covid"
            col_names = (plot_var,)
            percent_change_col = plot_var
        else:
            table_name = plot_var
            col_names = candlestick_col_names
            percent_change_col = "close"
        
        SQLcmd = f"""
            SELECT dates.timestamp, {', '.join(f'{table_name}.{col_name}' for col_name in col_names)} 
            FROM dates JOIN {table_name} 
            ON dates.date_id = {table_name}.date_id 
            WHERE dates.timestamp BETWEEN {begin_timestamp} AND {end_timestamp}
            ORDER BY dates.timestamp
            """
        print(SQLcmd)
        self.cur.execute(SQLcmd)

        # init as defaultdict(list) so lists will dynamically be generated for each key used
        timeseries_dict = defaultdict(list)
        for i, result_tup in enumerate(self.cur.fetchall()):
            for col_name, data in zip(("timestamp", *col_names), result_tup):
                timeseries_dict[col_name].append(data)

            percent_change = None
            if i > 0:
                current = timeseries_dict[percent_change_col][i] 
                previous = timeseries_dict[percent_change_col][i-1]
                if current and previous:
                    percent_change = ((current / previous) - 1) * 100

            timeseries_dict["percent_change"].append(percent_change)
        
        if not isdir("calculations"):
            mkdir("calculations")

        # Write calculations to file
        with open(f"calculations/{plot_var}.json", "w+") as f:
            dump(timeseries_dict, f,indent=2)

        return timeseries_dict

