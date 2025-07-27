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

### Utility Functions (`utils.py`)
- **Currency Formatting**: Intelligent formatting of financial values with appropriate suffixes (K, M, B, T)
- **Number Formatting**: General number formatting for large values
- **Symbol Validation**: Validation logic to ensure entered stock symbols are valid and exist

## Data Flow

1. **User Input**: User enters stock symbol and selects time period via sidebar
2. **Validation**: Symbol is validated using Yahoo Finance API
3. **Data Fetching**: Historical and real-time stock data retrieved from Yahoo Finance
4. **Processing**: Raw data processed and formatted using utility functions
5. **Visualization**: Processed data rendered as interactive charts using Plotly
6. **Display**: Results presented in the main dashboard area

## External Dependencies

### Primary Libraries
- **streamlit**: Web application framework
- **yfinance**: Yahoo Finance API wrapper for stock data
- **plotly**: Interactive visualization library
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

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
- Modular design for easy extension and maintenance
- Clear naming conventions and type hints for better code quality