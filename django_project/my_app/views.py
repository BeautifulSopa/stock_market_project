from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Stock, UserProfile, StockHistory
from .utils import fetch_stock_data
from django.db import models
import json
import datetime

def home(request):
    # Get all stocks, or fetch default ones if none exist
    stocks = Stock.objects.all()
    if not stocks:
        from .utils import fetch_multiple_stocks
        default_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        fetch_multiple_stocks(default_stocks)
        stocks = Stock.objects.all()
    
    context = {
        'stocks': stocks,
        'page_title': 'Stock Market Dashboard'
    }
    return render(request, 'home/web.html', context)

def stock_detail(request, symbol):
    try:
        stock = Stock.objects.get(symbol=symbol.upper())
        # Update the stock data if it's stale
        if stock.needs_update():
            from .utils import fetch_stock_data
            stock = fetch_stock_data(symbol.upper())
    except Stock.DoesNotExist:
        from .utils import fetch_stock_data
        stock = fetch_stock_data(symbol.upper())
        if not stock:
            from django.http import Http404
            raise Http404(f"Stock with symbol {symbol} not found")
    
    # Get the last 30 days of data
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=30)
    
    history = stock.history.filter(date__range=(start_date, end_date))
    
    # Prepare data for charts
    dates = [h.date.strftime('%Y-%m-%d') for h in history]
    prices = [float(h.close_price) for h in history]
    
    context = {
        'stock': stock,
        'history': history,
        'chart_dates': json.dumps(dates),
        'chart_prices': json.dumps(prices),
    }
    return render(request, 'stock/detail.html', context)

@login_required
def add_to_favorites(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.favorite_stocks.add(stock)
    return redirect('stock_detail', symbol=symbol)

@login_required
def remove_from_favorites(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    profile = get_object_or_404(UserProfile, user=request.user)
    profile.favorite_stocks.remove(stock)
    return redirect('stock_detail', symbol=symbol)

def search_stocks(request):
    query = request.GET.get('q', '')
    stocks = []
    message = None
    
    if query:
        # First check if we already have this stock
        stocks = Stock.objects.filter(
            models.Q(symbol__icontains=query) | 
            models.Q(name__icontains=query)
        )
        
        # If the exact symbol is not found, try to fetch it
        if query.upper() not in [s.symbol for s in stocks]:
            from .utils import fetch_stock_data
            new_stock = fetch_stock_data(query.upper())
            if new_stock:
                # Refresh the query to include the new stock
                stocks = Stock.objects.filter(
                    models.Q(symbol__icontains=query) | 
                    models.Q(name__icontains=query)
                )
                message = f"Added new stock: {new_stock.name} ({new_stock.symbol})"
    
    context = {
        'stocks': stocks,
        'query': query,
        'message': message
    }
    return render(request, 'stock/search.html', context)