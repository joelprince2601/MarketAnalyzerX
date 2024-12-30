import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import asyncio

def generate_simulated_stock_data():
    """Generate fake initial stock data for simulation"""
    base_price = 100
    return {
        'price': base_price,
        'trend': np.random.choice(['bullish', 'bearish', 'sideways']),
        'volatility_base': 0.002
    }

class TradingSimulator:
    def __init__(self, initial_balance=100000):
        # Initialize simulation parameters
        sim_data = generate_simulated_stock_data()
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.positions = {}
        self.is_running = False
        
        # Set market hours for simulation
        current_date = datetime.now().date()
        self.market_open = datetime.combine(current_date, datetime.strptime("09:15", "%H:%M").time())
        self.market_close = datetime.combine(current_date, datetime.strptime("15:30", "%H:%M").time())
        self.total_minutes = int((self.market_close - self.market_open).total_seconds() / 60)
        
        # Simulation parameters
        self.base_price = sim_data['price']
        self.current_price = self.base_price
        self.time_compression = self.total_minutes / 30  # 30 seconds simulation
        
    def reset(self):
        """Reset simulator to initial state"""
        self.current_balance = self.initial_balance
        self.positions = {}
        self.is_running = False
        self.current_price = self.base_price
        
    def simulate_price_movement(self, current_price, time_of_day, volatility=0.002):
        """Simulate realistic price movement based on time of day"""
        # Increase volatility during market open and close
        hour = time_of_day.hour
        minute = time_of_day.minute
        
        if (hour == 9 and minute < 30) or (hour == 15 and minute > 15):
            volatility *= 1.5
        elif hour in [11, 14]:  # Lunch hours - lower volatility
            volatility *= 0.7
            
        return current_price * (1 + np.random.normal(0, volatility))
    
    def create_real_time_chart(self):
        """Create real-time trading chart"""
        fig = make_subplots(rows=2, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.03,
                           row_heights=[0.7, 0.3])
        
        # Price chart
        fig.add_trace(
            go.Scatter(
                x=[], y=[],
                name="Price",
                line=dict(color='#2ecc71', width=2)
            ),
            row=1, col=1
        )
        
        # Volume chart
        fig.add_trace(
            go.Bar(
                x=[], y=[],
                name="Volume",
                marker_color='#3498db'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            title_text="Live Trading Simulation",
            showlegend=True,
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            updatemenus=[{
                'buttons': [
                    {'label': 'Price', 'method': 'update', 'args': [{'visible': [True, False]}]},
                    {'label': 'Volume', 'method': 'update', 'args': [{'visible': [False, True]}]}
                ],
                'direction': 'down',
                'showactive': True,
                'x': 0.1,
                'y': 1.1
            }]
        )
        
        return fig

def run_trading_simulation():
    """Run interactive trading simulation"""
    st.subheader("Live Trading Simulation")
    
    # Initialize session state
    if 'simulator' not in st.session_state:
        st.session_state.simulator = TradingSimulator()
        st.session_state.prices = []
        st.session_state.volumes = []
        st.session_state.timestamps = []
        st.session_state.trades = []
    
    # Create layout
    col1, col2 = st.columns([2,1])
    
    with col1:
        # Chart and time display
        chart_placeholder = st.empty()
        time_placeholder = st.empty()
        fig = st.session_state.simulator.create_real_time_chart()
    
    with col2:
        # Trading controls
        st.markdown("### Trading Controls")
        trade_type = st.radio("Action", ["Buy", "Sell"], key="sim_trade_type")
        quantity = st.number_input("Quantity", min_value=1, value=1, key="sim_quantity")
        trade_button = st.button("Execute Trade", key="sim_trade_button")
        
        # Simulation controls
        st.markdown("### Simulation Controls")
        volatility = st.slider("Market Volatility", 0.001, 0.01, 0.002, 0.001, key="sim_volatility")
        
        # Start/Reset buttons
        col1, col2 = st.columns(2)
        with col1:
            start_button = st.button("▶ Start Day", key="start_sim")
        with col2:
            reset_button = st.button("🔄 Reset", key="reset_sim")
        
        # Portfolio metrics
        st.markdown("### Portfolio")
        st.metric("Balance", 
                 f"₹{st.session_state.simulator.current_balance:,.2f}",
                 delta=f"₹{(st.session_state.simulator.current_balance - st.session_state.simulator.initial_balance):,.2f}")
        
        st.metric("Current Price",
                 f"₹{st.session_state.simulator.current_price:,.2f}")
    
    # Handle reset
    if reset_button:
        st.session_state.simulator.reset()
        st.session_state.prices = []
        st.session_state.volumes = []
        st.session_state.timestamps = []
        st.session_state.trades = []
        st.experimental_rerun()
    
    # Handle trading
    if trade_button:
        execute_trade(trade_type, quantity, st.session_state.simulator.current_price)
    
    # Run simulation
    if start_button:
        run_market_day(
            chart_placeholder,
            time_placeholder,
            fig,
            volatility
        )

def execute_trade(trade_type, quantity, price):
    """Execute a trade and update portfolio"""
    if trade_type == "Buy":
        cost = price * quantity
        if cost <= st.session_state.simulator.current_balance:
            st.session_state.simulator.current_balance -= cost
            st.session_state.trades.append({
                'type': 'BUY',
                'quantity': quantity,
                'price': price,
                'time': st.session_state.timestamps[-1] if st.session_state.timestamps else datetime.now()
            })
            st.success(f"Bought {quantity} shares at ₹{price:,.2f}")
        else:
            st.error("Insufficient funds!")
    else:
        # Calculate total owned shares
        owned_shares = sum([t['quantity'] for t in st.session_state.trades if t['type'] == 'BUY']) - \
                      sum([t['quantity'] for t in st.session_state.trades if t['type'] == 'SELL'])
        
        if owned_shares >= quantity:
            value = price * quantity
            st.session_state.simulator.current_balance += value
            st.session_state.trades.append({
                'type': 'SELL',
                'quantity': quantity,
                'price': price,
                'time': st.session_state.timestamps[-1] if st.session_state.timestamps else datetime.now()
            })
            st.success(f"Sold {quantity} shares at ₹{price:,.2f}")
        else:
            st.error("Insufficient shares!")

def run_market_day(chart_placeholder, time_placeholder, fig, volatility):
    """Simulate a full trading day in 30 seconds"""
    simulator = st.session_state.simulator
    current_time = simulator.market_open
    update_interval = 0.1  # Update every 100ms
    steps = int(30 / update_interval)  # Total steps for 30-second simulation
    minutes_per_step = simulator.total_minutes / steps
    
    # Market patterns
    patterns = {
        'opening_volatility': True,  # First 30 minutes
        'lunch_dip': True,          # Around 12-1 PM
        'closing_rally': True       # Last 30 minutes
    }
    
    trend = np.random.choice(['bullish', 'bearish', 'sideways'])
    trend_factor = {
        'bullish': 0.0001,
        'bearish': -0.0001,
        'sideways': 0
    }[trend]
    
    st.sidebar.markdown(f"### Market Trend: {trend.title()}")
    
    for step in range(steps):
        if current_time >= simulator.market_close:
            break
            
        # Base volatility
        current_volatility = volatility
        
        # Adjust volatility based on time of day
        hour = current_time.hour
        minute = current_time.minute
        
        # Opening volatility (first 30 minutes)
        if patterns['opening_volatility'] and hour == 9 and minute < 45:
            current_volatility *= 2
            
        # Lunch hour dip
        elif patterns['lunch_dip'] and hour in [12, 13]:
            current_volatility *= 0.5
            if trend != 'bearish':
                trend_factor = -0.0002  # Slight downward pressure
                
        # Closing volatility
        elif patterns['closing_rally'] and hour == 15 and minute > 0:
            current_volatility *= 1.5
            if trend != 'bearish':
                trend_factor = 0.0002  # Slight upward pressure
        
        # Update price with pattern-based movement
        price_change = np.random.normal(trend_factor, current_volatility)
        simulator.current_price *= (1 + price_change)
        
        # Generate volume based on time of day
        base_volume = np.random.randint(1000, 10000)
        if hour in [9, 15]:  # Higher volume at market open/close
            current_volume = base_volume * 2
        elif hour in [12, 13]:  # Lower volume during lunch
            current_volume = base_volume * 0.5
        else:
            current_volume = base_volume
            
        # Add volume spikes on significant price moves
        if abs(price_change) > current_volatility * 2:
            current_volume *= 1.5
        
        # Update data
        st.session_state.timestamps.append(current_time)
        st.session_state.prices.append(simulator.current_price)
        st.session_state.volumes.append(int(current_volume))
        
        # Keep only last 100 points for smooth visualization
        if len(st.session_state.prices) > 100:
            st.session_state.timestamps.pop(0)
            st.session_state.prices.pop(0)
            st.session_state.volumes.pop(0)
        
        # Update chart
        fig.data[0].x = st.session_state.timestamps
        fig.data[0].y = st.session_state.prices
        fig.data[1].x = st.session_state.timestamps
        fig.data[1].y = st.session_state.volumes
        
        # Update display
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        time_placeholder.markdown(
            f"""
            ### Market Time: {current_time.strftime('%H:%M')}
            Current Trend: {trend.title()}
            """
        )
        
        # Increment time
        current_time += timedelta(minutes=minutes_per_step)
        time.sleep(update_interval)
    
    # Market close summary
    st.success("Market Closed!")
    if st.session_state.trades:
        st.markdown("### Trading Summary")
        df_trades = pd.DataFrame(st.session_state.trades)
        st.dataframe(df_trades) 