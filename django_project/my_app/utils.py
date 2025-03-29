import yfinance as yf
from datetime import datetime, timedelta
from .models import Stock, StockHistory
import logging
import time

logger = logging.getLogger(__name__)

def fetch_stock_data(symbol):
    """
    Fetch current and historical data for a stock symbol from Yahoo Finance
    
    Args:
        symbol (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        Stock: The updated or newly created Stock object, or None if fetching failed
    """
    try:
        # Get the stock ticker
        ticker = yf.Ticker(symbol)
        
        # Get stock info
        info = ticker.info
        
        # Update or create the stock in our database
        stock, created = Stock.objects.update_or_create(
            symbol=symbol,
            defaults={
                'name': info.get('shortName', info.get('longName', 'Unknown')),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0))
            }
        )
        
        # Get historical data for the last 90 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # Fetch historical data
        hist = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
        # Save historical data to database
        for date, row in hist.iterrows():
            StockHistory.objects.update_or_create(
                stock=stock,
                date=date.date(),
                defaults={
                    'open_price': row['Open'],
                    'close_price': row['Close'],
                    'high': row['High'],
                    'low': row['Low'],
                    'volume': row['Volume']
                }
            )
        
        logger.info(f"Successfully fetched data for {symbol}")
        return stock
    
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def fetch_multiple_stocks(symbols):
    """
    Fetch data for multiple stock symbols with rate limiting
    
    Args:
        symbols (list): List of stock symbols to fetch
        
    Returns:
        list: Successfully fetched Stock objects
    """
    results = []
    for symbol in symbols:
        stock = fetch_stock_data(symbol)
        if stock:
            results.append(stock)
        # Add a small delay to avoid hitting rate limits
        time.sleep(1)  
    return results

def get_market_indices():
    """
    Fetch current data for major market indices
    
    Returns:
        dict: Dictionary with index data
    """
    indices = {
        'S&P 500': '^GSPC',
        'Dow Jones': '^DJI',
        'NASDAQ': '^IXIC',
    }
    
    result = {}
    
    try:
        for name, symbol in indices.items():
            ticker = yf.Ticker(symbol)
            data = ticker.info
            
            # Get the current price and calculate percentage change
            current = data.get('regularMarketPrice', 0)
            previous = data.get('regularMarketPreviousClose', 0)
            
            if previous and previous > 0:
                change_pct = (current - previous) / previous * 100
            else:
                change_pct = 0
                
            result[name] = {
                'price': current,
                'change': change_pct
            }
            
            # Add delay to avoid rate limiting
            time.sleep(1)
            
        return result
    except Exception as e:
        logger.error(f"Error fetching market indices: {str(e)}")
        return {}

def get_stock_recommendations(symbol):
    """
    Get analyst recommendations for a stock
    
    Args:
        symbol (str): The stock ticker symbol
        
    Returns:
        dict: Dictionary with recommendation data
    """
    try:
        ticker = yf.Ticker(symbol)
        recommendations = ticker.recommendations
        
        if recommendations is not None and not recommendations.empty:
            # Get the most recent recommendations
            recent = recommendations.tail(5)
            
            return {
                'firm': recent.index.tolist(),
                'grades': recent['To Grade'].tolist(),
                'date': recent.index.strftime('%Y-%m-%d').tolist()
            }
        
        return {}
    except Exception as e:
        logger.error(f"Error fetching recommendations for {symbol}: {str(e)}")
        return {}