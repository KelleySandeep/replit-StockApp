import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
from utils import format_currency, format_number, get_stock_info, validate_symbol, get_stock_history_optimized
from database import (
    init_database, store_stock_data, get_stored_stock_data,
    add_to_watchlist, get_watchlist, remove_from_watchlist,
    add_to_portfolio, get_portfolio, update_portfolio_prices
)
from stock_symbols import search_stocks, get_symbol_suggestions, extract_symbol_from_suggestion

# Initialize database
init_database()

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
st.sidebar.header("🔍 Smart Stock Search")

# Create a container for the search
search_container = st.sidebar.container()

with search_container:
    # Initialize session state for selected stock
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = "AAPL"
    
    # Text input for stock symbol
    search_query = st.text_input(
        "Search Stock Symbol or Company",
        value="",
        help="Type to search for stocks by symbol or company name",
        key="stock_search"
    )
    
    # Show current selection
    if st.session_state.selected_stock:
        st.info(f"📊 Currently analyzing: **{st.session_state.selected_stock}**")
    
    # Show suggestions if user is typing
    if search_query and len(search_query) > 0:
        suggestions = get_symbol_suggestions(search_query, max_suggestions=8)
        
        if suggestions:
            st.write("**💡 Suggestions:**")
            for i, suggestion in enumerate(suggestions):
                if st.button(
                    suggestion, 
                    key=f"suggestion_{i}",
                    help="Click to select this stock"
                ):
                    # Update the selected stock
                    st.session_state.selected_stock = extract_symbol_from_suggestion(suggestion)
                    st.rerun()
        elif len(search_query) > 1:
            # Show fuzzy matches if no exact suggestions
            fuzzy_matches = search_stocks(search_query, limit=5)
            if fuzzy_matches:
                st.write("**🔍 Did you mean:**")
                for symbol, company, score in fuzzy_matches:
                    if st.button(
                        f"{symbol} - {company}", 
                        key=f"fuzzy_{symbol}",
                        help=f"Match confidence: {score}%"
                    ):
                        st.session_state.selected_stock = symbol
                        st.rerun()
            else:
                st.warning("No matches found. Try a different search term.")
    
    # Manual symbol entry option
    manual_symbol = st.text_input(
        "Or enter symbol directly:",
        value="",
        help="Enter a stock symbol manually (e.g., AAPL, TSLA)",
        key="manual_symbol"
    )
    
    if manual_symbol:
        if st.button("Analyze This Stock", key="analyze_manual"):
            st.session_state.selected_stock = manual_symbol.upper().strip()
            st.rerun()

# Use the selected stock
symbol = st.session_state.selected_stock

# Time period selection with performance warnings
period_options = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "Max": "max"
}

# Performance hints for period selection
period_descriptions = {
    "1 Month": "Fast loading",
    "3 Months": "Fast loading", 
    "6 Months": "Fast loading",
    "1 Year": "Fast loading",
    "2 Years": "Good performance",
    "5 Years": "May take a moment",
    "Max": "Optimized for large datasets"
}

selected_period = st.sidebar.selectbox(
    "Select Time Period",
    options=list(period_options.keys()),
    index=3,  # Default to 1 Year
    help="Choose time period. 'Max' shows all available historical data with smart optimization for performance."
)

