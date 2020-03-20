from templates.marketdata import MarketData
    

market_data = MarketData()

def error_msg(err):
    """
    Return a helpful error message div

    Parameters
    ----------
    err : str
        Error message to help the user

    Returns
    -------
    Formatted error message to be inserted to page
    """
    error_div = f'''
        <h3>ERROR</h3>
        <p>
        OH NO! The following error was received:<br>
        <code>{err}</code><br>
        <br>
        If the message specifies that the call limit has been reached, please
        wait a few minutes and try again.<br>
        Otherwise, you may have supplied an invalid stock symbol.
        </p>
    '''
    return error_div

def plot_stocks(form):
    """ Plot the actual stock data using user provided information

    Parameters
    ----------
    form : response.form object
        User submitted information
    
    Returns
    -------
    (script,div) for showing the plots in the webpage
    """
    # Extract the data from the user submitted form (if data is not empty)
    symbols = []
    if form.get('sname'):
        symbols = form.get('sname').split(',')

    # Get colorblind-friendly?
    cb_friendly = False
    if bool(form.get('colorblind')):
        cb_friendly = True

    # Get major indices
    if bool(form.get('djia')):
        symbols.append('DJI')    
    if bool(form.get('sp500')):
        symbols.append('SPX')
    # if bool(form.get('nasdaq')):
    #     pass
    
    # Update the data
    err = market_data.queryStocks(symbols)

    # Check if an error was returned
    if err:
        return '',error_msg(err)
    else:
        return market_data.plot(symbols, param=form.get('plotinfo'),cbf=cb_friendly)
