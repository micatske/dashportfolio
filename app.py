from os import path
from dash import Dash, dcc, html
from dash.dependencies import Input, Output,State
from sklearn import metrics
import layouts
import time
import dash
import yfinance as yf
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime as dt
import plotly.graph_objs as go
from utils import calculate_portfolio_metrics



app = Dash(__name__,suppress_callback_exceptions=True)
app.title = 'Tech Stocks Dashboard'

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname in [None, '/', '/portfolio-table']:
        return layouts.index_page
    elif pathname == '/stock-price':
        return layouts.stock_page
    elif pathname == '/portfolio-page':
        return layouts.portfolio_page
    else:
        # This can be a 404 page or redirect to home
        return '404 - Page not found'




global DEFAULT_TICKERS
DEFAULT_TICKERS = ['AAPL', 'NFLX','MSFT', 'GOOGL', 'AMZN', 'META', 'TCEHY', 'TSLA', 'BABA', 'NVDA']
default_start_date = dt.now() - pd.Timedelta(days=365)
default_end_date =dt.now()

def fetch_data():
    stock_info = []
    for ticker in DEFAULT_TICKERS:
        ticker_info = yf.Ticker(ticker).info
        stock_info.append({
            'Company Name': ticker_info.get('longName', 'N/A'),
            'Ticker': ticker,
            'Market Cap': ticker_info.get('marketCap', 'N/A')
        })

    # Create DataFrame
    info_df = pd.DataFrame(stock_info)
    total_market_cap = info_df['Market Cap'].sum()

    info_df['Weight'] = round((info_df['Market Cap'] / total_market_cap)*100,2)

    # Assume a portfolio value of $10,000
    portfolio_value = 10000
    info_df['Investment'] = round(info_df['Weight'] * portfolio_value,2)
    return info_df






@app.callback(
     [#Output('portfolio-table', 'data'),
     Output('portfolio-value-graph', 'figure'),
     Output('total-return-metric', 'children'),
     Output('annualized-return-metric', 'children'),
     Output('sharpe-ratio-metric', 'children')
     ],
    [Input('portfolio-date-picker-range', 'start_date'),
     Input('portfolio-date-picker-range', 'end_date')])
def update_portfolio_and_graph(start_date, end_date):
    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if not start_date or not end_date:
        # Default date range if not set
        start_date=dt.now() - pd.Timedelta(days=365)
        end_date=dt.now()
    else:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    # Recalculate portfolio data
    stock_info = []
    for ticker in DEFAULT_TICKERS:
        ticker_info = yf.Ticker(ticker).info
        stock_info.append({
            'Company Name': ticker_info.get('longName', 'N/A'),
            'Ticker': ticker,
            'Market Cap': ticker_info.get('marketCap', 'N/A')
        })

    # Create DataFrame
    info_df = pd.DataFrame(stock_info)
    total_market_cap = info_df['Market Cap'].sum()

    info_df['Weight'] = round((info_df['Market Cap'] / total_market_cap)*100,2)

    # Assume a portfolio value of $10,000
    portfolio_value = 10000
    info_df['Investment'] = round(info_df['Weight'] * portfolio_value,2)
    # Update portfolio table data
    updated_table_data = info_df.to_dict('records')

    # Update portfolio graph
    if not start_date or not end_date:
        start_date = pd.to_datetime('2023-01-19')
        end_date = pd.to_datetime('2024-01-19')
    else:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        # Fetch and calculate portfolio value over time within the selected date range
    

    # Fetch historical data for the tickers
    historical_data = pd.DataFrame()
    for ticker in DEFAULT_TICKERS:
        stock_data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
        historical_data[ticker] = stock_data

    # Apply the portfolio weights to the historical data
    # Assuming market_cap_df has a 'Weight' column
    weights = info_df.set_index('Ticker')['Weight'].reindex(historical_data.columns).fillna(0)
    asset_quantity=round(weights*portfolio_value/100/historical_data.iloc[0]) 
    weighted_data = historical_data.multiply(asset_quantity, axis='columns')
    df_pv = weighted_data.sum(axis=1)

    # Create the graph
    updated_graph = go.Figure(data=[go.Scatter(x=df_pv.index, y=df_pv, mode='lines')],
                                layout={'title': 'Portfolio Value Over Time'})

    # Calculate portfolio metrics
    metrics = calculate_portfolio_metrics(df_pv)
    
    #return #updated_table_data,
    return updated_graph,metrics['Total Return'], metrics['Annualized Return'], metrics['Sharpe Ratio']


@app.callback(
    Output('stock-price-graph', 'figure'),
    [Input('stock-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')])
def update_stock_graph(selected_tickers, start_date, end_date):
    if start_date is not None and end_date is not None and selected_tickers:
        # Convert string dates to datetime objects
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Aggregate data for selected tickers
        df = pd.DataFrame()
        for ticker in selected_tickers:
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            df[ticker] = stock_data['Adj Close']

        # Create the plot
        fig = go.Figure()
        for ticker in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[ticker], mode='lines', name=ticker))

        fig.update_layout(title='Stock Prices Over Time', xaxis_title='Date', yaxis_title='Price')
        return fig
    return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
