import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

# Available chart themes
CHART_THEMES = {
    'default': 'plotly',
    'dark': 'plotly_dark',
    'white': 'plotly_white',
    'light': 'plotly_white',
    'presentation': 'presentation',
    'ggplot2': 'ggplot2',
    'seaborn': 'seaborn'
}

# Chart types and their configurations
CHART_TYPES = {
    'candlestick': {'name': 'Candlestick', 'requires': ['open', 'high', 'low', 'close']},
    'line': {'name': 'Line', 'requires': ['close']},
    'area': {'name': 'Area', 'requires': ['close']},
    'bar': {'name': 'OHLC Bars', 'requires': ['open', 'high', 'low', 'close']},
    'hollow_candle': {'name': 'Hollow Candlestick', 'requires': ['open', 'high', 'low', 'close']}
}

def initialize_session_state():
    """Initialize all session state variables with default values"""
    if 'chart_config' not in st.session_state:
        st.session_state.chart_config = {
            'chart_type': 'candlestick',
            'overlays': [],
            'drawing_tools': False,
            'theme': 'light',
            'show_trendlines': False,
            'trendline_period': 20,
            'show_support_resistance': False,
            'show_fibonacci': False
        }
    
    if 'expander_states' not in st.session_state:
        st.session_state.expander_states = {
            'chart_settings': True,
            'technical_overlays': True,
            'drawing_tools': True,
            'technical_analysis': True,
            'save_load': True
        }

def calculate_trendlines(df, period=20):
    """Calculate trendlines using linear regression"""
    highs = df['high'].rolling(window=period).max()
    lows = df['low'].rolling(window=period).min()
    
    x = np.arange(len(df))
    
    # Resistance line
    slope_high, intercept_high, _, _, _ = stats.linregress(x[-period:], highs[-period:])
    resistance_line = slope_high * x + intercept_high
    
    # Support line
    slope_low, intercept_low, _, _, _ = stats.linregress(x[-period:], lows[-period:])
    support_line = slope_low * x + intercept_low
    
    return resistance_line, support_line

def calculate_fibonacci_levels(df):
    """Calculate Fibonacci retracement levels"""
    high = df['high'].max()
    low = df['low'].min()
    diff = high - low
    
    levels = {
        0.0: low,
        0.236: low + 0.236 * diff,
        0.382: low + 0.382 * diff,
        0.5: low + 0.5 * diff,
        0.618: low + 0.618 * diff,
        1.0: high
    }
    return levels

class ChartVisualizer:
    def __init__(self):
        self.drawings = []
        self.annotations = []
        self.current_theme = st.session_state.chart_config['theme']
        self.current_chart_type = st.session_state.chart_config['chart_type']

    def create_base_chart(self, df, chart_type='candlestick', theme='light'):
        """Create the base chart with the specified type and theme"""
        if chart_type == 'candlestick':
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )])
        elif chart_type == 'line':
            fig = go.Figure(data=[go.Scatter(
                x=df.index,
                y=df['close'],
                mode='lines'
            )])
        elif chart_type == 'area':
            fig = go.Figure(data=[go.Scatter(
                x=df.index,
                y=df['close'],
                fill='tozeroy'
            )])
            
        # Update layout with theme
        fig.update_layout(
            template=CHART_THEMES[theme],
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        return fig

    def add_technical_overlays(self, fig, df, overlays):
        """Add technical overlays to the chart"""
        if 'sma' in overlays:
            sma = df['close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=sma,
                name='SMA (20)',
                line=dict(color='blue')
            ))
            
        if 'ema' in overlays:
            ema = df['close'].ewm(span=20).mean()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=ema,
                name='EMA (20)',
                line=dict(color='orange')
            ))
            
        return fig

