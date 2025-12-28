from django.contrib import admin
from .models import Favourite


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__userId', 'book__title')
    readonly_fields = ('created_at',)
