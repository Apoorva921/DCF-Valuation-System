"""
Updated data.py using yfinance (compatible with DCF slicing logic)
"""

import yfinance as yf
import traceback


def get_income_statement(ticker, period='annual', apikey=''):
    try:
        stock = yf.Ticker(ticker)
        df = stock.financials

        # Convert DataFrame → list of dicts
        data = df.T.reset_index().to_dict(orient='records')

        return data   # ✅ IMPORTANT: return list
    except Exception as e:
        print(f"Error fetching income statement for {ticker}")
        print(traceback.format_exc())
        return []


def get_cashflow_statement(ticker, period='annual', apikey=''):
    try:
        stock = yf.Ticker(ticker)
        df = stock.cashflow

        data = df.T.reset_index().to_dict(orient='records')

        return data
    except Exception as e:
        print(f"Error fetching cash flow for {ticker}")
        print(traceback.format_exc())
        return []


def get_balance_statement(ticker, period='annual', apikey=''):
    try:
        stock = yf.Ticker(ticker)
        df = stock.balance_sheet

        data = df.T.reset_index().to_dict(orient='records')

        return data
    except Exception as e:
        print(f"Error fetching balance sheet for {ticker}")
        print(traceback.format_exc())
        return []


def get_EV_statement(ticker, period='annual', apikey=''):
    """
    Replacement for Enterprise Value
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return [{
            'enterpriseValue': info.get('enterpriseValue', 0),
            'numberOfShares': info.get('sharesOutstanding', 0)
        }]
    except Exception as e:
        print(f"Error fetching EV data for {ticker}")
        return [{
            'enterpriseValue': 0,
            'numberOfShares': 0
        }]


def get_stock_price(ticker, apikey=''):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'][0]

        return {'symbol': ticker, 'price': price}
    except Exception as e:
        print(f"Error fetching stock price for {ticker}")
        print(traceback.format_exc())
        return {'symbol': ticker, 'price': None}


def get_batch_stock_prices(tickers, apikey=''):
    prices = {}
    for ticker in tickers:
        prices[ticker] = get_stock_price(ticker)['price']
    return prices


def get_historical_share_prices(ticker, dates, apikey=''):
    prices = {}
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")

        for date in dates:
            try:
                prices[date] = hist.loc[date]['Close']
            except:
                prices[date] = None

    except Exception as e:
        print(f"Error fetching historical prices for {ticker}")
        print(traceback.format_exc())

    return prices


if __name__ == '__main__':
    ticker = 'AAPL'
    print(get_income_statement(ticker))