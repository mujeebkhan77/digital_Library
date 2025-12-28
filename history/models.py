from django.db import models
from django.conf import settings
from books.models import Book


class ReadingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    last_read_at = models.DateTimeField(auto_now=True)
    first_read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_read_at']
        unique_together = ['user', 'book']  # One history entry per user per book
        verbose_name_plural = 'Reading Histories'
    
    def __str__(self):
        return f"{self.user.userId} - {self.book.title} - {self.last_read_at}"