def add_technical_analysis(fig, df, config):
    """Add technical analysis features to the chart"""
    if config.get('show_trendlines', False):
        resistance, support = calculate_trendlines(df, config['trendline_period'])
        fig.add_trace(go.Scatter(
            x=df.index,
            y=resistance,
            name='Resistance',
            line=dict(color='red', dash='dash'),
            opacity=0.7
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=support,
            name='Support',
            line=dict(color='green', dash='dash'),
            opacity=0.7
        ))
    
    if config.get('show_fibonacci', False):
        fib_levels = calculate_fibonacci_levels(df)
        colors = ['rgba(255,0,0,0.3)', 'rgba(255,165,0,0.3)', 'rgba(255,255,0,0.3)',
                 'rgba(0,255,0,0.3)', 'rgba(0,0,255,0.3)']
        
        for (level, value), color in zip(fib_levels.items(), colors):
            fig.add_hline(
                y=value,
                line_dash="dash",
                line_color=color,
                annotation_text=f"Fib {level}",
                annotation_position="right"
            )
    
    return fig

def create_enhanced_chart(df, config):
    """Create an enhanced chart with all selected features"""
    # Initialize visualizer
    visualizer = ChartVisualizer()
    
    # Create base chart
    fig = visualizer.create_base_chart(df, config['chart_type'], config.get('theme', 'light'))
    
    # Add technical overlays
    fig = visualizer.add_technical_overlays(fig, df, config['overlays'])
    
    # Add technical analysis features
    fig = add_technical_analysis(fig, df, config)
    
    return fig

def render_chart_controls():
    """
    Render Streamlit controls for chart customization
    """
    # Initialize session state
    initialize_session_state()
    
    with st.sidebar:
        st.title("Chart Controls")
        
        # Chart Settings Expander
        with st.expander("Chart Settings", expanded=st.session_state.expander_states['chart_settings']):
            # Chart Type Selection
            chart_type = st.selectbox(
                "Chart Type",
                ['candlestick', 'line', 'area'],
                index=['candlestick', 'line', 'area'].index(st.session_state.chart_config['chart_type'])
            )
            
            # Update expander state
            st.session_state.expander_states['chart_settings'] = True
            
        # Technical Overlays Expander
        with st.expander("Technical Overlays", expanded=st.session_state.expander_states['technical_overlays']):
            show_sma = st.checkbox("Show SMA", value='sma' in st.session_state.chart_config['overlays'])
            show_ema = st.checkbox("Show EMA", value='ema' in st.session_state.chart_config['overlays'])
            
            # Update expander state
            st.session_state.expander_states['technical_overlays'] = True
            
        # Technical Analysis Expander
        with st.expander("Technical Analysis", expanded=st.session_state.expander_states['technical_analysis']):
            show_trendlines = st.checkbox("Show Trendlines", value=st.session_state.chart_config.get('show_trendlines', False))
            show_support_resistance = st.checkbox("Show Support/Resistance", value=st.session_state.chart_config.get('show_support_resistance', False))
            show_fibonacci = st.checkbox("Show Fibonacci Levels", value=st.session_state.chart_config.get('show_fibonacci', False))
            
            if show_trendlines:
                trendline_period = st.slider("Trendline Period", 5, 50, 20)
            else:
                trendline_period = 20
            
            # Update expander state
            st.session_state.expander_states['technical_analysis'] = True
            
        # Drawing Tools Expander
        with st.expander("Drawing Tools", expanded=st.session_state.expander_states['drawing_tools']):
            enable_drawing = st.checkbox("Enable Drawing Tools", value=st.session_state.chart_config['drawing_tools'])
            
            # Update expander state
            st.session_state.expander_states['drawing_tools'] = True
            
        # Save/Load Configuration Expander
        with st.expander("Save/Load Configuration", expanded=st.session_state.expander_states['save_load']):
            save_name = st.text_input("Configuration Name")
            
            # Update expander state
            st.session_state.expander_states['save_load'] = True
        
        # Update chart configuration
        st.session_state.chart_config.update({
            'chart_type': chart_type,
            'overlays': ['sma' if show_sma else None, 'ema' if show_ema else None],
            'drawing_tools': enable_drawing,
            'show_trendlines': show_trendlines,
            'trendline_period': trendline_period,
            'show_support_resistance': show_support_resistance,
            'show_fibonacci': show_fibonacci
        })
        
        return st.session_state.chart_config
