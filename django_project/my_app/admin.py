from django.contrib import admin
from .models import Stock, UserProfile, StockHistory

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'current_price', 'last_updated')
    search_fields = ('symbol', 'name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('favorite_stocks',)

@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'open_price', 'close_price', 'high', 'low', 'volume')
    list_filter = ('stock', 'date')
    date_hierarchy = 'date'