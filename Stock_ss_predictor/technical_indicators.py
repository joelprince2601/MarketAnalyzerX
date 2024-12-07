import pandas as pd
import numpy as np
from ta.trend import MACD
from ta.momentum import RSIIndicator
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_macd_histogram(df):
    """
    Calculate MACD and its histogram
    """
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_histogram'] = macd.macd_diff()
    return df

def calculate_fibonacci_levels(df):
    """
    Calculate Fibonacci retracement levels
    """
    max_price = df['high'].max()
    min_price = df['low'].min()
    diff = max_price - min_price
    
    levels = {
        '0.0': min_price,
        '0.236': min_price + 0.236 * diff,
        '0.382': min_price + 0.382 * diff,
        '0.5': min_price + 0.5 * diff,
        '0.618': min_price + 0.618 * diff,
        '0.786': min_price + 0.786 * diff,
        '1.0': max_price
    }
    return levels

def calculate_ichimoku_cloud(df):
    """
    Calculate Ichimoku Cloud components
    """
    high_prices = df['high']
    low_prices = df['low']
    
    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
    period9_high = high_prices.rolling(window=9).max()
    period9_low = low_prices.rolling(window=9).min()
    df['tenkan_sen'] = (period9_high + period9_low) / 2
    
    # Kijun-sen (Base Line): (26-period high + 26-period low)/2
    period26_high = high_prices.rolling(window=26).max()
    period26_low = low_prices.rolling(window=26).min()
    df['kijun_sen'] = (period26_high + period26_low) / 2
    
    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    
    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2
    period52_high = high_prices.rolling(window=52).max()
    period52_low = low_prices.rolling(window=52).min()
    df['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)
    
    # Chikou Span (Lagging Span): Close shifted back 26 periods
    df['chikou_span'] = df['close'].shift(-26)
    
    return df

def calculate_adx(df, period=14):
    """
    Calculate Average Directional Index (ADX)
    """
    df['tr1'] = abs(df['high'] - df['low'])
    df['tr2'] = abs(df['high'] - df['close'].shift(1))
    df['tr3'] = abs(df['low'] - df['close'].shift(1))
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    df['dx'] = df['tr'].rolling(window=period).mean()
    df['adx'] = 100 * df['dx'].rolling(window=period).mean()
    
    return df

def calculate_obv(df):
    """
    Calculate On-Balance Volume (OBV)
    """
    df['daily_ret'] = df['close'].pct_change()
    df['direction'] = np.where(df['daily_ret'] > 0, 1, -1)
    df['direction'][df['daily_ret'] == 0] = 0
    df['obv'] = (df['volume'] * df['direction']).cumsum()
    
    return df

def plot_advanced_indicators(df):
    """
    Create a comprehensive plot with all advanced indicators
    """
    # Create figure with secondary y-axis
    fig = make_subplots(rows=4, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.05,
                       subplot_titles=('Price with Ichimoku Cloud', 
                                     'MACD Histogram',
                                     'ADX',
                                     'OBV'))

    # Plot candlestick
    fig.add_trace(go.Candlestick(x=df.index,
                                open=df['open'],
                                high=df['high'],
                                low=df['low'],
                                close=df['close'],
                                name='Price'),
                  row=1, col=1)

    # Plot Ichimoku Cloud
    fig.add_trace(go.Scatter(x=df.index, y=df['tenkan_sen'],
                            name='Tenkan-sen',
                            line=dict(color='blue')),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['kijun_sen'],
                            name='Kijun-sen',
                            line=dict(color='red')),
                  row=1, col=1)
    
    # Plot MACD Histogram
    fig.add_trace(go.Bar(x=df.index, y=df['macd_histogram'],
                        name='MACD Histogram'),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['macd'],
                            name='MACD',
                            line=dict(color='blue')),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['macd_signal'],
                            name='Signal',
                            line=dict(color='red')),
                  row=2, col=1)

    # Plot ADX
    fig.add_trace(go.Scatter(x=df.index, y=df['adx'],
                            name='ADX',
                            line=dict(color='purple')),
                  row=3, col=1)

    # Plot OBV
    fig.add_trace(go.Scatter(x=df.index, y=df['obv'],
                            name='OBV',
                            line=dict(color='green')),
                  row=4, col=1)

    # Update layout
    fig.update_layout(
        height=1200,
        title_text="Advanced Technical Analysis",
        showlegend=True,
        xaxis4_title="Date",
    )

    return fig

def get_advanced_analysis(df):
    """
    Main function to calculate and return all advanced indicators
    """
    # Calculate all indicators
    df = calculate_macd_histogram(df)
    fibonacci_levels = calculate_fibonacci_levels(df)
    df = calculate_ichimoku_cloud(df)
    df = calculate_adx(df)
    df = calculate_obv(df)
    
    # Generate the plot
    fig = plot_advanced_indicators(df)
    
    # Prepare analysis summary
    analysis = {
        'fibonacci_levels': fibonacci_levels,
        'current_indicators': {
            'macd': df['macd'].iloc[-1],
            'macd_histogram': df['macd_histogram'].iloc[-1],
            'adx': df['adx'].iloc[-1],
            'obv': df['obv'].iloc[-1]
        },
        'ichimoku_cloud': {
            'tenkan_sen': df['tenkan_sen'].iloc[-1],
            'kijun_sen': df['kijun_sen'].iloc[-1],
            'senkou_span_a': df['senkou_span_a'].iloc[-1],
            'senkou_span_b': df['senkou_span_b'].iloc[-1]
        },
        'chart': fig
    }
    
    return analysis 