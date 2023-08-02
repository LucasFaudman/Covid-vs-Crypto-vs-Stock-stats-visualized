import requests
import argparse
from os.path import isfile
from pprint import pprint
from shared import *


def get_covid_data(keys_to_get=tuple(PLOTABLE_VARS["covid"].keys())):
    """Gets COVID-19 daily statistical data from covidtracking.com in JSON format.
    Accumulates a list of dicts with each dict containing a datetime.timestamp() and 
    values for each of the keys in keys_to_get. 

    Keyword Arguments:
        keys_to_get {tuple} -- list of keys to add to each dict in data_dicts (default: {list(PLOTABLE_VARS["covid"].keys())})

    Returns:
        data_dicts {list} -- list of dicts containing data for each key in keys_to_get and a timestamp
    """
    covid_api_url = "https://covidtracking.com/api/v1/us/daily.json"
    try:
        resp = requests.get(covid_api_url)
        json_resp = resp.json()
        data_dicts = []
        for d in json_resp:
            data_dict = {}
            for key, val in d.items():
                if key in keys_to_get:
                    data_dict[key] = val
                elif key == "dateChecked":
                    try:
                        data_dict["timestamp"] = datetime.strptime(
                        
                        val.split("T")[0], "%Y-%m-%d").timestamp()#
                        data_dicts.append(data_dict)   
                    except Exception as e:
                        print(e)
                        breakpoint()
                        

        return data_dicts
    except (requests.HTTPError, KeyError) as e:
        retry_or_breakpoint_on_execption(
            e, get_covid_data, keys_to_get=keys_to_get)


