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
from chart_tables import (
    create_table_visualization,
    create_indicator_summary,
    create_fibonacci_visualization,
    create_sentiment_gauge,
    create_news_summary_table
)
from stock_predictions import display_stock_opportunities
from trading_analytics import display_price_targets

# Load environment variables
ALPHA_VANTAGE_API_KEY = 'FCUWUJUPQYQV47ZG'

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
            df.columns = ['1. open', '2. high', '3. low', '4. close', '5. volume']
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df.index = pd.to_datetime(df.index)
            for col in df.columns:
                df[col] = df[col].astype(float)
            return df
        else:
            error_message = data.get('Note', data.get('Error Message', 'Unknown error'))
            if 'Note' in data:
                st.warning("API call frequency limit reached. Please wait a minute before trying again.")
            else:
                st.error(f"Error fetching data: {error_message}")
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
    Enhanced analysis including trend lines, signals, and news
    """
    # Get news analysis
    news_data = get_news_analysis(company_name)
    
    # Convert PIL Image to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Pattern Analysis Results
    analysis_results = []
    signals = []
    
    # Get advanced technical analysis
    advanced_analysis = get_advanced_analysis(df)
    
    # Get chart configuration
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
    
    # Get market sentiment
    market_sentiment = news_data['company_sentiment'] if news_data['company_sentiment'] is not None else 0
    
    # Generate Buy/Sell Signals with Confidence Levels
    
    # RSI Signals
    if current_rsi < 30:
        signals.append(("STRONG BUY", "RSI indicates heavily oversold condition", 0.9))
        analysis_results.append("Strong buying opportunity detected: RSI below 30")
    elif current_rsi < 40:
        signals.append(("BUY", "RSI indicates oversold condition", 0.7))
    elif current_rsi > 70:
        signals.append(("STRONG SELL", "RSI indicates heavily overbought condition", 0.9))
        analysis_results.append("Strong selling signal: RSI above 70")
    elif current_rsi > 60:
        signals.append(("SELL", "RSI indicates overbought condition", 0.7))
    
    # MACD Signals
    if macd_hist.iloc[-1] > 0 and macd_hist.iloc[-2] < 0:
        signals.append(("BUY", "MACD bullish crossover", 0.8))
        analysis_results.append("Bullish MACD crossover detected")
    elif macd_hist.iloc[-1] < 0 and macd_hist.iloc[-2] > 0:
        signals.append(("SELL", "MACD bearish crossover", 0.8))
        analysis_results.append("Bearish MACD crossover detected")
    
    # Volume Signals
    if volume_ratio > 2.0 and df['close'].iloc[-1] > df['close'].iloc[-2]:
        signals.append(("BUY", "High volume breakout", 0.85))
        analysis_results.append("Strong volume breakout detected")
    elif volume_ratio > 2.0 and df['close'].iloc[-1] < df['close'].iloc[-2]:
        signals.append(("SELL", "High volume breakdown", 0.85))
        analysis_results.append("High volume selling pressure detected")
    
    # Trend Analysis
    if advanced_analysis['current_indicators']['adx'] > 25:
        trend_strength = "Strong"
        if df['close'].iloc[-1] > df['close'].iloc[-5]:
            signals.append(("BUY", f"{trend_strength} uptrend detected", 0.75))
        else:
            signals.append(("SELL", f"{trend_strength} downtrend detected", 0.75))
    
    # News Sentiment Impact
    if market_sentiment > 0.3:
        signals.append(("BUY", "Positive news sentiment", 0.6))
    elif market_sentiment < -0.3:
        signals.append(("SELL", "Negative news sentiment", 0.6))
    
    # Sort signals by confidence level
    signals.sort(key=lambda x: x[2], reverse=True)
    
    # Prepare final analysis summary
    if signals:
        top_signal = signals[0]
        if top_signal[0] in ["STRONG BUY", "BUY"]:
            analysis_results.insert(0, f"🟢 Primary Signal: {top_signal[0]} - {top_signal[1]} (Confidence: {top_signal[2]*100:.0f}%)")
        else:
            analysis_results.insert(0, f"🔴 Primary Signal: {top_signal[0]} - {top_signal[1]} (Confidence: {top_signal[2]*100:.0f}%)")
    
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
        'signals': signals,
        'fibonacci_levels': advanced_analysis['fibonacci_levels'],
        'ichimoku_cloud': advanced_analysis['ichimoku_cloud'],
        'news_data': news_data,
        'chart_config': chart_config
    }

def main():
    st.title("MarketAnalyzerX")
    
    # Add tabs for different functionalities
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Pattern Analysis", 
        "Market Opportunities", 
        "Technical Screener",
        "Portfolio Analysis",
        "Learning Center"
    ])
    
    with tab1:
        st.write("Upload a stock chart and select the stock for pattern analysis")
        
        
        
        # Add sector filter
        selected_sector = st.selectbox(
            "Filter by Sector (Optional)",
            ["All Sectors", "BANKING", "IT", "PHARMA", "AUTO", "CONSUMER"],
            key="pattern_sector"
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
            available_stocks,
            key="pattern_stock"
        )
        
        if uploaded_file and selected_stock_name:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Stock Chart", use_column_width=True)
            
            # Get the stock symbol
            symbol = get_stock_info(selected_stock_name)
            
            if symbol:
                if st.button("Analyze Pattern", key="pattern_analyze"):
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
                            st.subheader("Trading Signals & Analysis")
                            col1, col2 = st.columns([2, 1])

                            with col1:
                                for result in analysis_result['analysis']:
                                    if result.startswith('🟢') or result.startswith('🔴'):
                                        st.markdown(f"### {result}")
                                    else:
                                        st.write(result)

                            with col2:
                                # Display a summary box of signals
                                st.markdown("""
                                <style>
                                .signal-box {
                                    padding: 10px;
                                    border-radius: 5px;
                                    margin: 5px 0;
                                }
                                .buy {background-color: rgba(46, 204, 113, 0.2)}
                                .sell {background-color: rgba(231, 76, 60, 0.2)}
                                </style>
                                """, unsafe_allow_html=True)
                                
                                for signal, reason, confidence in analysis_result['signals'][:3]:
                                    color_class = "buy" if "BUY" in signal else "sell"
                                    st.markdown(f"""
                                    <div class="signal-box {color_class}">
                                    <strong>{signal}</strong><br>
                                    {reason}<br>
                                    Confidence: {confidence*100:.0f}%
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Display enhanced chart with all indicators
                            st.plotly_chart(analysis_result['chart'])
                            
                            # Display technical indicators
                            st.subheader("Technical Indicators")
                            indicators_fig = create_indicator_summary(analysis_result['technical_indicators'])
                            st.plotly_chart(indicators_fig)
                            
                            # Add Fibonacci visualization
                            st.subheader("Fibonacci Retracement Levels")
                            fib_fig = create_fibonacci_visualization(analysis_result['fibonacci_levels'])
                            st.plotly_chart(fib_fig)
                            
                            # Add sentiment gauge
                            st.subheader("Market Sentiment")
                            sentiment_fig = create_sentiment_gauge(analysis_result['technical_indicators']['News Sentiment'])
                            st.plotly_chart(sentiment_fig)
                            
                            # Update news display
                            st.subheader("Recent News")
                            if analysis_result['news_data']['recent_articles']:
                                for article in analysis_result['news_data']['recent_articles']:
                                    with st.expander(f"{article['title']} (Sentiment: {article['sentiment']:.2f})"):
                                        st.write(f"Source: {article['source']}")
                                        if 'description' in article:
                                            st.write(article['description'])
                                        if 'url' in article:
                                            st.write(f"[Read more]({article['url']})")
                            else:
                                st.info("No recent news found for this stock")
                            
                            # Add market news if available
                            if analysis_result['news_data'].get('market_news'):
                                st.subheader("Market News")
                                for news in analysis_result['news_data']['market_news']:
                                    with st.expander(news['title']):
                                        st.write(f"Source: {news['source']}")
                                        if 'description' in news:
                                            st.write(news['description'])
                                        if 'url' in news:
                                            st.write(f"[Read more]({news['url']})")
                            
                            # Display basic statistics
                            st.subheader("Basic Statistics")
                            st.write({
                                "Latest Close": f"₹{df['close'].iloc[0]:.2f}",
                                "50-day Average": f"₹{df['close'].head(50).mean():.2f}",
                                "Trading Volume": f"{int(df['volume'].iloc[0]):,}"
                            })
                            
                            # Add Price Targets
                            display_price_targets(df)
            else:
                st.error(f"Could not find symbol for {selected_stock_name}")
        
    with tab2:
        display_stock_opportunities()
        
    with tab3:
        st.title("Technical Stock Screener")
        col1, col2 = st.columns(2)
        
        with col1:
            sector = st.selectbox(
                "Select Sector",
                ["All Sectors", "BANKING", "IT", "PHARMA", "AUTO", "CONSUMER"]
            )
            rsi_range = st.slider(
                "RSI Range",
                0, 100, (30, 70)
            )
            
        with col2:
            volume_filter = st.selectbox(
                "Volume Filter",
                ["Above Average", "High Volume", "Very High Volume", "Any"]
            )
            trend_filter = st.selectbox(
                "Trend Filter",
                ["Uptrend", "Downtrend", "Sideways", "Any"]
            )
        
        # Price Range Filter
        price_range = st.slider(
            "Price Range (₹)",
            0, 10000, (100, 5000)
        )
        
        # Pattern Selection
        patterns = st.multiselect(
            "Select Patterns to Screen",
            ["Double Bottom", "Double Top", "Head and Shoulders", 
             "Inverse H&S", "Bull Flag", "Bear Flag"],
            default=["Double Bottom", "Bull Flag"]
        )
        
        if st.button("Run Technical Screen"):
            with st.spinner("Screening stocks..."):
                # Import and use the screen_stocks function
                from technical_screener import screen_stocks
                results = screen_stocks(
                    sector, rsi_range, volume_filter, 
                    trend_filter, price_range, patterns
                )
                if results is not None and not results.empty:
                    st.success("Screening Complete!")
                    st.dataframe(results)
                else:
                    st.info("No stocks matched your screening criteria.")
    
    with tab4:
        st.title("Portfolio Analysis")
        
        # Portfolio Input Section
        with st.expander("Add Stock to Portfolio"):
            col1, col2, col3 = st.columns(3)
            with col1:
                stock_symbol = st.selectbox(
                    "Select Stock",
                    get_all_stocks()
                )
            with col2:
                quantity = st.number_input("Quantity", min_value=1, value=1)
            with col3:
                buy_price = st.number_input("Buy Price (₹)", min_value=0.0, value=0.0)
                
            if st.button("Add to Portfolio"):
                # Initialize portfolio in session state if it doesn't exist
                if 'portfolio' not in st.session_state:
                    st.session_state.portfolio = {}
                
                # Add stock to portfolio
                st.session_state.portfolio[stock_symbol] = {
                    'quantity': quantity,
                    'buy_price': buy_price
                }
                st.success(f"Added {stock_symbol} to portfolio!")
        
        # Portfolio Analysis Section
        if 'portfolio' in st.session_state and st.session_state.portfolio:
            st.subheader("Current Portfolio")
            
            portfolio_data = []
            total_investment = 0
            current_value = 0
            
            for symbol, details in st.session_state.portfolio.items():
                df = fetch_stock_data(get_stock_info(symbol))
                if df is not None:
                    current_price = df['close'].iloc[-1]
                    investment = details['quantity'] * details['buy_price']
                    value = details['quantity'] * current_price
                    gain_loss = value - investment
                    gain_loss_pct = (gain_loss / investment) * 100
                    
                    portfolio_data.append({
                        'Stock': symbol,
                        'Quantity': details['quantity'],
                        'Buy Price': f"₹{details['buy_price']:,.2f}",
                        'Current Price': f"₹{current_price:,.2f}",
                        'Investment': f"₹{investment:,.2f}",
                        'Current Value': f"₹{value:,.2f}",
                        'Gain/Loss': f"₹{gain_loss:,.2f}",
                        'Return %': f"{gain_loss_pct:,.2f}%"
                    })
                    
                    total_investment += investment
                    current_value += value
            
            if portfolio_data:
                df_portfolio = pd.DataFrame(portfolio_data)
                st.dataframe(df_portfolio)
                
                # Portfolio Summary
                total_gain_loss = current_value - total_investment
                total_return = (total_gain_loss / total_investment) * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Investment", f"₹{total_investment:,.2f}")
                with col2:
                    st.metric("Current Value", f"₹{current_value:,.2f}")
                with col3:
                    st.metric("Overall Return", f"{total_return:,.2f}%")
    
    with tab5:
        st.title("Stock Market Learning Center")
        
        # Create three main sections
        learning_section = st.radio(
            "Select Learning Section",
            ["Trading Tutorials", "Market Glossary", "Paper Trading Simulator"]
        )
        
        if learning_section == "Trading Tutorials":
            st.subheader("Stock Trading Tutorials")
            
            # Tutorial levels
            level = st.selectbox(
                "Select Your Level",
                ["Beginner", "Intermediate", "Advanced"]
            )
            
            # Tutorial content based on level
            if level == "Beginner":
                topics = {
                    "Introduction to Stock Markets": {
                        "content": """
                        ### What is the Stock Market?
                        The stock market is a place where shares of publicly traded companies are bought and sold.
                        
                        ### Key Concepts:
                        - **Stocks**: Represent ownership in a company
                        - **Exchange**: Platform where stocks are traded
                        - **Market Index**: Measures the performance of a group of stocks
                        
                        ### Basic Terms:
                        1. Bull Market: Market is rising
                        2. Bear Market: Market is falling
                        3. Dividend: Company profits paid to shareholders
                        """,
                        "video_url": "https://youtube.com/..."
                    },
                    "Basic Technical Analysis": {
                        "content": """
                        ### Understanding Charts
                        Learn to read different types of stock charts and basic patterns.
                        
                        ### Common Indicators:
                        - Moving Averages
                        - Volume Analysis
                        - Support and Resistance
                        """,
                        "video_url": "https://youtube.com/..."
                    }
                }
            
            elif level == "Intermediate":
                topics = {
                    "Advanced Chart Patterns": {
                        "content": """
                        ### Popular Trading Patterns
                        - Head and Shoulders
                        - Double Top/Bottom
                        - Triangle Patterns
                        
                        ### Using Multiple Timeframes
                        Understanding different time horizons for better analysis.
                        """,
                        "video_url": "https://youtube.com/..."
                    }
                }
            
            else:  # Advanced
                topics = {
                    "Advanced Trading Strategies": {
                        "content": """
                        ### Complex Trading Strategies
                        - Options Trading
                        - Risk Management
                        - Portfolio Optimization
                        
                        ### Market Psychology
                        Understanding market sentiment and behavioral finance.
                        """,
                        "video_url": "https://youtube.com/..."
                    }
                }
            
            # Display topics
            for topic, data in topics.items():
                with st.expander(topic):
                    st.markdown(data["content"])
                    st.write("📺 [Watch Video Tutorial](" + data["video_url"] + ")")
        
        elif learning_section == "Market Glossary":
            st.subheader("Stock Market Glossary")
            
            # Search functionality
            search_term = st.text_input("Search Terms", "")
            
            # Glossary dictionary
            glossary = {
                "Ask Price": "The lowest price a seller is willing to accept for a stock",
                "Bid Price": "The highest price a buyer is willing to pay for a stock",
                "Blue Chip": "Stock of a large, well-established company with stable earnings",
                "Dividend": "A portion of company's earnings paid to shareholders",
                "EPS (Earnings Per Share)": "Company's profit divided by outstanding shares",
                "MACD": "Moving Average Convergence Divergence - A technical indicator",
                "P/E Ratio": "Price-to-Earnings Ratio - Stock price divided by earnings per share",
                "RSI": "Relative Strength Index - Momentum indicator measuring speed of price changes",
                "Volume": "Number of shares traded during a specific period",
                "Yield": "Dividend expressed as a percentage of stock price"
            }
            
            # Filter terms based on search
            filtered_terms = {k: v for k, v in glossary.items() 
                            if search_term.lower() in k.lower() or 
                            search_term.lower() in v.lower()}
            
            # Display glossary
            for term, definition in filtered_terms.items():
                with st.expander(term):
                    st.write(definition)
        
        else:  # Paper Trading Simulator
            st.subheader("Stock Market Simulator Game")
            st.markdown("""
            Practice trading in a risk-free environment with simulated market conditions.
            The simulator runs a complete trading day (9:15 AM to 3:30 PM) in 30 seconds.
            """)
            
            # Import and run simulation without any real market data
            from trading_simulator import run_trading_simulation
            run_trading_simulation()

if __name__ == "__main__":
    main()
