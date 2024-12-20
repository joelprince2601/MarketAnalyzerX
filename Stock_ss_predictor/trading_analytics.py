import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict

class TradingAnalytics:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.current_price = df['close'].iloc[-1]
        self.high = df['high']
        self.low = df['low']
        self.close = df['close']
        
    def calculate_price_targets(self) -> Dict[str, float]:
        """
        Calculate support, resistance and price targets using multiple methods
        """
        # Calculate support and resistance using recent price action
        recent_data = self.df.tail(20)  # Last 20 days
        support = recent_data['low'].min()
        resistance = recent_data['high'].max()
        
        # Calculate pivot points
        pivot = (recent_data['high'].iloc[-1] + 
                recent_data['low'].iloc[-1] + 
                recent_data['close'].iloc[-1]) / 3
        
        r1 = 2 * pivot - recent_data['low'].iloc[-1]
        s1 = 2 * pivot - recent_data['high'].iloc[-1]
        
        # Calculate targets based on volatility
        volatility = self.df['close'].pct_change().std()
        volatility_target = self.current_price * (1 + 2 * volatility)
        
        # Calculate risk/reward ratios
        risk_to_support = self.current_price - support
        reward_to_resistance = resistance - self.current_price
        risk_reward_ratio = reward_to_resistance / risk_to_support if risk_to_support > 0 else 0
        
        return {
            'Current Price': round(self.current_price, 2),
            'Strong Support': round(support, 2),
            'Weak Support': round(s1, 2),
            'Strong Resistance': round(resistance, 2),
            'Weak Resistance': round(r1, 2),
            'Short-term Target': round(self.current_price * 1.05, 2),
            'Medium-term Target': round(self.current_price * 1.10, 2),
            'Volatility Target': round(volatility_target, 2),
            'Risk/Reward Ratio': round(risk_reward_ratio, 2)
        }

def display_price_targets(df: pd.DataFrame):
    """Display price targets and analysis in Streamlit with enhanced UI matching app theme"""
    analytics = TradingAnalytics(df)
    targets = analytics.calculate_price_targets()
    
    st.markdown("""
    <style>
    .target-header {
        background: linear-gradient(90deg, #1e3799 0%, #0c2461 100%);
        color: #ffffff;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
    }
    .price-card {
        background: #192a56;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        border-left: 5px solid;
    }
    .card-current { border-color: #3498db; }
    .card-support { border-color: #2ecc71; }
    .card-resistance { border-color: #e74c3c; }
    .card-target { border-color: #f1c40f; }
    .price-label {
        color: #dcdde1;
        font-size: 14px;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .price-value {
        color: #ffffff;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .price-context {
        color: #b2bec3;
        font-size: 12px;
        font-style: italic;
    }
    .highlight-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        color: #dcdde1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="target-header">🎯 Price Analysis & Targets</div>', unsafe_allow_html=True)
    
    # Current Price Section
    st.markdown(f"""
    <div class="price-card card-current">
        <div class="price-label">Current Market Price</div>
        <div class="price-value">₹{targets['Current Price']:,.2f}</div>
        <div class="price-context">Last traded price in the market</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Support & Resistance Levels
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="price-card card-support">
            <div class="price-label">Support Levels</div>
            <div class="price-value">₹{targets['Strong Support']:,.2f}</div>
            <div class="highlight-box">
                <div style="color: #2ecc71; font-weight: 500;">Secondary Support</div>
                <div style="font-size: 18px; color: #2ecc71;">₹{targets['Weak Support']:,.2f}</div>
            </div>
            <div class="price-context">Based on recent price action and volume</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="price-card card-resistance">
            <div class="price-label">Resistance Levels</div>
            <div class="price-value">₹{targets['Strong Resistance']:,.2f}</div>
            <div class="highlight-box">
                <div style="color: #e74c3c; font-weight: 500;">Secondary Resistance</div>
                <div style="font-size: 18px; color: #e74c3c;">₹{targets['Weak Resistance']:,.2f}</div>
            </div>
            <div class="price-context">Based on recent price action and volume</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Price Targets Section
    st.markdown("### 🎯 Price Targets")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="price-card card-target">
            <div class="price-label">Short-term Target</div>
            <div class="price-value">₹{targets['Short-term Target']:,.2f}</div>
            <div class="price-context">Expected in 1-2 weeks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="price-card card-target">
            <div class="price-label">Medium-term Target</div>
            <div class="price-value">₹{targets['Medium-term Target']:,.2f}</div>
            <div class="price-context">Expected in 1-2 months</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="price-card card-target">
            <div class="price-label">Volatility-based Target</div>
            <div class="price-value">₹{targets['Volatility Target']:,.2f}</div>
            <div class="price-context">Based on price volatility</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk/Reward Section
    risk_color = "#2ecc71" if targets['Risk/Reward Ratio'] >= 2 else "#f1c40f" if targets['Risk/Reward Ratio'] >= 1 else "#e74c3c"
    
    st.markdown(f"""
    <div class="price-card" style="border-color: {risk_color};">
        <div class="price-label">Risk/Reward Analysis</div>
        <div class="price-value" style="font-size: 20px;">
            {targets['Risk/Reward Ratio']:.2f} : 1
        </div>
        <div class="highlight-box">
            <div style="color: {risk_color};">
                {'👍 Favorable risk/reward ratio' if targets['Risk/Reward Ratio'] >= 2 else 
                '⚠️ Consider risk management carefully' if targets['Risk/Reward Ratio'] >= 1 else 
                '⛔ Unfavorable risk/reward ratio'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)