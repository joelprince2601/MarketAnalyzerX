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
            'theme': 'light'
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
        self.current_theme = st.session_state.chart_config['theme']
        self.current_chart_type = st.session_state.chart_config['chart_type']
    
    def create_base_chart(self, df, chart_type='candlestick', theme='default'):
        """
        Create the base chart with specified type and theme
        """
        fig = make_subplots(rows=2, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.03,
                           row_heights=[0.7, 0.3])

        # Main price chart
        if chart_type == 'candlestick':
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ),
                row=1, col=1
            )
        elif chart_type == 'line':
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['close'],
                    mode='lines',
                    name='Price'
                ),
                row=1, col=1
            )
        elif chart_type == 'area':
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['close'],
                    fill='tozeroy',
                    name='Price'
                ),
                row=1, col=1
            )
        elif chart_type == 'bar':
            fig.add_trace(
                go.Ohlc(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ),
                row=1, col=1
            )
        elif chart_type == 'hollow_candle':
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price',
                    increasing={'fillcolor': 'white'},
                    decreasing={'fillcolor': 'black'}
                ),
                row=1, col=1
            )

        # Volume chart
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='Volume',
                marker_color='rgba(100,100,100,0.5)'
            ),
            row=2, col=1
        )

        # Update layout with theme
        fig.update_layout(
            template=CHART_THEMES[theme],
            xaxis_rangeslider_visible=False,
            height=800
        )

        return fig

    def add_drawing_tools(self, fig):
        """
        Add drawing tools to the chart
        """
        fig.update_layout(
            dragmode='drawline',
            newshape=dict(
                line_color='yellow'
            ),
            modebar_add=[
                'drawline',
                'drawopenpath',
                'drawclosedpath',
                'drawcircle',
                'drawrect',
                'eraseshape'
            ]
        )
        return fig

    def add_technical_overlays(self, fig, df, overlays):
        """
        Add technical overlays to the chart
        """
        if 'sma' in overlays:
            sma20 = df['close'].rolling(window=20).mean()
            sma50 = df['close'].rolling(window=50).mean()
            
            fig.add_trace(
                go.Scatter(x=df.index, y=sma20, name='SMA 20', line=dict(color='blue')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=sma50, name='SMA 50', line=dict(color='red')),
                row=1, col=1
            )

        if 'bollinger' in overlays:
            sma20 = df['close'].rolling(window=20).mean()
            std20 = df['close'].rolling(window=20).std()
            upper_band = sma20 + (std20 * 2)
            lower_band = sma20 - (std20 * 2)
            
            fig.add_trace(
                go.Scatter(x=df.index, y=upper_band, name='Upper BB',
                          line=dict(color='gray', dash='dash')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=lower_band, name='Lower BB',
                          line=dict(color='gray', dash='dash')),
                row=1, col=1
            )

        return fig

    def save_chart_config(self, config, filename):
        """
        Save chart configuration to a file
        """
        config['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create directory if it doesn't exist
        os.makedirs('chart_configs', exist_ok=True)
        
        with open(f'chart_configs/{filename}.json', 'w') as f:
            json.dump(config, f)

    def load_chart_config(self, filename):
        """
        Load chart configuration from a file
        """
        try:
            with open(f'chart_configs/{filename}.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

def create_enhanced_chart(df, config=None):
    """
    Main function to create enhanced chart with all features
    """
    visualizer = ChartVisualizer()
    
    if config is None:
        config = st.session_state.chart_config
    else:
        st.session_state.chart_config = config
    
    # Create base chart
    fig = visualizer.create_base_chart(df, config['chart_type'], config['theme'])
    
    # Add technical overlays
    fig = visualizer.add_technical_overlays(fig, df, config['overlays'])
    
    # Add drawing tools if enabled
    if config.get('drawing_tools', True):
        fig = visualizer.add_drawing_tools(fig)
    
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
            'drawing_tools': enable_drawing
        })
        
        return st.session_state.chart_config
