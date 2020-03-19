from math import pi
import json
import pandas as pd
import os

# Alpha Vantage module
from alpha_vantage.timeseries import TimeSeries

from bokeh.plotting          import figure
from bokeh.embed             import components

# Define a class for holding the market data
class MarketData:
    """ Class for holding market data """
    
    def __init__(self):
        """ Initialize the MarketData object """
        # Create storage for each stock. Each stock is represented as an entry
        # in the following dictionary. This allows caching each stock that is
        # queried so we don't need to look it up a second time. Each stock id
        # references a pandas dataframe storing open, close, high, low, and 
        # volume trading data for the past 20 years
        self.stock_data = dict()

        # Update the column names
        self.new_cols = {'1. open'   : 'open',
                         '2. high'   : 'high',
                         '3. low'    : 'low',
                         '4. close'  : 'close',
                         '5. volume' : 'volume'}


    def queryStocks(self, symbols):
        """ Extracts the latest stock information and stores it

        Parameters
        ----------
        symbols : list(str)
            List of symbols to query for
        """

        # Create a query object
        ts = TimeSeries(os.environ['AVTOKEN'], output_format='pandas')

        # Loop on each symbol
        for sym in symbols:
            if sym not in self.stock_data.keys():
                # Get the data for this symbol
                dat    = ts.get_daily_adjusted(symbol=sym, outputsize='full')
                
                # TODO: Handle error messages from the above query

                # Store the data in a dataframe                
                market_df = pd.DataFrame(dat[0])

                # Store the dataframe
                self.stock_data[sym] = market_df.rename(columns=self.new_cols)

        return
                
    def plotCandlesticks(self, symbol):
        df = self.stock_data[symbol]
        df["date"] = pd.to_datetime(df.index)

        inc = df.close > df.open
        dec = df.open > df.close
        w = 20*60*60*1000 # half day in ms

        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

        p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title = f"{symbol} Candlestick")
        p.xaxis.major_label_orientation = pi/4
        p.grid.grid_line_alpha=0.3

        p.segment(df.date, df.high, df.date, df.low, color="black")
        p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#0059FF", line_color="black")
        p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#FFA500", line_color="black")

        return p


    def plotStocks(self, symbols, param):
        """ Plots the stock information for all symbols in 'symbols'.

        Parameters
        ----------
        symbols : list(str)
            Python list of symbols to be plotted
        param : str
            Parameter to plot (open, close, high, low, volume)
        """
        pass

    def plot(self, symbols, param='detailed'):
        
        p = None
        if (len(symbols) == 1) and (param == 'detailed'):
            p = self.plotCandlesticks(symbols[0])
        else:
            p = self.plotStocks(symbols, param)

        return components(p)
