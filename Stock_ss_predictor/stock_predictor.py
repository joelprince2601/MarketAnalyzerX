import requests
import pandas as pd
from datetime import datetime
import os
import time
import streamlit as st
from PIL import Image
import io
import cv2
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import plotly.graph_objects as go
from scipy.signal import find_peaks
from technical_indicators import get_advanced_analysis
from news_analyzer import get_news_analysis
from indian_stocks import get_all_stocks, get_stock_info, get_stocks_by_sector
from chart_visualizations import create_enhanced_chart, render_chart_controls

# Load environment variables

ALPHA_VANTAGE_API_KEY = 'CJN7LBTPJOGTCIX5'

def fetch_stock_data(symbol):
    """
    Fetch historical stock data from Alpha Vantage API
    """
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': 'compact',
        'apikey': ALPHA_VANTAGE_API_KEY,
        'datatype': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df.index = pd.to_datetime(df.index)
            for col in df.columns:
                df[col] = df[col].astype(float)
            return df
        else:
            error_message = data.get('Note', data.get('Error Message', 'Unknown error'))
            st.error(f"Error fetching data: {error_message}")
            if 'Note' in data:
                st.warning("API call frequency limit reached. Please wait a minute before trying again.")
            return None
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def detect_trend_lines(img_gray):
    """
    Detect trend lines from the chart image using computer vision
    """
    # Edge detection
    edges = cv2.Canny(img_gray, 50, 150, apertureSize=3)
    
    # Detect lines using HoughLinesP
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
    
    trend_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            
            # Filter lines based on angle (trend lines are usually between 20-70 degrees)
            if 20 < abs(angle) < 70:
                trend_lines.append(((x1, y1), (x2, y2), angle))
    
    return trend_lines

