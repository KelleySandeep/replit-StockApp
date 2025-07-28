import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

# Database configuration
Base = declarative_base()

def get_database_engine():
    """Get database engine with proper error handling."""
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not found")
    return create_engine(DATABASE_URL)

def get_session_local():
    """Get SessionLocal with proper error handling."""
    engine = get_database_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Models
class StockData(Base):
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    date = Column(DateTime, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    company_name = Column(String(200))
    added_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class Portfolio(Base):
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    shares = Column(Float)
    purchase_price = Column(Float)
    purchase_date = Column(DateTime)
    current_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database functions
@st.cache_resource
def init_database():
    """Initialize database tables."""
    try:
        engine = get_database_engine()
        Base.metadata.create_all(bind=engine)
        return engine
    except Exception as e:
        st.error(f"Database initialization failed: {str(e)}")
        return None

def get_db():
    """Get database session."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def store_stock_data(symbol: str, data: pd.DataFrame):
    """Store stock data in database."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        # Clear existing data for this symbol
        db.query(StockData).filter(StockData.symbol == symbol).delete()
        
        # Store new data
        for index, row in data.iterrows():
            stock_entry = StockData(
                symbol=symbol,
                date=index,
                open_price=float(row['Open']),
                high_price=float(row['High']),
                low_price=float(row['Low']),
                close_price=float(row['Close']),
                volume=int(row['Volume'])
            )
            db.add(stock_entry)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        st.error(f"Error storing stock data: {str(e)}")
        return False
    finally:
        db.close()

def get_stored_stock_data(symbol: str) -> pd.DataFrame:
    """Retrieve stored stock data from database."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        stocks = db.query(StockData).filter(StockData.symbol == symbol).order_by(StockData.date).all()
        
        if not stocks:
            return pd.DataFrame()
        
        data = []
        for stock in stocks:
            data.append({
                'Date': stock.date,
                'Open': stock.open_price,
                'High': stock.high_price,
                'Low': stock.low_price,
                'Close': stock.close_price,
                'Volume': stock.volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('Date', inplace=True)
        return df
    
    except Exception as e:
        st.error(f"Error retrieving stock data: {str(e)}")
        return pd.DataFrame()
    finally:
        db.close()

def add_to_watchlist(symbol: str, company_name: str, notes: str = ""):
    """Add stock to watchlist."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        # Check if already exists
        existing = db.query(Watchlist).filter(
            Watchlist.symbol == symbol,
            Watchlist.is_active == True
        ).first()
        
        if existing:
            return False, "Stock already in watchlist"
        
        watchlist_entry = Watchlist(
            symbol=symbol,
            company_name=company_name,
            notes=notes
        )
        db.add(watchlist_entry)
        db.commit()
        return True, "Added to watchlist"
    
    except Exception as e:
        db.rollback()
        return False, f"Error adding to watchlist: {str(e)}"
    finally:
        db.close()

def get_watchlist():
    """Get user's watchlist."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        watchlist = db.query(Watchlist).filter(Watchlist.is_active == True).order_by(Watchlist.added_date.desc()).all()
        
        data = []
        for item in watchlist:
            data.append({
                'Symbol': item.symbol,
                'Company': item.company_name,
                'Added Date': item.added_date.strftime('%Y-%m-%d'),
                'Notes': item.notes or "",
                'ID': item.id
            })
        
        return pd.DataFrame(data)
    
    except Exception as e:
        st.error(f"Error retrieving watchlist: {str(e)}")
        return pd.DataFrame()
    finally:
        db.close()

def remove_from_watchlist(watchlist_id: int):
    """Remove stock from watchlist."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        item = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
        if item:
            item.is_active = False
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        st.error(f"Error removing from watchlist: {str(e)}")
        return False
    finally:
        db.close()

def add_to_portfolio(symbol: str, shares: float, purchase_price: float, purchase_date: datetime):
    """Add stock to portfolio."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        portfolio_entry = Portfolio(
            symbol=symbol,
            shares=shares,
            purchase_price=purchase_price,
            purchase_date=purchase_date
        )
        db.add(portfolio_entry)
        db.commit()
        return True, "Added to portfolio"
    
    except Exception as e:
        db.rollback()
        return False, f"Error adding to portfolio: {str(e)}"
    finally:
        db.close()

def get_portfolio():
    """Get user's portfolio."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        portfolio = db.query(Portfolio).order_by(Portfolio.purchase_date.desc()).all()
        
        data = []
        for item in portfolio:
            data.append({
                'Symbol': item.symbol,
                'Shares': item.shares,
                'Purchase Price': item.purchase_price,
                'Purchase Date': item.purchase_date.strftime('%Y-%m-%d'),
                'Current Price': item.current_price or 0,
                'Total Value': (item.current_price or 0) * item.shares,
                'Gain/Loss': ((item.current_price or 0) - item.purchase_price) * item.shares,
                'ID': item.id
            })
        
        return pd.DataFrame(data)
    
    except Exception as e:
        st.error(f"Error retrieving portfolio: {str(e)}")
        return pd.DataFrame()
    finally:
        db.close()

def update_portfolio_prices(symbol: str, current_price: float):
    """Update current prices for portfolio holdings."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        portfolio_items = db.query(Portfolio).filter(Portfolio.symbol == symbol).all()
        for item in portfolio_items:
            item.current_price = current_price
            item.updated_at = datetime.utcnow()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        st.error(f"Error updating portfolio prices: {str(e)}")
        return False
    finally:
        db.close()