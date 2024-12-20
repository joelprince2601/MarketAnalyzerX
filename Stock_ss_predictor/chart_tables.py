import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_table_visualization(df, title="Data Table"):
    """
    Create an interactive table visualization using plotly
    """
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color='#1f77b4',
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color='lavender',
            align='left',
            font=dict(color='darkslate gray', size=11)
        )
    )])
    
    fig.update_layout(
        title=title,
        height=400,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return fig

def create_indicator_summary(indicators_dict):
    """
    Create a visual summary of technical indicators with additional information
    """
    fig = make_subplots(
        rows=3, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}]],
        vertical_spacing=0.3,
        horizontal_spacing=0.2
    )
    
    # Extend the indicators dictionary with additional metrics
    extended_indicators = {
        'RSI': {
            'value': indicators_dict['RSI'],
            'status': 'Overbought' if indicators_dict['RSI'] > 70 else 'Oversold' if indicators_dict['RSI'] < 30 else 'Neutral',
            'color': '#e74c3c' if indicators_dict['RSI'] > 70 else '#2ecc71' if indicators_dict['RSI'] < 30 else '#f1c40f'
        },
        'MACD': {
            'value': indicators_dict['MACD'],
            'status': 'Bullish' if indicators_dict['MACD'] > 0 else 'Bearish',
            'color': '#2ecc71' if indicators_dict['MACD'] > 0 else '#e74c3c'
        },
        'Volume Ratio': {
            'value': indicators_dict['Volume Ratio'],
            'status': 'High' if indicators_dict['Volume Ratio'] > 1.5 else 'Low' if indicators_dict['Volume Ratio'] < 0.5 else 'Normal',
            'color': '#3498db'
        },
        'ADX': {
            'value': indicators_dict['ADX'],
            'status': 'Strong Trend' if indicators_dict['ADX'] > 25 else 'Weak Trend',
            'color': '#9b59b6'
        },
        'OBV': {
            'value': indicators_dict['OBV'],
            'status': 'Accumulation' if indicators_dict['OBV'] > 0 else 'Distribution',
            'color': '#1abc9c'
        },
        'News Sentiment': {
            'value': indicators_dict['News Sentiment'],
            'status': 'Positive' if indicators_dict['News Sentiment'] > 0 else 'Negative',
            'color': '#f1c40f'
        }
    }
    
    positions = [(1,1), (1,2), (2,1), (2,2), (3,1), (3,2)]
    
    for (key, data), position in zip(extended_indicators.items(), positions):
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=data['value'] if isinstance(data['value'], (int, float)) else 0,
                title={
                    "text": f"{key}<br><span style='font-size:0.8em;color:{data['color']}'>{data['status']}</span>",
                    "font": {"size": 16}
                },
                delta={
                    'reference': 0,
                    'relative': True,
                    'position': "bottom"
                },
                number={
                    'font': {'size': 20, 'color': data['color']},
                    'prefix': "₹" if key == "OBV" else "",
                    'suffix': "%" if key in ["RSI", "Volume Ratio"] else ""
                },
            ),
            row=position[0], col=position[1]
        )
    
    # Add interpretation text
    interpretations = {
        'RSI': {
            '>70': 'Overbought - Consider Selling',
            '<30': 'Oversold - Consider Buying',
            'else': 'Neutral - Hold Position'
        },
        'MACD': {
            '>0': 'Bullish Momentum',
            '<0': 'Bearish Momentum'
        },
        'ADX': {
            '>25': 'Strong Trend Present',
            '<25': 'No Strong Trend'
        }
    }
    
    fig.update_layout(
        height=800,  # Increased height for additional information
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[
            dict(
                text="Trend Strength",
                x=0.5,
                y=-0.1,
                showarrow=False,
                font=dict(size=14),
                xref="paper",
                yref="paper"
            ),
            dict(
                text="Volume Analysis",
                x=0.5,
                y=-0.15,
                showarrow=False,
                font=dict(size=14),
                xref="paper",
                yref="paper"
            )
        ]
    )
    
    return fig

