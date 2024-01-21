from operator import index
from os import times
from dash import html, dcc,dash_table, Input, Output,State
from dash.dash_table import DataTable
from dash.dash_table.Format import Format, Group, Prefix, Scheme, Symbol
import dash_bootstrap_components as dbc
from app import fetch_data, DEFAULT_TICKERS
from datetime import datetime as dt
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
info_df=fetch_data()


# Function to create the navbar

def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Portfolio Time Series", href="/portfolio-time-series")),
            dbc.NavItem(dbc.NavLink("Stock Time Series", href="/stock-time-series")),
        ],
        brand="Tech Stocks Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
    )
    return navbar

# Home Page Layout with the Portfolio Table
# Fetch data for default tickers
index_page = html.Div([
 html.H1('Market Cap Based Portfolio'),
    
    # html.Div([
    #     dcc.Input(id='new-ticker-input', type='text', placeholder='Enter a new ticker...'),
    #     html.Button('Add Ticker', id='add-ticker-button', n_clicks=0),
    #     html.Button('Remove Ticker', id='remove-ticker-button', n_clicks=0),
    # ]),
    # html.Br(),
    DataTable(
        id='portfolio-table',
        columns=[{"name": i, "id": i} for i in info_df.columns],
        data=info_df.to_dict('records')
    ),
    html.Br(),
    html.Label('Select Date Range:'),
    dcc.DatePickerRange(
        id='portfolio-date-picker-range',
        start_date=dt.now() - pd.Timedelta(days=365),
        end_date=dt.now(),
        display_format='YYYY-MM-DD'
    ),
    dcc.Graph(id='portfolio-value-graph'),
    html.Br(),
    dcc.Link('Go to Stock Price Page', href='/stock-price')
])


# Portfolio Performance Page Layout
   
portfolio_page=html.Div([
    html.H1('Portfolio Value Over Time'),
    html.Label('Select Date Range:'),
    dcc.DatePickerRange(
        id='portfolio-date-picker-range',
        start_date=dt.now() - pd.Timedelta(days=365),
        end_date=dt.now(),
        display_format='YYYY-MM-DD'
    ),
    dcc.Graph(id='portfolio-value-graph'),#figure=create_portfolio_graph(DEFAULT_TICKERS)),
    html.Br(),
    dcc.Link('Go back to Home', href='/')
])

#


    # Fetch portfolio time series data
stock_page=html.Div([
    html.H1('Stock Prices Over Time'),

    html.Label('Select Stocks:'),
    dcc.Dropdown(
        id='stock-dropdown',
        options=[{'label': ticker, 'value': ticker} for ticker in DEFAULT_TICKERS],
        value=['AAPL'],  # Default value
        multi=True  # Allow multiple selections
    ),

    html.Br(),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=dt.now() - pd.Timedelta(days=365),
        end_date=dt.now(),
        display_format='YYYY-MM-DD'
    ),

    dcc.Graph(id='stock-price-graph'),
    html.Br(),
    dcc.Link('Go back to Home', href='/')
])