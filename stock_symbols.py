import pandas as pd
import requests
import streamlit as st
from fuzzywuzzy import fuzz, process
from typing import List, Tuple
import json
import os

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_stock_symbols() -> pd.DataFrame:
    """Load stock symbols from multiple sources."""
    try:
        # Try to load from local file first
        if os.path.exists('stock_symbols.csv'):
            df = pd.read_csv('stock_symbols.csv')
            if not df.empty:
                return df
        
        # Create a comprehensive dataset from known major stocks and popular tickers
        major_stocks = [
            # Technology
            ('AAPL', 'Apple Inc.'),
            ('GOOGL', 'Alphabet Inc. Class A'),
            ('GOOG', 'Alphabet Inc. Class C'),
            ('MSFT', 'Microsoft Corporation'),
            ('AMZN', 'Amazon.com Inc.'),
            ('TSLA', 'Tesla Inc.'),
            ('META', 'Meta Platforms Inc.'),
            ('NVDA', 'NVIDIA Corporation'),
            ('NFLX', 'Netflix Inc.'),
            ('ADBE', 'Adobe Inc.'),
            ('CRM', 'Salesforce Inc.'),
            ('ORCL', 'Oracle Corporation'),
            ('CSCO', 'Cisco Systems Inc.'),
            ('INTC', 'Intel Corporation'),
            ('AMD', 'Advanced Micro Devices Inc.'),
            ('PYPL', 'PayPal Holdings Inc.'),
            ('UBER', 'Uber Technologies Inc.'),
            ('SNAP', 'Snap Inc.'),
            ('TWTR', 'Twitter Inc.'),
            ('SPOT', 'Spotify Technology S.A.'),
            
            # Finance
            ('JPM', 'JPMorgan Chase & Co.'),
            ('BAC', 'Bank of America Corporation'),
            ('WFC', 'Wells Fargo & Company'),
            ('GS', 'The Goldman Sachs Group Inc.'),
            ('MS', 'Morgan Stanley'),
            ('C', 'Citigroup Inc.'),
            ('V', 'Visa Inc.'),
            ('MA', 'Mastercard Incorporated'),
            ('AXP', 'American Express Company'),
            ('BRK.A', 'Berkshire Hathaway Inc. Class A'),
            ('BRK.B', 'Berkshire Hathaway Inc. Class B'),
            
            # Healthcare
            ('JNJ', 'Johnson & Johnson'),
            ('PFE', 'Pfizer Inc.'),
            ('UNH', 'UnitedHealth Group Incorporated'),
            ('ABBV', 'AbbVie Inc.'),
            ('MRK', 'Merck & Co. Inc.'),
            ('BMY', 'Bristol Myers Squibb Company'),
            ('LLY', 'Eli Lilly and Company'),
            ('AMGN', 'Amgen Inc.'),
            ('GILD', 'Gilead Sciences Inc.'),
            ('BIIB', 'Biogen Inc.'),
            
            # Consumer Goods
            ('WMT', 'Walmart Inc.'),
            ('HD', 'The Home Depot Inc.'),
            ('MCD', 'McDonald\'s Corporation'),
            ('KO', 'The Coca-Cola Company'),
            ('PEP', 'PepsiCo Inc.'),
            ('NKE', 'NIKE Inc.'),
            ('SBUX', 'Starbucks Corporation'),
            ('TGT', 'Target Corporation'),
            ('LOW', 'Lowe\'s Companies Inc.'),
            ('COST', 'Costco Wholesale Corporation'),
            
            # Energy
            ('XOM', 'Exxon Mobil Corporation'),
            ('CVX', 'Chevron Corporation'),
            ('COP', 'ConocoPhillips'),
            ('SLB', 'Schlumberger Limited'),
            ('EOG', 'EOG Resources Inc.'),
            
            # Industrial
            ('BA', 'The Boeing Company'),
            ('CAT', 'Caterpillar Inc.'),
            ('GE', 'General Electric Company'),
            ('MMM', '3M Company'),
            ('UPS', 'United Parcel Service Inc.'),
            ('FDX', 'FedEx Corporation'),
            
            # ETFs
            ('SPY', 'SPDR S&P 500 ETF Trust'),
            ('QQQ', 'Invesco QQQ Trust'),
            ('VTI', 'Vanguard Total Stock Market ETF'),
            ('IWM', 'iShares Russell 2000 ETF'),
            ('EFA', 'iShares MSCI EAFE ETF'),
            ('GLD', 'SPDR Gold Shares'),
            
            # Additional Popular Stocks
            ('DIS', 'The Walt Disney Company'),
            ('VZ', 'Verizon Communications Inc.'),
            ('T', 'AT&T Inc.'),
            ('CMCSA', 'Comcast Corporation'),
            ('IBM', 'International Business Machines Corporation'),
            ('F', 'Ford Motor Company'),
            ('GM', 'General Motors Company'),
            ('DAL', 'Delta Air Lines Inc.'),
            ('AAL', 'American Airlines Group Inc.'),
            ('CCL', 'Carnival Corporation & plc'),
            ('ROKU', 'Roku Inc.'),
            ('ZM', 'Zoom Video Communications Inc.'),
            ('DOCU', 'DocuSign Inc.'),
            ('SHOP', 'Shopify Inc.'),
            ('SQ', 'Block Inc.'),
            ('COIN', 'Coinbase Global Inc.'),
            ('PLTR', 'Palantir Technologies Inc.'),
            ('RBLX', 'Roblox Corporation'),
            ('HOOD', 'Robinhood Markets Inc.'),
            ('RIVN', 'Rivian Automotive Inc.'),
            ('LCID', 'Lucid Group Inc.'),
            ('NIO', 'NIO Inc.'),
            ('XPEV', 'XPeng Inc.'),
            ('LI', 'Li Auto Inc.'),
            
            # Additional Tech Stocks
            ('SNOW', 'Snowflake Inc.'),
            ('CRWD', 'CrowdStrike Holdings Inc.'),
            ('ZS', 'Zscaler Inc.'),
            ('OKTA', 'Okta Inc.'),
            ('DDOG', 'Datadog Inc.'),
            ('NET', 'Cloudflare Inc.'),
            ('FSLY', 'Fastly Inc.'),
            ('TEAM', 'Atlassian Corporation'),
            ('WDAY', 'Workday Inc.'),
            ('NOW', 'ServiceNow Inc.'),
            ('SPLK', 'Splunk Inc.'),
            ('PANW', 'Palo Alto Networks Inc.'),
            ('FTNT', 'Fortinet Inc.'),
            ('CYBR', 'CyberArk Software Ltd.'),
            
            # Media & Entertainment
            ('CMCSA', 'Comcast Corporation'),
            ('VZ', 'Verizon Communications Inc.'),
            ('T', 'AT&T Inc.'),
            ('TMUS', 'T-Mobile US Inc.'),
            ('CHTR', 'Charter Communications Inc.'),
            
            # Real Estate
            ('AMT', 'American Tower Corporation'),
            ('PLD', 'Prologis Inc.'),
            ('CCI', 'Crown Castle Inc.'),
            ('EQIX', 'Equinix Inc.'),
            ('PSA', 'Public Storage'),
            
            # Utilities
            ('NEE', 'NextEra Energy Inc.'),
            ('SO', 'The Southern Company'),
            ('DUK', 'Duke Energy Corporation'),
            ('AEP', 'American Electric Power Company Inc.'),
            
            # Materials
            ('FCX', 'Freeport-McMoRan Inc.'),
            ('NUE', 'Nucor Corporation'),
            ('LIN', 'Linde plc'),
            ('APD', 'Air Products and Chemicals Inc.'),
            
            # Semiconductors
            ('TSM', 'Taiwan Semiconductor Manufacturing Company Limited'),
            ('ASML', 'ASML Holding N.V.'),
            ('QCOM', 'QUALCOMM Incorporated'),
            ('AVGO', 'Broadcom Inc.'),
            ('TXN', 'Texas Instruments Incorporated'),
            ('MU', 'Micron Technology Inc.'),
            ('LRCX', 'Lam Research Corporation'),
            ('AMAT', 'Applied Materials Inc.'),
            ('KLAC', 'KLA Corporation'),
            
            # Biotech
            ('MRNA', 'Moderna Inc.'),
            ('BNTX', 'BioNTech SE'),
            ('REGN', 'Regeneron Pharmaceuticals Inc.'),
            ('VRTX', 'Vertex Pharmaceuticals Incorporated'),
            ('ILMN', 'Illumina Inc.'),
            
            # Cryptocurrency Related
            ('MSTR', 'MicroStrategy Incorporated'),
            ('SQ', 'Block Inc.'),
            ('RIOT', 'Riot Platforms Inc.'),
            ('MARA', 'Marathon Digital Holdings Inc.'),
            
            # Retail
            ('AMZN', 'Amazon.com Inc.'),
            ('ETSY', 'Etsy Inc.'),
            ('EBAY', 'eBay Inc.'),
            ('BABA', 'Alibaba Group Holding Limited'),
            ('JD', 'JD.com Inc.'),
            ('PDD', 'PDD Holdings Inc.'),
            
            # Transportation
            ('UBER', 'Uber Technologies Inc.'),
            ('LYFT', 'Lyft Inc.'),
            ('DASH', 'DoorDash Inc.'),
            ('ABNB', 'Airbnb Inc.'),
            
            # Gaming
            ('ATVI', 'Activision Blizzard Inc.'),
            ('EA', 'Electronic Arts Inc.'),
            ('TTWO', 'Take-Two Interactive Software Inc.'),
            ('RBLX', 'Roblox Corporation'),
            ('U', 'Unity Software Inc.'),
            
            # More ETFs
            ('VOO', 'Vanguard S&P 500 ETF'),
            ('VTI', 'Vanguard Total Stock Market ETF'),
            ('VXUS', 'Vanguard Total International Stock ETF'),
            ('VEA', 'Vanguard FTSE Developed Markets ETF'),
            ('VWO', 'Vanguard FTSE Emerging Markets ETF'),
            ('BND', 'Vanguard Total Bond Market ETF'),
            ('VNQ', 'Vanguard Real Estate ETF'),
        ]
        
        # Create DataFrame
        df = pd.DataFrame(major_stocks, columns=['Symbol', 'Company'])
        
        # Save to local file for future use
        df.to_csv('stock_symbols.csv', index=False)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading stock symbols: {str(e)}")
        # Return minimal fallback data
        fallback_data = [
            ('AAPL', 'Apple Inc.'),
            ('GOOGL', 'Alphabet Inc.'),
            ('MSFT', 'Microsoft Corporation'),
            ('AMZN', 'Amazon.com Inc.'),
            ('TSLA', 'Tesla Inc.')
        ]
        return pd.DataFrame(fallback_data, columns=['Symbol', 'Company'])

