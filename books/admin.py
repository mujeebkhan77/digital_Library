from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'type', 'is_approved', 'view_count', 'created_at')
    list_filter = ('category', 'type', 'is_approved', 'created_at')
    search_fields = ('title', 'author', 'description')
    list_editable = ('is_approved',)
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'description', 'category', 'type')
        }),
        ('Files', {
            'fields': ('cover_image', 'pdf_file')
        }),
        ('Status', {
            'fields': ('is_approved', 'view_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