def create_fibonacci_visualization(levels):
    """
    Create a visual representation of Fibonacci levels
    """
    levels_df = pd.DataFrame(list(levels.items()), columns=['Level', 'Price'])
    
    fig = go.Figure(data=[
        go.Scatter(
            x=levels_df['Level'],
            y=levels_df['Price'],
            mode='lines+markers+text',
            text=levels_df['Price'].round(2),
            textposition="top center",
            line=dict(color='#8e44ad', width=2),
            marker=dict(size=8, symbol='diamond')
        )
    ])
    
    fig.update_layout(
        title='Fibonacci Retracement Levels',
        xaxis_title='Fibonacci Level',
        yaxis_title='Price',
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    return fig

def create_sentiment_gauge(sentiment_score):
    """
    Create an enhanced gauge chart for sentiment visualization with professional spacing
    """
    # Normalize sentiment score to percentage (0-100 scale)
    normalized_score = (sentiment_score + 1) * 50

    fig = go.Figure()

    # Add the main gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=normalized_score,
        domain={'x': [0, 1], 'y': [0.25, 1]},  # Adjusted domain to prevent overlap
        title={
            'text': "Market Sentiment",
            'font': {'size': 24}
        },
        delta={
            'reference': 50,
            'position': "bottom",
            'relative': True
        },
        number={
            'font': {'size': 30},
            'suffix': '%'
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'ticktext': ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'],
                'tickvals': [10, 30, 50, 70, 90],
                'tickfont': {'size': 12}
            },
            'bar': {'thickness': 0.75},
            'borderwidth': 2,
            'steps': [
                {'range': [0, 20], 'color': '#ff4444'},
                {'range': [20, 40], 'color': '#ffa07a'},
                {'range': [40, 60], 'color': '#ffe66d'},
                {'range': [60, 80], 'color': '#90ee90'},
                {'range': [80, 100], 'color': '#32cd32'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': normalized_score
            }
        }
    ))

    # Add sentiment description
    sentiment_text = "Very Negative"
    if normalized_score > 80:
        sentiment_text = "Very Positive"
    elif normalized_score > 60:
        sentiment_text = "Positive"
    elif normalized_score > 40:
        sentiment_text = "Neutral"
    elif normalized_score > 20:
        sentiment_text = "Negative"

    # Add interpretation text with better spacing
    fig.update_layout(
        height=500,  # Increased height
        margin=dict(l=20, r=20, t=80, b=80),  # Increased margins
        annotations=[
            dict(
                text=f"Current Market Sentiment: {sentiment_text}",
                x=0.5,
                y=0.15,  # Adjusted position
                showarrow=False,
                font=dict(size=16, color='#2c3e50'),
                align='center'
            ),
            dict(
                text=f"Sentiment Score: {sentiment_score:.2f}",
                x=0.5,
                y=0.08,  # Adjusted position
                showarrow=False,
                font=dict(size=14, color='#7f8c8d'),
                align='center'
            ),
            dict(
                text="Market Interpretation",
                x=0.5,
                y=0,  # Bottom position
                showarrow=False,
                font=dict(size=12, color='#95a5a6'),
                align='center'
            )
        ]
    )

    return fig

def create_news_summary_table(news_data):
    """
    Create a visual summary of news articles
    """
    if not news_data['recent_articles']:
        return None
        
    news_df = pd.DataFrame(news_data['recent_articles'])
    news_df['sentiment_color'] = news_df['sentiment'].apply(
        lambda x: '#2ecc71' if x > 0.1 else '#e74c3c' if x < -0.1 else '#f1c40f'
    )
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Title', 'Source', 'Sentiment'],
            fill_color='#1f77b4',
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[
                news_df['title'],
                news_df['source'],
                news_df['sentiment'].round(3)
            ],
            fill_color=[['white']*len(news_df), ['white']*len(news_df), news_df['sentiment_color']],
            align='left',
            font=dict(color='darkslate gray', size=11)
        )
    )])
    
    fig.update_layout(
        title='Recent News Analysis',
        height=400,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return fig 