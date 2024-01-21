import pandas as pd
import numpy as np
def calculate_portfolio_metrics(df_pv):
    df=pd.DataFrame(df_pv, columns=['Portfolio Value']).reset_index()
    # Calculate total return
    total_return = (df['Portfolio Value'].iloc[-1] - df['Portfolio Value'].iloc[0]) / df['Portfolio Value'].iloc[0]
    
    # Calculate annualized return
    annualized_return = ((1 + total_return) ** (365 / len(df.index)) - 1)
    
    # Calculate risk-adjusted return (e.g., Sharpe ratio)
    risk_free_rate = 0.03  # Replace with the appropriate risk-free rate
    excess_return = df['Portfolio Value'].pct_change() - risk_free_rate / 365
    sharpe_ratio = (excess_return.mean() / excess_return.std()) * np.sqrt(365)
    
    # Create a dictionary to store the metrics
    metrics = {
        'Total Return': round(total_return,4),
        'Annualized Return': round(annualized_return,4),
        'Sharpe Ratio': round(sharpe_ratio,4),
        # Add more metrics as needed
    }
    
    return metrics