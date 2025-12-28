from django.db import models
from django.conf import settings


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('Science', 'Science'),
        ('Engineering', 'Engineering'),
        ('Fiction', 'Fiction'),
        ('Computer Science', 'Computer Science'),
        ('Islamiyat', 'Islamiyat'),
        ('History', 'History'),
        ('Biography', 'Biography'),
        ('Literature', 'Literature'),
    ]
    
    TYPE_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='free')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True, help_text='Optional cover image for the book')
    pdf_file = models.FileField(upload_to='pdfs/')
    is_approved = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_total_reads(self):
        """Get total number of times this book has been read"""
        return self.readinghistory_set.count()
    
    def get_total_favorites(self):
        """Get total number of users who favorited this book"""
        return self.favourite_set.count()
    
    def get_average_rating(self):
        """Get average rating for this book"""
        reviews = self.review_set.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0
