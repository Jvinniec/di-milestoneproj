from math import pi
import os
import json
from dateutil.relativedelta import relativedelta
import datetime
import pandas as pd
import numpy as np

# Alpha Vantage module
from alpha_vantage.timeseries import TimeSeries

# Bokeh plotting
from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed    import components
from bokeh.models   import HoverTool, Range1d

# Define a class for holding the market data
class MarketData:
    """ Class for holding market data """
    
    def __init__(self):
        """ Initialize the MarketData object 
        """
        # Create storage for each stock. Each stock is represented as an entry
        # in the following dictionary. This allows caching each stock that is
        # queried so we don't need to look it up a second time. Each stock id
        # references a pandas dataframe storing open, close, high, low, and 
        # volume trading data for the past 20 years
        self.stock_data = dict()

        # Keep track of some information associated with the stock
        self.stock_info = dict()

        # Update the column names
        self.data_cols = {'1. open'              : 'open',
                          '2. high'              : 'high',
                          '3. low'               : 'low',
                          '4. close'             : 'close',
                          '5. adjusted close'    : 'closeAdj',
                          '6. volume'            : 'volume',
                          '7. dividend amount'   : 'dividend',
                          '8. split coefficient' : 'splitcoeff'}
        # Stock info column names
        self.info_cols = {'1. symbol' : 'symbol',
                          '2. name'   : 'name'}

        # Set the bar colors
        self.line_colors = ['black','red','blue','green','orange']
        self.setcolors(False)

        # Setup the query objects
        self.timeseries = TimeSeries(os.environ['AVTOKEN'], output_format='pandas')


    def setcolors(self, cbf=False):
        """ Sets the bar colors for candlestick plot

        Parameters
        ----------
        cbf : bool
            True if color-blind friendly colors should be used
        """
        # Colorblind friendly colors?
        if cbf:
            self.colors = {'inc': 'blue', 'dec': 'orange'}
        # Red/green are fine
        else:
            self.colors = {'inc': 'lightgreen', 'dec': 'red'}


    def queryStocks(self, symbols):
        """ Extracts the latest stock information and stores it

        Parameters
        ----------
        symbols : list(str)
            List of symbols to query for

        Returns
        -------
        Error message string if an error occurs.
        """
        # Track whether there was an error
        errMsg = None

        # Loop on each symbol
        for sym in symbols:
            if sym not in self.stock_data.keys():
                try:
                    # Get info regarding this symbol
                    if sym not in ['DJI','SPX']:
                        info = self.timeseries.get_symbol_search(sym)
                    
                    # Get the data for this symbol
                    dat = self.timeseries.get_daily_adjusted(symbol=sym, outputsize='full')
                except ValueError as err:
                    errMsg  = err
                    break

                # Store the data in a dataframe                
                market_df = pd.DataFrame(dat[0])
                market_df['datetime'] = pd.to_datetime(market_df.index)
                
                # Extract info as dataframe
                if sym not in ['DJI','SPX']:
                    info_df = pd.DataFrame(info[0])
                    info_df.index = info_df.index.astype(int)
                else:
                    info_df = pd.DataFrame([[sym, sym]],
                                           columns=['1. symbol', '2. name'])
                    print(info_df.head())
                
                # Store the dataframe
                self.stock_data[sym] = market_df.rename(columns=self.data_cols)
                self.stock_info[sym] = info_df.rename(columns=self.info_cols)

        return errMsg
        

    def plotCandlesticks(self, symbol, days2show=100):
        """ Plots the stock information for all symbols in 'symbols'.

        Parameters
        ----------
        symbols : list(str)
            Python list of symbols to be plotted
        days2show : int
            Initial number of days to show data for when plot first loads

        Returns
        -------
        bokeh.plotting.figure object
        """
        # Get the data associated with this symbol
        df   = self.stock_data[symbol]
        info = self.stock_info[symbol]

        # Get indices for increasing/decresing market days
        inc = df.close > df.open
        dec = df.open > df.close

        # Specify the width of the bars
        w = 20*60*60*1000 # half day in ms

        # Define over tooltips
        hover = HoverTool(tooltips=[('Date',       '@datetime{%F}'),
                                    ('Open',       '$@open{0.2f}'),
                                    ('Adj. Close', '$@closeAdj{0.2f}'),
                                    ('High',       '$@high{0.2f}'),
                                    ('Low',        '$@low{0.2f}'),
                                    ('Volume',     '@volume{0.00 a}')],
                          formatters={'@datetime': 'datetime'},
                          names=['segments'])

        # Define the tools for user manipulation of figure
        TOOLS = ['pan','wheel_zoom','box_zoom','reset','save', hover]

        # Specify the range of the x,y axes
        xstop  = df.datetime[0] + relativedelta(days=3)
        xstart = xstop - relativedelta(days=days2show)
        ystart = 0.95 * np.min(df.low[:days2show])
        ystop  = 1.05 * np.max(df.high[:days2show])

        # Setup the figure for plotting
        p = figure(x_axis_type="datetime", tools=TOOLS, 
                   x_range=(xstart, xstop), y_range=(ystart,ystop),
                   x_axis_label='Date', y_axis_label='Price ($USD)',
                   plot_width=750, plot_height=400, 
                   title=f"Stock Price Data: {info['name'][0]}")
        p.xaxis.major_label_orientation = pi/4
        p.grid.grid_line_alpha=0.3

        # Generate the plots
        p.segment('datetime', 'high', 'datetime', 'low', source=ColumnDataSource(df),
                   color="black", line_width=2, name='segments')
        p.vbar(df.datetime[inc], w, df.open[inc], df.close[inc], 
               fill_color=self.colors['inc'], line_color="black", name='incbar')
        p.vbar(df.datetime[dec], w, df.open[dec], df.close[dec], 
               fill_color=self.colors['dec'], line_color="black", name='decbar')

        return p


    def plotStocks(self, symbols, param, days2show=100):
        """ Plots the stock information for all symbols in 'symbols'.

        Parameters
        ----------
        symbols : list(str)
            Python list of symbols to be plotted
        param : str
            Parameter to plot (open, close, high, low, volume)
        days2show : int
            Initial number of days to show data for when plot first loads

        Returns
        -------
        bokeh.plotting.figure object
        """

        # Define the tools for user manipulation of figure
        TOOLS = ['pan','wheel_zoom','box_zoom','reset','save']

        # Define the starting range to be the last 100 days
        xstop  = datetime.datetime.now() + relativedelta(days=3)
        xstart = xstop - relativedelta(days=days2show)
        ystart = 1e30
        ystop  = -1e30
            
        # Setup the figure for plotting
        p = figure(x_axis_type="datetime", tools=TOOLS, x_range=(xstart, xstop),
                   plot_width=750, plot_height=400, 
                   x_axis_label='Date', y_axis_label=param,
                   title=f"{param.upper()} Data: {', '.join(symbols)}")

        for s,sym in enumerate(symbols):
            # Get the data associated with this symbol
            df   = self.stock_data[sym]
            info = self.stock_info[sym]

            # Specify the range of the x,y axes
            ystart = min(ystart, np.min(df[param][:days2show]))
            ystop  = max(ystop, np.max(df[param][:days2show]))

            # Add the next line plot
            color_indx = s % len(self.line_colors)
            p.line(df.datetime, df[param], 
                   line_color=self.line_colors[color_indx], legend_label=info.name[0])

        # Update the range of x,y
        p.y_range = Range1d(0.95*ystart, 1.05*ystop)
        
        # Setup the legend
        p.legend.location = "top_left"

        return p


    def plot(self, symbols, param='closeAdj', cbf=False):
        """

        Parameters
        ----------
        symbols : list()
            Python list of symbols to be plotted
        param : str
            Parameter to be plotted for multi-symbol plots
        cbf : bool
            Whether color blind friendly colors should be used
        
        Returns
        -------
        (script,div) for showing the plots in the webpage
        """
        # Update colors if colorblind friendly
        self.setcolors(cbf)

        # Get the actual figure to be plotted
        p = None
        if len(symbols) == 1:
            p = self.plotCandlesticks(symbols[0])
        else:
            p = self.plotStocks(symbols, param)

        return components(p)
