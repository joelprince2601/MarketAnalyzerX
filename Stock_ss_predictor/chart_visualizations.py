import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# Available chart themes
CHART_THEMES = {
    'default': 'plotly',
    'dark': 'plotly_dark',
    'white': 'plotly_white',
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
            'theme': 'default'  # Using 'default' from CHART_THEMES
        }
    
    if 'expander_states' not in st.session_state:
        st.session_state.expander_states = {
            'chart_settings': True,
            'technical_overlays': True,
            'drawing_tools': True,
            'save_load': True
        }

class ChartVisualizer:
    def __init__(self):
        self.drawings = []
        self.annotations = []
        self.current_theme = st.session_state.chart_config.get('theme', 'default')
        self.current_chart_type = st.session_state.chart_config.get('chart_type', 'candlestick')

    def create_base_chart(self, df, chart_type='candlestick', theme='default'):
        """Create the base chart with the specified type and theme"""
        # Ensure theme exists in CHART_THEMES, fallback to default if not
        theme = theme if theme in CHART_THEMES else 'default'
        
        # Standardize column names (convert to title case)
        df.columns = [col.title() for col in df.columns]
        
        fig = go.Figure(
            layout=go.Layout(
                template=CHART_THEMES[theme],
                xaxis_rangeslider_visible=False,
                height=600,
                title={
                    'text': f"Stock Price Chart",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
        )

        if chart_type == 'candlestick':
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='OHLC'
                )
            )
        elif chart_type == 'line':
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    mode='lines',
                    name='Close Price'
                )
            )
        elif chart_type == 'area':
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    fill='tozeroy',
                    name='Close Price'
                )
            )

        return fig

    def add_volume_subplot(self, fig, df):
        """Add volume subplot to the chart"""
        # Ensure column names are standardized
        df.columns = [col.title() for col in df.columns]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color='rgba(0,0,255,0.5)'
            ),
            row=2, col=1
        )
        return fig

    def add_technical_indicators(self, fig, df, indicators):
        """Add technical indicators to the chart"""
        # Ensure column names are standardized
        df.columns = [col.title() for col in df.columns]
        
        if 'sma' in indicators:
            sma = df['Close'].rolling(window=20).mean()
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=sma,
                    name='20 SMA',
                    line=dict(color='orange')
                )
            )
        
        if 'ema' in indicators:
            ema = df['Close'].ewm(span=20, adjust=False).mean()
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=ema,
                    name='20 EMA',
                    line=dict(color='blue')
                )
            )
        
        return fig

    def add_drawings(self, fig):
        """Add user drawings to the chart"""
        for drawing in self.drawings:
            fig.add_trace(drawing)
        return fig

    def add_annotations(self, fig):
        """Add annotations to the chart"""
        for annotation in self.annotations:
            fig.add_annotation(annotation)
        return fig

def render_chart_controls():
    """Render Streamlit controls for chart customization"""
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
            
            # Theme Selection
            theme = st.selectbox(
                "Chart Theme",
                list(CHART_THEMES.keys()),
                index=list(CHART_THEMES.keys()).index(st.session_state.chart_config['theme'])
            )
            
            # Update expander state
            st.session_state.expander_states['chart_settings'] = True
        
        # Technical Overlays Expander
        with st.expander("Technical Overlays", expanded=st.session_state.expander_states['technical_overlays']):
            show_sma = st.checkbox("Show SMA", value='sma' in st.session_state.chart_config['overlays'])
            show_ema = st.checkbox("Show EMA", value='ema' in st.session_state.chart_config['overlays'])
            
            # Update expander state
            st.session_state.expander_states['technical_overlays'] = True
        
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
            'theme': theme,
            'overlays': [x for x in ['sma' if show_sma else None, 'ema' if show_ema else None] if x is not None],
            'drawing_tools': enable_drawing
        })
        
        return st.session_state.chart_config

def create_enhanced_chart(df, config):
    """Create an enhanced chart with all selected features"""
    visualizer = ChartVisualizer()
    
    # Create base chart
    fig = visualizer.create_base_chart(df, config['chart_type'], config['theme'])
    
    # Add technical indicators if specified
    if config['overlays']:
        fig = visualizer.add_technical_indicators(fig, df, config['overlays'])
    
    # Add drawings if enabled
    if config['drawing_tools']:
        fig = visualizer.add_drawings(fig)
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def save_chart_config(config, name):
    """Save chart configuration to file"""
    config_dir = "chart_configs"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    filename = os.path.join(config_dir, f"{name}.json")
    with open(filename, 'w') as f:
        json.dump(config, f)

def load_chart_config(name):
    """Load chart configuration from file"""
    filename = os.path.join("chart_configs", f"{name}.json")
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return None
