from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    def needs_update(self):
        """Check if the stock data needs updating (older than 1 hour)"""
        from django.utils import timezone
        if not self.last_updated:
            return True
        return (timezone.now() - self.last_updated).total_seconds() > 3600

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_stocks = models.ManyToManyField(Stock, blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"

class StockHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='history')
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    
    class Meta:
        unique_together = ['stock', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.stock.symbol} on {self.date}"