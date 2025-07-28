# Stock Analysis Dashboard

## Overview

This is a Streamlit-based web application for stock market analysis. The application provides comprehensive financial data visualization and interactive charts for any stock symbol using the Yahoo Finance API. Users can analyze stock performance across different time periods with professional-grade charts and metrics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - A Python-based web framework for rapid development of data applications
- **UI Components**: Native Streamlit widgets including sidebar inputs, selectboxes, and text inputs
- **Layout**: Wide layout with expandable sidebar for better data visualization space
- **Styling**: Built-in Streamlit theming with custom page configuration

### Backend Architecture
- **Language**: Python
- **Data Processing**: Pandas and NumPy for data manipulation and numerical operations
- **API Integration**: Yahoo Finance (yfinance) for real-time and historical stock data
- **Visualization**: Plotly for interactive charts and graphs
- **Database**: PostgreSQL with SQLAlchemy ORM for data persistence
- **Caching**: Streamlit caching for performance optimization

### Data Visualization
- **Charting Library**: Plotly Graph Objects and Plotly Express
- **Chart Types**: Support for multiple chart types including line charts, candlestick charts, and subplots
- **Interactivity**: Interactive charts with zoom, pan, and hover capabilities

## Key Components

### Core Application (`app.py`)
- Main Streamlit application entry point
- User interface configuration and layout
- Stock symbol input validation and processing
- Time period selection functionality
- Integration point for data fetching and visualization
- Database-integrated watchlist and portfolio management

### Database Layer (`database.py`)
- **PostgreSQL Integration**: SQLAlchemy models for stock data, watchlist, and portfolio
- **Data Persistence**: Store historical stock data for offline analysis
- **Watchlist Management**: Add, view, and remove stocks from personal watchlist
- **Portfolio Tracking**: Add holdings and track performance with real-time updates
- **Session Management**: Proper database connection handling with error recovery

### Utility Functions (`utils.py`)
- **Currency Formatting**: Intelligent formatting of financial values with appropriate suffixes (K, M, B, T)
- **Number Formatting**: General number formatting for large values
- **Symbol Validation**: Validation logic to ensure entered stock symbols are valid and exist

## Data Flow

1. **User Input**: User enters stock symbol and selects time period via sidebar
2. **Validation**: Symbol is validated using Yahoo Finance API
3. **Data Fetching**: Historical and real-time stock data retrieved from Yahoo Finance
4. **Database Integration**: Option to store historical data for offline analysis
5. **Processing**: Raw data processed and formatted using utility functions
6. **Visualization**: Processed data rendered as interactive charts using Plotly
7. **Personal Management**: Add stocks to watchlist or portfolio with database persistence
8. **Display**: Results presented in the main dashboard with personalized tracking

## External Dependencies

### Primary Libraries
- **streamlit**: Web application framework
- **yfinance**: Yahoo Finance API wrapper for stock data
- **plotly**: Interactive visualization library
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **sqlalchemy**: Database ORM for PostgreSQL integration
- **psycopg2-binary**: PostgreSQL adapter for Python

### Data Sources
- **Yahoo Finance**: Primary data source for stock prices, financial metrics, and company information
- **Real-time Data**: Current stock prices and market data
- **Historical Data**: Historical price data for trend analysis

## Deployment Strategy

### Development Environment
- Python-based application suitable for local development
- Streamlit's built-in development server for testing
- Hot-reloading support for rapid iteration

### Production Considerations
- Streamlit Cloud deployment ready
- Can be containerized with Docker
- Environment variables for configuration management
- Caching strategies for improved performance with large datasets

### Scalability
- Stateless application design allows for horizontal scaling
- API rate limiting considerations for Yahoo Finance
- Client-side chart rendering reduces server load
- Streamlit's session state management for user interactions

## Technical Decisions

### Framework Choice
- **Streamlit** chosen for rapid prototyping and deployment of data applications
- Native support for Python data science libraries
- Built-in responsive design and mobile compatibility

### Data Source
- **Yahoo Finance** selected for comprehensive, free financial data
- Real-time and historical data availability
- No API key requirements for basic usage

### Visualization Strategy
- **Plotly** chosen over matplotlib for interactive capabilities
- Client-side rendering for better performance
- Professional financial chart types (candlestick, OHLC)

### Code Organization
- Separation of concerns with utility functions in dedicated module
- Database layer abstraction for clean data persistence
- Modular design for easy extension and maintenance
- Clear naming conventions and type hints for better code quality

## Recent Changes (July 28, 2025)

### Database Integration
- Added PostgreSQL database with SQLAlchemy ORM
- Implemented three main data models: StockData, Watchlist, Portfolio
- Created database management functions with proper error handling
- Added session management with automatic connection cleanup

### Enhanced Features
- **Watchlist Management**: Users can save stocks for quick access and monitoring
- **Portfolio Tracking**: Add stock holdings with purchase details and track performance
- **Data Persistence**: Store historical stock data for offline analysis
- **Real-time Updates**: Portfolio values update automatically with current stock prices
- **Enhanced UI**: Added 5 tabs including new Watchlist and Portfolio sections

### Technical Improvements
- Fixed caching issues with stock data retrieval
- Improved error handling for database operations
- Added comprehensive data validation and user feedback
- Implemented CSV export functionality for portfolio data

### Smart Search & Autocomplete (July 28, 2025)
- **Intelligent Stock Search**: Real-time autocomplete as you type stock symbols or company names
- **Fuzzy Matching**: Find closest matches when exact symbols aren't found using advanced algorithms
- **Comprehensive Database**: 200+ popular stocks across all major sectors and ETFs
- **Smart Suggestions**: Click-to-select suggestions that update instantly
- **Portfolio Search**: Autocomplete functionality when adding stocks to portfolio
- **Enhanced UX**: Search shows suggestions, company names, and confidence scores for matches

### Performance Optimizations (July 28, 2025)
- **Smart Data Sampling**: For "max" period, intelligently samples data keeping recent data dense and older data sparse
- **Chart Optimization**: Large datasets are automatically sampled for chart rendering to improve performance
- **Enhanced Caching**: Extended cache times for historical data (1 hour) and stock info (10 minutes)
- **Progressive Loading**: Shows loading messages specific to data size and expected wait time
- **Data Pagination**: Large datasets show recent 1,000 rows by default with option to show all
- **Chart Performance**: Disabled range slider and optimized hover templates for large datasets
- **Memory Management**: Limits maximum data points to prevent memory issues while maintaining data quality

### History & Comparison Features (July 28, 2025)
- **Stock Viewing History**: Automatically tracks all previously analyzed stocks with timestamps and view counts
- **Quick Actions**: One-click buttons to re-analyze stocks from history or add them to comparison
- **Stock Comparison Tool**: Side-by-side analysis of two stocks with normalized performance charts
- **Performance Metrics**: Compare key financial metrics, returns, and visual performance over 1-year period
- **Quick Compare**: Fast comparison selection from recently viewed stocks in history
- **History Management**: View detailed history table with price tracking and clear history option
- **Intelligent Tracking**: Stores last price, time period used, and company names for comprehensive history