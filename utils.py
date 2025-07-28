import streamlit as st
import yfinance as yf
from typing import Dict, Any

def format_currency(value: float) -> str:
    """Format a number as currency."""
    if value is None or value == 0:
        return "N/A"
    
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

def format_number(value: float) -> str:
    """Format a large number with appropriate suffixes."""
    if value is None or value == 0:
        return "N/A"
    
    if value >= 1e12:
        return f"{value/1e12:.2f}T"
    elif value >= 1e9:
        return f"{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"{value/1e6:.2f}M"
    elif value >= 1e3:
        return f"{value/1e3:.2f}K"
    else:
        return f"{value:,.0f}"

def validate_symbol(symbol: str) -> bool:
    """Validate if a stock symbol exists."""
    try:
        # Try to get basic info for the symbol
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if we got valid data
        if info is None or len(info) == 0:
            return False
        
        # Check for common indicators of invalid symbols
        if info.get('regularMarketPrice') is None and info.get('currentPrice') is None:
            return False
        
        return True
    except Exception:
        return False

@st.cache_data(ttl=600)  # Cache for 10 minutes for better performance
def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Get stock information with caching."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info if info else {}
    except Exception as e:
        st.warning(f"Could not fetch detailed stock information: {str(e)}")
        return {}

@st.cache_data(ttl=3600)  # Cache historical data for 1 hour
def get_stock_history(symbol: str, period: str) -> Any:
    """Get stock historical data with aggressive caching for performance."""
    try:
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period)
        return hist_data
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return None

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_stock_history_optimized(symbol: str, period: str, max_rows: int = 1000) -> Any:
    """Get optimized stock historical data with row limits for better performance."""
    try:
        ticker = yf.Ticker(symbol)
        
        # For max period, limit the data to improve performance
        if period == "max":
            # Get data in chunks to avoid memory issues
            hist_data = ticker.history(period="max")
            
            # If too much data, sample it intelligently
            if len(hist_data) > max_rows:
                # Keep recent data dense, older data sparse
                recent_data = hist_data.tail(max_rows // 2)  # Last half of max_rows for recent data
                older_data = hist_data.head(len(hist_data) - max_rows // 2)
                
                # Sample older data every nth row to reduce size
                sample_rate = max(1, len(older_data) // (max_rows // 2))
                sampled_older = older_data.iloc[::sample_rate]
                
                # Combine sampled older data with recent data
                hist_data = pd.concat([sampled_older, recent_data]).sort_index()
                
            return hist_data
        else:
            # For shorter periods, get full data
            hist_data = ticker.history(period=period)
            return hist_data
            
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return None

def calculate_technical_indicators(data):
    """Calculate technical indicators for the stock data."""
    indicators = {}
    
    if len(data) >= 14:
        # RSI calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['RSI'] = 100 - (100 / (1 + rs))
    
    if len(data) >= 20:
        # Bollinger Bands
        sma_20 = data['Close'].rolling(window=20).mean()
        std_20 = data['Close'].rolling(window=20).std()
        indicators['BB_Upper'] = sma_20 + (std_20 * 2)
        indicators['BB_Lower'] = sma_20 - (std_20 * 2)
        indicators['BB_Middle'] = sma_20
    
    return indicators

def get_financial_ratios(info: Dict[str, Any]) -> Dict[str, str]:
    """Extract and format financial ratios from stock info."""
    ratios = {}
    
    # Profitability ratios
    if info.get('returnOnEquity'):
        ratios['ROE'] = f"{info['returnOnEquity'] * 100:.2f}%"
    
    if info.get('returnOnAssets'):
        ratios['ROA'] = f"{info['returnOnAssets'] * 100:.2f}%"
    
    if info.get('profitMargins'):
        ratios['Profit Margin'] = f"{info['profitMargins'] * 100:.2f}%"
    
    # Liquidity ratios
    if info.get('currentRatio'):
        ratios['Current Ratio'] = f"{info['currentRatio']:.2f}"
    
    if info.get('quickRatio'):
        ratios['Quick Ratio'] = f"{info['quickRatio']:.2f}"
    
    # Debt ratios
    if info.get('debtToEquity'):
        ratios['Debt to Equity'] = f"{info['debtToEquity']:.2f}"
    
    return ratios
