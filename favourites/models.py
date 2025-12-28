from django.db import models
from django.conf import settings
from books.models import Book


class Favourite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'book']  # One favorite per user per book
    
    def __str__(self):
        return f"{self.user.userId} - {self.book.title}"
