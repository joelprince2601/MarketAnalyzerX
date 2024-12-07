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

# Initialize session state for chart configuration and expander states
if 'chart_config' not in st.session_state:
    st.session_state.chart_config = {
        'chart_type': 'candlestick',
        'theme': 'default',
        'overlays': ['sma', 'bollinger'],
        'drawing_tools': True
    }

# Initialize expander states
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
    # Initialize session state if not already done
    if 'expander_states' not in st.session_state:
        st.session_state.expander_states = True  # Default to expanded

    with st.sidebar:
        st.title("Chart Controls")
        
        # Chart Settings Expander
        with st.expander("Chart Settings", expanded=st.session_state.expander_states):
            # Chart Type Selection
            chart_type = st.selectbox(
                "Chart Type",
                list(CHART_TYPES.keys()),
                index=list(CHART_TYPES.keys()).index(st.session_state.chart_config['chart_type']),
                format_func=lambda x: CHART_TYPES[x]['name'],
                key='chart_type_select'
            )
            
            # Theme Selection
            theme = st.selectbox(
                "Chart Theme",
                list(CHART_THEMES.keys()),
                index=list(CHART_THEMES.keys()).index(st.session_state.chart_config['theme']),
                key='theme_select'
            )
            
            # Update expander state
            st.session_state.expander_states = True
        
        # Technical Overlays Expander
        with st.expander("Technical Overlays", expanded=st.session_state.expander_states):
            show_sma = st.checkbox("Show SMA", 
                                 value='sma' in st.session_state.chart_config['overlays'],
                                 key='sma_checkbox')
            show_bollinger = st.checkbox("Show Bollinger Bands", 
                                       value='bollinger' in st.session_state.chart_config['overlays'],
                                       key='bollinger_checkbox')
            
            # Update expander state
            st.session_state.expander_states = True
        
        # Drawing Tools Expander
        with st.expander("Drawing Tools", expanded=st.session_state.expander_states):
            enable_drawing = st.checkbox("Enable Drawing Tools", 
                                       value=st.session_state.chart_config['drawing_tools'],
                                       key='drawing_tools_checkbox')
            
            # Update expander state
            st.session_state.expander_states = True
        
        # Save/Load Configuration Expander
        with st.expander("Save/Load Configuration", expanded=st.session_state.expander_states):
            save_name = st.text_input("Configuration Name")
            
            if st.button("Save Configuration"):
                config = {
                    'chart_type': chart_type,
                    'theme': theme,
                    'overlays': [],
                    'drawing_tools': enable_drawing
                }
                if show_sma:
                    config['overlays'].append('sma')
                if show_bollinger:
                    config['overlays'].append('bollinger')
                
                visualizer = ChartVisualizer()
                visualizer.save_chart_config(config, save_name)
                st.success("Configuration saved!")
                st.session_state.chart_config = config
                
                # Reset expander states after saving
                for key in st.session_state.expander_states:
                    st.session_state.expander_states[key] = False
            
            # Load Configuration
            saved_configs = [f.replace('.json', '') for f in os.listdir('chart_configs')] if os.path.exists('chart_configs') else []
            if saved_configs:
                load_config = st.selectbox("Load Configuration", [''] + saved_configs)
                if load_config:
                    visualizer = ChartVisualizer()
                    config = visualizer.load_chart_config(load_config)
                    if config:
                        st.success("Configuration loaded!")
                        st.session_state.chart_config = config
                        return config
            
            # Update expander state
            st.session_state.expander_states = True
        
        # Update session state with current settings
        current_config = {
            'chart_type': chart_type,
            'theme': theme,
            'overlays': (['sma'] if show_sma else []) + (['bollinger'] if show_bollinger else []),
            'drawing_tools': enable_drawing
        }
        st.session_state.chart_config = current_config
        return current_config 
