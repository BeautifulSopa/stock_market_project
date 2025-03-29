from django.core.management.base import BaseCommand
from my_app.models import Stock
from my_app.utils import fetch_stock_data, fetch_multiple_stocks
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update stock data from Yahoo Finance'

    def add_arguments(self, parser):
        parser.add_argument('--symbols', nargs='+', type=str, help='Specific stock symbols to update')

    def handle(self, *args, **options):
        symbols = options.get('symbols')
        
        if symbols:
            self.stdout.write(f"Updating data for {len(symbols)} stocks...")
            fetch_multiple_stocks(symbols)
        else:
            # Update all stocks in the database
            existing_stocks = Stock.objects.all().values_list('symbol', flat=True)
            if existing_stocks:
                self.stdout.write(f"Updating all {len(existing_stocks)} stocks in database...")
                fetch_multiple_stocks(existing_stocks)
            else:
                # Default stocks if database is empty
                default_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
                self.stdout.write(f"No stocks in database. Adding default stocks: {', '.join(default_stocks)}")
                fetch_multiple_stocks(default_stocks)
        
        self.stdout.write(self.style.SUCCESS('Successfully updated stock data')) # noqa: F821   
        
        # Log the completion
        logger.info("Stock data update completed successfully")
# Note: The noqa comment is used to suppress the F821 error for self.style.SUCCESS