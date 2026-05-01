import argparse, traceback
from decimal import Decimal
import yfinance as yf

from modeling.data import *


def DCF(ticker, ev_statement, income_statement, balance_statement, cashflow_statement, discount_rate, forecast, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate):

    enterprise_val = enterprise_value(
        ticker,
        forecast,
        discount_rate,
        earnings_growth_rate,
        perpetual_growth_rate
    )

    equity_val, share_price = equity_value(enterprise_val, ev_statement)

    print('\nEnterprise Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(enterprise_val))),
          '\nEquity Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(equity_val))),
          '\nPer share value for {}: ${}.\n'.format(ticker, '%.2E' % Decimal(str(share_price))),
          )

    return {
        'date': 'Latest',
        'enterprise_value': enterprise_val,
        'equity_value': equity_val,
        'share_price': share_price
    }


def historical_DCF(ticker, years, forecast, discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, interval='annual', apikey=''):

    dcfs = {}

    enterprise_value_statement = get_EV_statement(ticker=ticker)

    dcf = DCF(
        ticker,
        enterprise_value_statement[0],
        None, None, None,
        discount_rate,
        forecast,
        earnings_growth_rate,
        cap_ex_growth_rate,
        perpetual_growth_rate
    )

    dcfs[ticker] = dcf
    return dcfs


def equity_value(enterprise_value, ev_statement):

    shares = ev_statement.get('numberOfShares', 1)

    equity_val = enterprise_value
    share_price = equity_val / float(shares if shares else 1)

    return equity_val, share_price


def enterprise_value(ticker, period, discount_rate, growth_rate, perpetual_growth_rate):

    stock = yf.Ticker(ticker)

    # ✅ Get real Free Cash Flow
    cashflow = stock.cashflow

    try:
        operating_cf = cashflow.loc['Total Cash From Operating Activities'][0]
        capex = cashflow.loc['Capital Expenditures'][0]
    except Exception:
        print("WARNING: Using fallback values")
        operating_cf = 1e11
        capex = -2e10

    # FCF = Operating Cash Flow - CapEx
    fcf = operating_cf - capex

    if fcf <= 0:
        fcf = abs(fcf)

    flows = []

    print(f'Forecasting flows for {period} years.')

    for yr in range(1, period + 1):

        # declining growth
        growth = growth_rate * (0.9 ** yr)

        fcf *= (1 + growth)

        PV_flow = fcf / ((1 + discount_rate) ** yr)
        flows.append(PV_flow)

        print(f"Year {yr}: {'%.2E' % Decimal(PV_flow)}")

    NPV_FCF = sum(flows)

    # Terminal Value
    final_cashflow = flows[-1] * (1 + perpetual_growth_rate)

    if discount_rate <= perpetual_growth_rate:
        discount_rate = perpetual_growth_rate + 0.01

    TV = final_cashflow / (discount_rate - perpetual_growth_rate)
    NPV_TV = TV / ((1 + discount_rate) ** (1 + period))

    return NPV_FCF + NPV_TV