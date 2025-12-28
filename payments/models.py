from django.db import models
from django.conf import settings
from books.models import Book


class Purchase(models.Model):
    """Model to track book purchases via Stripe"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='purchases')
    stripe_payment_id = models.CharField(max_length=255, unique=True)
    is_paid = models.BooleanField(default=True)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-purchased_at']
        unique_together = ['user', 'book']  # User can only purchase a book once
    
    def __str__(self):
        return f"{self.user.userId} - {self.book.title}"
