from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__userId', 'book__title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'book', 'rating', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