# Show performance hint
if selected_period in period_descriptions:
    hint = period_descriptions[selected_period]
    if selected_period == "Max":
        st.sidebar.info(f"⚡ {hint}")
    elif "May take" in hint:
        st.sidebar.warning(f"⏳ {hint}")
    else:
        st.sidebar.success(f"🚀 {hint}")

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
        # Show loading spinner with period-specific messages
        loading_message = f"Fetching data for {symbol}..."
        if period == "max":
            loading_message = f"Fetching maximum historical data for {symbol}... (this may take a moment)"
        
        with st.spinner(loading_message):
            # Get optimized historical data
            hist_data = get_stock_history_optimized(symbol, period)
            
            if hist_data is None:
                st.error(f"Failed to fetch data for {symbol}. Please try again.")
                st.stop()
            
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
        
        # Add stock management buttons
        col_left, col_center, col_right = st.columns([1, 1, 1])
        
        with col_left:
            if st.button("➕ Add to Watchlist", use_container_width=True):
                success, message = add_to_watchlist(symbol, info.get('longName', symbol))
                if success:
                    st.success(message)
                else:
                    st.warning(message)
        
        with col_center:
            if st.button("💾 Store Historical Data", use_container_width=True):
                if store_stock_data(symbol, hist_data):
                    st.success("Historical data stored successfully!")
                else:
                    st.error("Failed to store historical data")
        
        with col_right:
            # Update portfolio prices
            update_portfolio_prices(symbol, current_price)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Charts", "📋 Financial Data", "📈 Key Metrics", "👁️ Watchlist", "💼 Portfolio"])
        
        with tab1:
            # Optimize chart data for large datasets
            chart_data = hist_data.copy()
            
            # For very large datasets, sample data for charts to improve performance
            if len(chart_data) > 2000:
                # Sample every nth point to reduce chart complexity
                sample_rate = max(1, len(chart_data) // 1500)
                chart_data = chart_data.iloc[::sample_rate]
                st.info(f"📈 Chart optimized: showing every {sample_rate} data point(s) for better performance")
            
            # Calculate technical indicators on chart data
            if show_ma20 and len(chart_data) >= 20:
                chart_data['MA20'] = chart_data['Close'].rolling(window=20).mean()
            if show_ma50 and len(chart_data) >= 50:
                chart_data['MA50'] = chart_data['Close'].rolling(window=50).mean()
            
            # Create price chart with optimizations
            if chart_type == "Candlestick":
                fig = go.Figure(data=[go.Candlestick(
                    x=chart_data.index,
                    open=chart_data['Open'],
                    high=chart_data['High'],
                    low=chart_data['Low'],
                    close=chart_data['Close'],
                    name=symbol
                )])
            elif chart_type == "Line Chart":
                fig = go.Figure(data=[go.Scatter(
                    x=chart_data.index,
                    y=chart_data['Close'],
                    mode='lines',
                    name=f'{symbol} Close Price',
                    line=dict(color='#00d4aa', width=2),
                    hovertemplate='<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>'
                )])
            else:  # Area Chart
                fig = go.Figure(data=[go.Scatter(
                    x=chart_data.index,
                    y=chart_data['Close'],
                    fill='tonexty',
                    mode='lines',
                    name=f'{symbol} Close Price',
                    line=dict(color='#00d4aa', width=2),
                    hovertemplate='<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>'
                )])
            
            # Add moving averages using chart data
            if show_ma20 and 'MA20' in chart_data.columns:
                fig.add_trace(go.Scatter(
                    x=chart_data.index,
                    y=chart_data['MA20'],
                    mode='lines',
                    name='20-Day MA',
                    line=dict(color='orange', width=1, dash='dash'),
                    hovertemplate='<b>%{x}</b><br>20-Day MA: $%{y:.2f}<extra></extra>'
                ))
            
            if show_ma50 and 'MA50' in chart_data.columns:
                fig.add_trace(go.Scatter(
                    x=chart_data.index,
                    y=chart_data['MA50'],
                    mode='lines',
                    name='50-Day MA',
                    line=dict(color='red', width=1, dash='dash'),
                    hovertemplate='<b>%{x}</b><br>50-Day MA: $%{y:.2f}<extra></extra>'
                ))
            
            # Update layout with performance optimizations
            fig.update_layout(
                title=f"{symbol} Stock Price - {selected_period}",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=600,
                showlegend=True,
                hovermode='x unified',
                # Performance optimizations
                dragmode='pan'
            )
            
            # Optimize for large datasets
            if len(chart_data) > 1000:
                fig.update_layout(
                    xaxis=dict(
                        rangeslider=dict(visible=False),  # Disable rangeslider for performance
                        type='date'
                    )
                )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart (optimized)
            if show_volume:
                # Use sampled chart data for volume too
                vol_fig = go.Figure(data=[go.Bar(
                    x=chart_data.index,
                    y=chart_data['Volume'],
                    name='Volume',
                    marker_color='rgba(0, 212, 170, 0.6)',
                    hovertemplate='<b>%{x}</b><br>Volume: %{y:,}<extra></extra>'
                )])
                
                vol_fig.update_layout(
                    title=f"{symbol} Trading Volume",
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    height=300,
                    dragmode='pan'
                )
                
                st.plotly_chart(vol_fig, use_container_width=True)
        
        with tab2:
            st.subheader("Historical Price Data")
            
            # Show data summary for large datasets
            total_rows = len(hist_data)
            if total_rows > 500:
                st.info(f"📊 Showing {total_rows:,} data points. Large datasets are optimized for better performance.")
            
            # Prepare data for display with pagination for large datasets
            display_data = hist_data.copy()
            display_data = display_data.round(2)
            display_data.index = display_data.index.strftime('%Y-%m-%d')
            
            # Sort by date (most recent first)
            display_data = display_data.sort_index(ascending=False)
            
            # For very large datasets, show only recent data by default with option to show more
            if len(display_data) > 1000:
                show_all = st.checkbox("Show all historical data (may be slow)", value=False)
                if not show_all:
                    display_data = display_data.head(1000)
                    st.warning(f"Showing most recent 1,000 rows out of {total_rows:,} total. Check the box above to show all data.")
            
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
        
        with tab4:
            st.subheader("👁️ Your Watchlist")
            
            # Display current watchlist
            watchlist_df = get_watchlist()
            
            if not watchlist_df.empty:
                # Create columns for actions
                for idx, row in watchlist_df.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{row['Symbol']}** - {row['Company']}")
                        if row['Notes']:
                            st.caption(f"Notes: {row['Notes']}")
                        st.caption(f"Added: {row['Added Date']}")
                    
                    with col2:
                        if st.button(f"View {row['Symbol']}", key=f"view_{row['ID']}"):
                            st.rerun()
                    
                    with col3:
                        if st.button(f"Remove", key=f"remove_{row['ID']}", type="secondary"):
                            if remove_from_watchlist(row['ID']):
                                st.success(f"Removed {row['Symbol']} from watchlist")
                                st.rerun()
                    
                    st.divider()
                
                # Display watchlist table
                st.dataframe(watchlist_df.drop('ID', axis=1), use_container_width=True)
            else:
                st.info("Your watchlist is empty. Add stocks using the 'Add to Watchlist' button.")
                
        with tab5:
            st.subheader("💼 Your Portfolio")
            
            # Add new stock to portfolio
            with st.expander("➕ Add Stock to Portfolio"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Portfolio stock search with autocomplete
                    portfolio_search = st.text_input(
                        "Search Stock Symbol", 
                        placeholder="Type to search...",
                        key="portfolio_search"
                    )
                    
                    # Initialize portfolio selected symbol
                    if 'portfolio_symbol' not in st.session_state:
                        st.session_state.portfolio_symbol = ""
                    
                    # Show portfolio suggestions
                    if portfolio_search and len(portfolio_search) > 0:
                        portfolio_suggestions = get_symbol_suggestions(portfolio_search, max_suggestions=5)
                        
                        if portfolio_suggestions:
                            st.write("**Select from suggestions:**")
                            for i, suggestion in enumerate(portfolio_suggestions):
                                if st.button(
                                    suggestion, 
                                    key=f"portfolio_suggestion_{i}",
                                    help="Click to select for portfolio"
                                ):
                                    st.session_state.portfolio_symbol = extract_symbol_from_suggestion(suggestion)
                                    st.rerun()
                    
                    # Manual entry option
                    if st.button("Use Manual Entry", key="portfolio_manual"):
                        if portfolio_search:
                            st.session_state.portfolio_symbol = portfolio_search.upper().strip()
                            st.rerun()
                    
                    # Display selected symbol
                    portfolio_symbol = st.session_state.portfolio_symbol
                    if portfolio_symbol:
                        st.success(f"Selected: **{portfolio_symbol}**")
                    
                    shares = st.number_input("Number of Shares", min_value=0.0, step=0.01)
                
                with col2:
                    purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, step=0.01)
                    purchase_date = st.date_input("Purchase Date", value=datetime.now().date())
                
                if st.button("Add to Portfolio", use_container_width=True):
                    if portfolio_symbol and shares > 0 and purchase_price > 0:
                        success, message = add_to_portfolio(
                            portfolio_symbol, 
                            shares, 
                            purchase_price, 
                            datetime.combine(purchase_date, datetime.min.time())
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all fields with valid values")
            
            # Display portfolio
            portfolio_df = get_portfolio()
            
            if not portfolio_df.empty:
                # Calculate portfolio totals
                total_value = portfolio_df['Total Value'].sum()
                total_gain_loss = portfolio_df['Gain/Loss'].sum()
                total_invested = (portfolio_df['Shares'] * portfolio_df['Purchase Price']).sum()
                
                # Display portfolio summary
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Total Portfolio Value",
                        value=format_currency(total_value)
                    )
                
                with col2:
                    st.metric(
                        label="Total Gain/Loss",
                        value=format_currency(total_gain_loss),
                        delta=f"{(total_gain_loss/total_invested)*100:.2f}%" if total_invested > 0 else "0%"
                    )
                
                with col3:
                    st.metric(
                        label="Total Invested",
                        value=format_currency(total_invested)
                    )
                
                st.divider()
                
                # Format portfolio display
                display_portfolio = portfolio_df.copy()
                display_portfolio['Purchase Price'] = display_portfolio['Purchase Price'].apply(format_currency)
                display_portfolio['Current Price'] = display_portfolio['Current Price'].apply(format_currency)
                display_portfolio['Total Value'] = display_portfolio['Total Value'].apply(format_currency)
                display_portfolio['Gain/Loss'] = display_portfolio['Gain/Loss'].apply(lambda x: f"+{format_currency(x)}" if x > 0 else format_currency(x))
                
                # Display portfolio table
                st.dataframe(
                    display_portfolio.drop('ID', axis=1),
                    use_container_width=True,
                    height=400
                )
                
                # CSV download for portfolio
                csv_buffer = io.StringIO()
                portfolio_df.drop('ID', axis=1).to_csv(csv_buffer)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Portfolio as CSV",
                    data=csv_data,
                    file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Your portfolio is empty. Add stocks using the form above.")
    
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
