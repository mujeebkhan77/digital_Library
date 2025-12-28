from django.contrib import admin
from .models import ReadingHistory


@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'first_read_at', 'last_read_at')
    list_filter = ('first_read_at', 'last_read_at')
    search_fields = ('user__userId', 'book__title')
    readonly_fields = ('first_read_at', 'last_read_at')