def analyze_chart(image, df, symbol, company_name):
    """
    Enhanced analysis including trend lines, real-time signals, and news
    """
    # Get news analysis
    news_data = get_news_analysis(company_name)
    
    # Convert PIL Image to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Pattern Analysis Results
    analysis_results = []
    
    # Detect trend lines
    trend_lines = detect_trend_lines(img_gray)
    
    # Get advanced technical analysis
    advanced_analysis = get_advanced_analysis(df)
    
    # Get chart configuration from sidebar
    chart_config = render_chart_controls()
    
    # Create enhanced chart
    fig = create_enhanced_chart(df, chart_config)
    
    # Technical Analysis
    rsi = RSIIndicator(close=df['close'], window=14)
    current_rsi = rsi.rsi().iloc[-1]
    
    # Calculate MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - signal
    
    # Volume Analysis
    avg_volume = df['volume'].mean()
    current_volume = df['volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume
    
    # Get market sentiment from news
    market_sentiment = news_data['company_sentiment'] if news_data['company_sentiment'] is not None else 0
    
    # Generate Buy/Sell Signals
    signals = []
    
    # RSI Signals
    if current_rsi < 30:
        signals.append(("BUY", "RSI oversold condition"))
    elif current_rsi > 70:
        signals.append(("SELL", "RSI overbought condition"))
    
    # MACD Signals
    if macd_hist.iloc[-1] > 0 and macd_hist.iloc[-2] < 0:
        signals.append(("BUY", "MACD crossover"))
    elif macd_hist.iloc[-1] < 0 and macd_hist.iloc[-2] > 0:
        signals.append(("SELL", "MACD crossover"))
    
    # Volume Signals
    if volume_ratio > 1.5 and df['close'].iloc[-1] > df['close'].iloc[-2]:
        signals.append(("BUY", "High volume breakout"))
    elif volume_ratio > 1.5 and df['close'].iloc[-1] < df['close'].iloc[-2]:
        signals.append(("SELL", "High volume breakdown"))
    
    # Add news-based signals
    if market_sentiment > 0.2:
        signals.append(("BUY", "Positive news sentiment"))
    elif market_sentiment < -0.2:
        signals.append(("SELL", "Negative news sentiment"))
    
    # Add advanced indicator signals
    if advanced_analysis['current_indicators']['macd_histogram'] > 0:
        signals.append(("BUY", "MACD Histogram positive"))
    elif advanced_analysis['current_indicators']['macd_histogram'] < 0:
        signals.append(("SELL", "MACD Histogram negative"))
    
    if advanced_analysis['current_indicators']['adx'] > 25:
        signals.append(("INFO", "Strong trend detected (ADX > 25)"))
    
    return {
        'analysis': analysis_results,
        'chart': fig,
        'technical_indicators': {
            'RSI': round(current_rsi, 2),
            'MACD': round(macd.iloc[-1], 2),
            'Volume Ratio': round(volume_ratio, 2),
            'News Sentiment': round(market_sentiment, 2),
            'ADX': round(advanced_analysis['current_indicators']['adx'], 2),
            'OBV': int(advanced_analysis['current_indicators']['obv'])
        },
        'fibonacci_levels': advanced_analysis['fibonacci_levels'],
        'ichimoku_cloud': advanced_analysis['ichimoku_cloud'],
        'signals': signals,
        'news_data': news_data,
        'chart_config': chart_config
    }

def main():
    st.title("MarketAnalyzerX")
    st.write("Upload a stock chart and select the stock for pattern analysis")

    # Add information about API limits
    st.info("""
    Note: This application uses Alpha Vantage API and NewsAPI with following limits:
    - Alpha Vantage: 5 API calls per minute, 500 API calls per day
    - NewsAPI: 100 requests per day
    Please wait a minute between analyses if you receive a frequency limit error.
    """)

    # Add sector filter
    selected_sector = st.selectbox(
        "Filter by Sector (Optional)",
        ["All Sectors", "BANKING", "IT", "PHARMA", "AUTO", "CONSUMER"]
    )

    # Get stock list based on sector
    if selected_sector == "All Sectors":
        available_stocks = get_all_stocks()
    else:
        available_stocks = get_stocks_by_sector(selected_sector)
        if not available_stocks:
            st.warning(f"No stocks found in {selected_sector} sector. Showing all stocks.")
            available_stocks = get_all_stocks()

    # File uploader
    uploaded_file = st.file_uploader("Choose a stock chart image", type=['png', 'jpg', 'jpeg'])
    
    # Stock selector with sector filtering
    selected_stock_name = st.selectbox(
        "Select the stock",
        available_stocks
    )
    
    if uploaded_file and selected_stock_name:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Stock Chart", use_column_width=True)
        
        # Get the stock symbol
        symbol = get_stock_info(selected_stock_name)
        
        if symbol:
            if st.button("Analyze Pattern"):
                with st.spinner("Analyzing chart, fetching data, and gathering news..."):
                    # Fetch historical data
                    df = fetch_stock_data(symbol)
                    
                    if df is not None:
                        st.success("Data fetched successfully!")
                        
                        # Display recent stock data
                        st.subheader("Recent Stock Data")
                        st.dataframe(df.head())
                        
                        # Pass symbol and company name to analyze_chart
                        analysis_result = analyze_chart(image, df, symbol, selected_stock_name)
                        
                        # Display pattern analysis results
                        st.subheader("Pattern Analysis Results")
                        for result in analysis_result['analysis']:
                            st.write(result)
                        
                        # Display enhanced chart with all indicators
                        st.plotly_chart(analysis_result['chart'])
                        
                        # Display technical indicators
                        st.subheader("Technical Indicators")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("RSI", f"{analysis_result['technical_indicators']['RSI']}")
                            st.metric("ADX", f"{analysis_result['technical_indicators']['ADX']}")
                        with col2:
                            st.metric("MACD", f"{analysis_result['technical_indicators']['MACD']}")
                            st.metric("OBV", f"{analysis_result['technical_indicators']['OBV']:,}")
                        with col3:
                            st.metric("Volume Ratio", f"{analysis_result['technical_indicators']['Volume Ratio']}")
                            st.metric("News Sentiment", f"{analysis_result['technical_indicators']['News Sentiment']:.2f}")
                        
                        # Display Fibonacci Levels
                        st.subheader("Fibonacci Retracement Levels")
                        fib_df = pd.DataFrame.from_dict(analysis_result['fibonacci_levels'], 
                                                      orient='index', 
                                                      columns=['Price Level'])
                        st.dataframe(fib_df)
                        
                        # Display Ichimoku Cloud Values
                        st.subheader("Ichimoku Cloud Indicators")
                        ichimoku_df = pd.DataFrame.from_dict(analysis_result['ichimoku_cloud'], 
                                                           orient='index', 
                                                           columns=['Value'])
                        st.dataframe(ichimoku_df)
                        
                        # Display News Analysis
                        st.subheader("News Analysis")
                        st.write("News Summary:")
                        st.write(analysis_result['news_data']['news_summary'])
                        
                        # Display recent articles
                        st.subheader("Recent Company News")
                        for article in analysis_result['news_data']['recent_articles'][:5]:
                            with st.expander(f"{article['title']} ({article['source']})"):
                                st.write(article['description'])
                                st.write(f"Sentiment: {'Positive' if article['sentiment'] > 0 else 'Negative' if article['sentiment'] < 0 else 'Neutral'}")
                                st.write(f"[Read more]({article['url']})")
                        
                        # Display market news
                        st.subheader("General Market News")
                        for article in analysis_result['news_data']['market_news']:
                            with st.expander(f"{article['title']} ({article['source']})"):
                                st.write(article['description'])
                                st.write(f"[Read more]({article['url']})")
                        
                        # Display Buy/Sell Signals
                        st.subheader("Trading Signals")
                        signals = analysis_result['signals']
                        
                        for signal, reason in signals:
                            if signal == "BUY":
                                st.success(f"🔵 BUY Signal: {reason}")
                            elif signal == "SELL":
                                st.error(f"🔴 SELL Signal: {reason}")
                            else:
                                st.info(f"ℹ️ {reason}")
                        
                        # Display basic statistics
                        st.subheader("Basic Statistics")
                        st.write({
                            "Latest Close": f"₹{df['close'].iloc[0]:.2f}",
                            "50-day Average": f"₹{df['close'].head(50).mean():.2f}",
                            "Trading Volume": f"{int(df['volume'].iloc[0]):,}"
                        })
        else:
            st.error(f"Could not find symbol for {selected_stock_name}")

if __name__ == "__main__":
    main() 
