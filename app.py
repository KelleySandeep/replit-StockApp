import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
from utils import format_currency, format_number, get_stock_info, validate_symbol

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📈 Stock Analysis Dashboard")
st.markdown("*Get comprehensive financial data and interactive charts for any stock symbol*")

# Sidebar for inputs
st.sidebar.header("Stock Selection")

# Stock symbol input
symbol = st.sidebar.text_input(
    "Enter Stock Symbol",
    value="AAPL",
    help="Enter a valid stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
).upper().strip()

# Time period selection
period_options = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "Max": "max"
}

selected_period = st.sidebar.selectbox(
    "Select Time Period",
    options=list(period_options.keys()),
    index=3  # Default to 1 Year
)

period = period_options[selected_period]

# Chart type selection
chart_type = st.sidebar.selectbox(
    "Chart Type",
    options=["Candlestick", "Line Chart", "Area Chart"],
    index=0
)

# Technical indicators
st.sidebar.subheader("Technical Indicators")
show_volume = st.sidebar.checkbox("Show Volume", value=True)
show_ma20 = st.sidebar.checkbox("20-Day Moving Average", value=False)
show_ma50 = st.sidebar.checkbox("50-Day Moving Average", value=False)

# Main content
if symbol:
    # Validate symbol
    if not validate_symbol(symbol):
        st.error(f"⚠️ Invalid stock symbol: {symbol}. Please enter a valid ticker symbol.")
        st.stop()
    
    try:
        # Show loading spinner
        with st.spinner(f"Fetching data for {symbol}..."):
            # Get stock data
            stock = yf.Ticker(symbol)
            
            # Get historical data
            hist_data = stock.history(period=period)
            
            if hist_data.empty:
                st.error(f"No data found for symbol {symbol}. Please check the symbol and try again.")
                st.stop()
            
            # Get stock info
            info = get_stock_info(symbol)
            
        # Display stock information header
        col1, col2, col3, col4 = st.columns(4)
        
        current_price = hist_data['Close'].iloc[-1]
        prev_close = info.get('previousClose', hist_data['Close'].iloc[-2] if len(hist_data) > 1 else current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
        
        with col1:
            st.metric(
                label=f"{symbol} - {info.get('longName', 'N/A')}",
                value=format_currency(current_price),
                delta=f"{change:+.2f} ({change_percent:+.2f}%)"
            )
        
        with col2:
            st.metric(
                label="Market Cap",
                value=format_number(info.get('marketCap', 0))
            )
        
        with col3:
            st.metric(
                label="Volume",
                value=format_number(hist_data['Volume'].iloc[-1])
            )
        
        with col4:
            st.metric(
                label="P/E Ratio",
                value=f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A"
            )
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Charts", "📋 Financial Data", "📈 Key Metrics"])
        
        with tab1:
            # Calculate technical indicators
            if show_ma20 and len(hist_data) >= 20:
                hist_data['MA20'] = hist_data['Close'].rolling(window=20).mean()
            if show_ma50 and len(hist_data) >= 50:
                hist_data['MA50'] = hist_data['Close'].rolling(window=50).mean()
            
            # Create price chart
            if chart_type == "Candlestick":
                fig = go.Figure(data=[go.Candlestick(
                    x=hist_data.index,
                    open=hist_data['Open'],
                    high=hist_data['High'],
                    low=hist_data['Low'],
                    close=hist_data['Close'],
                    name=symbol
                )])
            elif chart_type == "Line Chart":
                fig = go.Figure(data=[go.Scatter(
                    x=hist_data.index,
                    y=hist_data['Close'],
                    mode='lines',
                    name=f'{symbol} Close Price',
                    line=dict(color='#00d4aa', width=2)
                )])
            else:  # Area Chart
                fig = go.Figure(data=[go.Scatter(
                    x=hist_data.index,
                    y=hist_data['Close'],
                    fill='tonexty',
                    mode='lines',
                    name=f'{symbol} Close Price',
                    line=dict(color='#00d4aa', width=2)
                )])
            
            # Add moving averages
            if show_ma20 and 'MA20' in hist_data.columns:
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=hist_data['MA20'],
                    mode='lines',
                    name='20-Day MA',
                    line=dict(color='orange', width=1, dash='dash')
                ))
            
            if show_ma50 and 'MA50' in hist_data.columns:
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=hist_data['MA50'],
                    mode='lines',
                    name='50-Day MA',
                    line=dict(color='red', width=1, dash='dash')
                ))
            
            # Update layout
            fig.update_layout(
                title=f"{symbol} Stock Price - {selected_period}",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=600,
                showlegend=True,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            if show_volume:
                vol_fig = go.Figure(data=[go.Bar(
                    x=hist_data.index,
                    y=hist_data['Volume'],
                    name='Volume',
                    marker_color='rgba(0, 212, 170, 0.6)'
                )])
                
                vol_fig.update_layout(
                    title=f"{symbol} Trading Volume",
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    height=300
                )
                
                st.plotly_chart(vol_fig, use_container_width=True)
        
        with tab2:
            st.subheader("Historical Price Data")
            
            # Prepare data for display
            display_data = hist_data.copy()
            display_data = display_data.round(2)
            display_data.index = display_data.index.strftime('%Y-%m-%d')
            
            # Sort by date (most recent first)
            display_data = display_data.sort_index(ascending=False)
            
            # Display the data
            st.dataframe(
                display_data,
                use_container_width=True,
                height=400
            )
            
            # Download button
            csv_buffer = io.StringIO()
            display_data.to_csv(csv_buffer)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label=f"📥 Download {symbol} Data as CSV",
                data=csv_data,
                file_name=f"{symbol}_stock_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with tab3:
            st.subheader("Key Financial Metrics")
            
            # Create two columns for metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Valuation Metrics**")
                metrics_data1 = {
                    "Market Cap": format_number(info.get('marketCap', 0)),
                    "Enterprise Value": format_number(info.get('enterpriseValue', 0)),
                    "P/E Ratio (TTM)": f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A",
                    "Forward P/E": f"{info.get('forwardPE', 'N/A'):.2f}" if info.get('forwardPE') else "N/A",
                    "Price to Book": f"{info.get('priceToBook', 'N/A'):.2f}" if info.get('priceToBook') else "N/A",
                    "Price to Sales": f"{info.get('priceToSalesTrailing12Months', 'N/A'):.2f}" if info.get('priceToSalesTrailing12Months') else "N/A"
                }
                
                for metric, value in metrics_data1.items():
                    st.write(f"**{metric}:** {value}")
            
            with col2:
                st.write("**Trading Metrics**")
                metrics_data2 = {
                    "52 Week High": format_currency(info.get('fiftyTwoWeekHigh', 0)),
                    "52 Week Low": format_currency(info.get('fiftyTwoWeekLow', 0)),
                    "Average Volume": format_number(info.get('averageVolume', 0)),
                    "Beta": f"{info.get('beta', 'N/A'):.2f}" if info.get('beta') else "N/A",
                    "Dividend Yield": f"{(info.get('dividendYield', 0) * 100):.2f}%" if info.get('dividendYield') else "N/A",
                    "Payout Ratio": f"{(info.get('payoutRatio', 0) * 100):.2f}%" if info.get('payoutRatio') else "N/A"
                }
                
                for metric, value in metrics_data2.items():
                    st.write(f"**{metric}:** {value}")
            
            # Financial highlights
            if info.get('longBusinessSummary'):
                st.subheader("Business Summary")
                st.write(info['longBusinessSummary'])
    
    except Exception as e:
        st.error(f"❌ Error fetching data for {symbol}: {str(e)}")
        st.write("Please check the stock symbol and try again.")

else:
    st.info("👆 Please enter a stock symbol in the sidebar to get started.")
    
    # Show some example symbols
    st.subheader("Popular Stock Symbols")
    example_symbols = {
        "Technology": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"],
        "Finance": ["JPM", "BAC", "WFC", "GS", "MS"],
        "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK"],
        "Consumer": ["AMZN", "WMT", "HD", "MCD", "NKE"]
    }
    
    for sector, symbols in example_symbols.items():
        st.write(f"**{sector}:** {', '.join(symbols)}")
