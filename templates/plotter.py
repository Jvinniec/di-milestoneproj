from templates.marketdata import MarketData
    

market_data = MarketData()

def plot_stocks(form):
    # Extract the data from the user submitted form
    symbols = form.get('sname').split(',')
    form.get('plotinfo')
    print(form.get('plotinfo'))
    if bool(form.get('djia')):
        symbols.append('DJI')

    if bool(form.get('sp500')):
        symbols.append('SPX')

    if bool(form.get('nasdaq')):
        pass
    
    # Update the data
    market_data.queryStocks(symbols)

    return market_data.plot(symbols)