def search_stocks(query: str, limit: int = 10) -> List[Tuple[str, str, int]]:
    """Search for stocks based on symbol or company name."""
    if not query:
        return []
    
    stocks_df = load_stock_symbols()
    query = query.upper().strip()
    
    # Create search strings combining symbol and company name
    stocks_df['search_string'] = stocks_df['Symbol'] + ' - ' + stocks_df['Company']
    search_list = stocks_df['search_string'].tolist()
    
    # Use fuzzy matching to find closest matches
    matches = process.extract(query, search_list, limit=limit, scorer=fuzz.partial_ratio)
    
    results = []
    for match, score in matches:
        # Extract symbol and company from the match
        parts = match.split(' - ', 1)
        if len(parts) == 2:
            symbol, company = parts
            results.append((symbol, company, score))
    
    # Also check for exact symbol matches at the beginning
    exact_matches = []
    partial_matches = []
    
    for symbol, company, score in results:
        if symbol.startswith(query):
            exact_matches.append((symbol, company, score + 50))  # Boost exact matches
        else:
            partial_matches.append((symbol, company, score))
    
    # Combine and sort by score
    all_matches = exact_matches + partial_matches
    all_matches.sort(key=lambda x: x[2], reverse=True)
    
    return all_matches[:limit]

def get_symbol_suggestions(query: str, max_suggestions: int = 5) -> List[str]:
    """Get symbol suggestions for autocomplete."""
    matches = search_stocks(query, max_suggestions)
    return [f"{symbol} - {company}" for symbol, company, _ in matches]

def extract_symbol_from_suggestion(suggestion: str) -> str:
    """Extract the symbol from a suggestion string."""
    if ' - ' in suggestion:
        return suggestion.split(' - ')[0].strip()
    return suggestion.strip().upper()