def get_crypto_data(from_asset, to_asset="USD", exchange="CCCAGG", time_offset=None, limit=365,
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
    cryptocompare_api_url = "https://min-api.cryptocompare.com/data/histoday"
    params = {
        "fsym": from_asset,
        "tsym": to_asset,
        "e": exchange,
        "limit": limit,
        "toTs": time_offset,
        "sign": "true"
    }
    try:
        resp = requests.get(cryptocompare_api_url, params)
        json_resp = resp.json()["Data"]
        data_dicts = []
        for d in json_resp:
            data_dict = {}
            for key, val in d.items():
                if key in keys_to_get:
                    data_dict[key] = val
                elif key == "time":
                    data_dict["timestamp"] = val
            data_dicts.append(data_dict)
        return data_dicts

    except (requests.HTTPError, KeyError) as e:
        retry_or_breakpoint_on_execption(
            e, get_crypto_data, from_asset=from_asset, to_asset=to_asset, exchange=exchange, time_offset=time_offset, limit=limit,
            keys_to_get=keys_to_get)


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
    alphavantage_api_url = "https://www.alphavantage.co/query"
    params = {
        "symbol": symbol,
        "function": "TIME_SERIES_DAILY",
        "datatype": "json",
        "apikey": "5BZHK9J4OFD30IPU",
    }
    try:
        resp = requests.get(alphavantage_api_url, params)
        json_resp = resp.json()["Time Series (Daily)"]
        data_dicts = []
        for date, d in json_resp.items():
            data_dict = {"timestamp": datetime.strptime(
                date, "%Y-%m-%d").timestamp()}
            for key, val in d.items():
                key = key.split(". ")[1]
                if key in keys_to_get:
                    data_dict[key] = float(val)
            data_dicts.append(data_dict)
        return data_dicts 

    except (requests.HTTPError, KeyError) as e:
        print(resp.json())
        return retry_or_breakpoint_on_execption(
            e, get_stock_data, symbol=symbol,keys_to_get=keys_to_get)
        


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
        template_data = {
            "crypto": {col_name: "FLOAT" for col_name in candlestick_setup_params},
            "stock": {col_name: "FLOAT" for col_name in candlestick_setup_params},
            "covid": {col_name: "INTEGER" for col_name in setup_params["covid"]},
        }

        table_names_and_SQL_datatypes = {
            symbol: template_data[category] for category in ("crypto", "stock") for symbol in setup_params[category]
        }

        table_names_and_SQL_datatypes["covid"] = template_data["covid"]
        table_names_and_SQL_datatypes["dates"] = {"timestamp": "TIMESTAMP"}
        pprint(table_names_and_SQL_datatypes)

        for table_name, col_names_and_datatypes in table_names_and_SQL_datatypes.items():
            try:
                SQLcmd = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    date_id INTEGER PRIMARY KEY, 
                    {', '.join(f'{col_name} {col_type}' for col_name, col_type in col_names_and_datatypes.items())}
                )
                """
                print(SQLcmd)
                self.cur.execute(SQLcmd)
                self.conn.commit()
            except sqlite3.OperationalError as e:
                print(e)
                breakpoint()

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
        SQLcmd = f"""
            SELECT date_id 
            FROM dates 
            WHERE timestamp = '{timestamp}' 
            ORDER BY timestamp
            """
        self.cur.execute(SQLcmd)
        # Search for an existing date_id for timestamp to prevent duplicates
        date_id = self.cur.fetchone()
        if not date_id:
            # Create new date_id if one does not exist for timestamp
            self.cur.execute(
                f"INSERT INTO dates (timestamp ) VALUES (? )", (timestamp,))
            self.conn.commit()
            self.cur.execute(SQLcmd)
            date_id = self.cur.fetchone()
        return date_id[0]
        

    def _insert_data(self, table_name, data_dict):
        """Internal method for inserting a row of data into table_name. 
        Each key value pair in data_dict corresponds to a column name in the Db and the value for the row to be inserted. 
        The timestamp of each data_dict is removed and its date_id is used instead to prevent duplicate timestamps.

        Arguments:
            self {DbGetter} -- The DbGetter instance to modify
            table_name {str} -- Name of table to insert data into
            data_dict {dict} -- dict containing column names and a row of data

        """
        data_dict["date_id"] = self._get_date_id(data_dict.pop("timestamp"))
        try:
            SQLcmd = f"INSERT INTO {table_name} ({', '.join(data_dict)}) VALUES ({', '.join('?' for k in data_dict)})"
            params = (*data_dict.values(),)
            print(SQLcmd, params)
            self.cur.execute(SQLcmd, params)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            breakpoint()

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
        try:
            self.cur.execute(f"""
                SELECT dates.timestamp 
                FROM dates JOIN {table_name} 
                ON dates.date_id = {table_name}.date_id 
                ORDER BY dates.timestamp
                """)
            # Find newest timestamp already recorded
            recorded_dates = self.cur.fetchall()
            if recorded_dates:
                newest_date = recorded_dates[-1][0]

            num_inserts = 0
            # Iterate from earliest to latest timestamp
            for data_dict in sorted(data_dicts, key=lambda d: d["timestamp"]):
                dict_timestamp = data_dict.get("timestamp")
                # Insert data_dicts new than the current newest date
                if not recorded_dates or dict_timestamp > newest_date:
                    self._insert_data(table_name, data_dict)
                    num_inserts += 1
                    if num_inserts < max_inserts:
                        newest_date = dict_timestamp
                    else:
                        break
            return num_inserts
        except sqlite3.OperationalError as e:
            print(e)
            breakpoint()
            return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_filename",default="db.sqlite",type=str)
    parser.add_argument("--max_inserts_per_table",default=100000,type=int)
    parser.add_argument("--max_inserts_per_execution",default=100000,type=int)
    args = parser.parse_args()

    db_filename = args.db_filename
    max_inserts_per_table = args.max_inserts_per_table
    max_inserts_per_execution = args.max_inserts_per_execution

    # Initialize DbGetter at db_filepath and setup data tables if no file existed prior to initialization
    do_setup_tables = not isfile(db_filename)
    db = DbGetter(db_filename)
    if do_setup_tables:
        db.setup_tables()

    # Insert rows of data for crypto stocks and covid. Counts number of inserts that completed successfully
    num_items_inserted = 0
    for symbol in PLOTABLE_VARS["crypto"]:
        data_dicts = get_crypto_data(symbol)
        pprint(data_dicts)
        num_items_inserted += db.insert_newest_data(
            symbol, data_dicts, max_inserts_per_table)
    
    for symbol in PLOTABLE_VARS["stock"]:
        data_dicts = get_stock_data(symbol)
        pprint(data_dicts)
        try:
            num_items_inserted += db.insert_newest_data(symbol, data_dicts, max_inserts_per_table)
        except:
            continue

    data_dicts = get_covid_data()
    pprint(data_dicts)
    num_items_inserted += db.insert_newest_data("covid", data_dicts, max_inserts_per_table)

    # Check assertion that no more than 20 items inserted per execution
    # with max_inserts=1 this number will always be between 1-13
    assert num_items_inserted <= max_inserts_per_execution
    print(f"\nSUCCESSFULLY INSERTED {num_items_inserted} Items!")

