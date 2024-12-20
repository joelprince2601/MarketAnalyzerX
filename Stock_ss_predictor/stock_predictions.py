import pandas as pd
import numpy as np
from ta.trend import ADXIndicator
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
import streamlit as st
from datetime import datetime, timedelta
import requests
import time

# Use the same API key as in stock_predictor.py
ALPHA_VANTAGE_API_KEY = 'CAT8NZ23VZXP62CE'

def fetch_stock_data_for_analysis(symbol, retry_days=5):
    """
    Fetch stock data using Alpha Vantage API with retry logic for previous days
    """
    base_url = 'https://www.alphavantage.co/query'
    
    for day_offset in range(retry_days):
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': 'compact',
                'apikey': ALPHA_VANTAGE_API_KEY,
                'datatype': 'json'
            }
            
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
                df.columns = ['1. open', '2. high', '3. low', '4. close', '5. volume']
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df.index = pd.to_datetime(df.index)
                
                if len(df) > 0:
                    for col in df.columns:
                        df[col] = df[col].astype(float)
                    
                    # If data is found, return it
                    return df
                
            elif 'Note' in data:
                # If we hit API limit, wait and try again
                time.sleep(60)
                continue
            
            # If no data found for current day, try previous day
            time.sleep(12)  # Small delay between retries
            
        except Exception as e:
            if day_offset == retry_days - 1:  # If this is our last retry
                st.warning(f"Could not fetch data for {symbol} after {retry_days} attempts")
            continue
    
    return None

def get_technical_signals(df):
    """Calculate technical indicators and generate signals"""
    # Calculate indicators
    df['RSI'] = RSIIndicator(close=df['Close']).rsi()
    df['OBV'] = OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume']).on_balance_volume()
    adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'])
    df['ADX'] = adx.adx()
    
    # Calculate moving averages
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    
    # Calculate MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Volume analysis
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
    
    return df

def calculate_score(stock_data):
    """Calculate a composite score for stock potential"""
    score = 0
    latest = stock_data.iloc[-1]
    
    # RSI signals (oversold opportunities)
    if 30 <= latest['RSI'] <= 40:
        score += 1
    elif latest['RSI'] < 30:
        score += 2
        
    # Trend strength
    if latest['ADX'] > 25:
        score += 1
    
    # MACD signals
    if latest['MACD'] > latest['Signal_Line']:
        score += 1
    
    # Volume confirmation
    if latest['Volume_Ratio'] > 1.5:
        score += 1
    
    # Moving average signals
    if latest['Close'] > latest['SMA20'] > latest['SMA50']:
        score += 2
    elif latest['Close'] > latest['SMA20']:
        score += 1
        
    # Price momentum
    returns = (stock_data['Close'].pct_change(5).iloc[-1]) * 100
    if returns > 2:
        score += 1
        
    return score

def get_promising_stocks(stock_list, min_score=4):
    """Identify promising stocks based on technical analysis"""
    promising_stocks = []
    
    with st.spinner('Analyzing market opportunities...'):
        progress_bar = st.progress(0)
        total_stocks = len(stock_list)
        
        # Convert stock_list to dictionary if it's not already
        stocks_dict = {}
        if isinstance(stock_list, list):
            stocks_dict = {name: name for name in stock_list}
        else:
            stocks_dict = stock_list
        
        for idx, (name, symbol) in enumerate(stocks_dict.items()):
            try:
                # Add delay to respect API limits
                if idx > 0 and idx % 5 == 0:
                    time.sleep(60)  # Wait for 60 seconds after every 5 requests
                
                # Get the symbol from indian_stocks module
                from indian_stocks import get_stock_info
                symbol = get_stock_info(name)
                
                if symbol:
                    # Fetch data with retry logic
                    df = fetch_stock_data_for_analysis(symbol)
                    
                    if df is not None and len(df) > 0:
                        # Calculate technical indicators
                        df = get_technical_signals(df)
                        
                        # Calculate potential score
                        score = calculate_score(df)
                        
                        if score >= min_score:
                            latest_price = df['Close'].iloc[-1]
                            change_pct = ((df['Close'].iloc[-1] / df['Close'].iloc[-5]) - 1) * 100
                            volume_ratio = df['Volume_Ratio'].iloc[-1]
                            latest_date = df.index[0].strftime('%Y-%m-%d')
                            
                            promising_stocks.append({
                                'Name': name,
                                'Symbol': symbol,
                                'Score': score,
                                'Price': latest_price,
                                'As of Date': latest_date,
                                '5-Day Return': f"{change_pct:.2f}%",
                                'RSI': df['RSI'].iloc[-1],
                                'Volume Ratio': volume_ratio,
                                'ADX': df['ADX'].iloc[-1]
                            })
                    
                progress_bar.progress((idx + 1) / total_stocks)
                
            except Exception as e:
                continue
        
        if not promising_stocks:
            st.warning("""
            No opportunities found in recent data. 
            This could be due to market closure or data availability. 
            Try again during market hours or adjust the filters.
            """)
                
    return pd.DataFrame(promising_stocks)

def display_stock_opportunities():
    """Display promising stock opportunities"""
    st.title("Market Opportunities Scanner")
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        min_score = st.slider("Minimum Opportunity Score", 1, 8, 4)
    with col2:
        sector_filter = st.selectbox(
            "Filter by Sector",
            ["All Sectors", "BANKING", "IT", "PHARMA", "AUTO", "CONSUMER"]
        )
    
    # Add API limit warning
    st.warning("""
    Note: Due to API limitations (5 calls per minute), the scanning process will be slower 
    and will pause periodically. Please be patient during the analysis.
    """)
    
    if st.button("Scan for Opportunities"):
        # Import stock list based on sector
        from indian_stocks import get_all_stocks, get_stocks_by_sector
        
        if sector_filter == "All Sectors":
            stocks = get_all_stocks()
        else:
            stocks = get_stocks_by_sector(sector_filter)
            if not stocks:
                st.warning(f"No stocks found in {sector_filter} sector. Showing all stocks.")
                stocks = get_all_stocks()
        
        # Get promising stocks
        results = get_promising_stocks(stocks, min_score)
        
        if len(results) > 0:
            st.subheader("Promising Stocks Found")
            
            # Display results in a sortable table
            st.dataframe(
                results.style.background_gradient(subset=['Score']),
                height=400
            )
            
            # Add detailed analysis for top stocks
            st.subheader("Top Opportunities Analysis")
            top_stocks = results.nlargest(3, 'Score')
            
            for _, stock in top_stocks.iterrows():
                with st.expander(f"{stock['Name']} (Score: {stock['Score']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Price", f"₹{stock['Price']:.2f}", stock['5-Day Return'])
                        st.metric("RSI", f"{stock['RSI']:.2f}")
                    with col2:
                        st.metric("Volume Ratio", f"{stock['Volume Ratio']:.2f}x")
                        st.metric("ADX", f"{stock['ADX']:.2f}")
                    
                    st.write("### Why This Stock?")
                    reasons = []
                    if stock['RSI'] < 40:
                        reasons.append("• Potentially oversold condition")
                    if stock['Volume Ratio'] > 1.5:
                        reasons.append("• Strong volume support")
                    if stock['ADX'] > 25:
                        reasons.append("• Strong trend detected")
                    
                    for reason in reasons:
                        st.write(reason)
        else:
            st.info("No stocks meeting the criteria found at this time. Try adjusting the filters.")

if __name__ == "__main__":
    display_stock_opportunities() 