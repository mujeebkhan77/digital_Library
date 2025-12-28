from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from books.models import Book
from .models import Review


@login_required
def add_review(request, book_id):
    """Add a review for a book"""
    book = get_object_or_404(Book, id=book_id, is_approved=True)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, 'Please provide both rating and comment.')
            return redirect('book_detail', book_id=book_id)
        
        # Check if user already reviewed this book
        review, created = Review.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'rating': int(rating), 'comment': comment}
        )
        
        if not created:
            # Update existing review
            review.rating = int(rating)
            review.comment = comment
            review.save()
            messages.success(request, 'Review updated successfully!')
        else:
            messages.success(request, 'Review added successfully!')
    
    return redirect('book_detail', book_id=book_id)


@login_required
def edit_review(request, review_id):
    """Edit a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            review.rating = int(rating)
            review.comment = comment
            review.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('book_detail', book_id=review.book.id)
        else:
            messages.error(request, 'Please provide both rating and comment.')
    
    context = {
        'review': review,
        'book': review.book,
    }
    return render(request, 'edit_review.html', context)


@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    book_id = review.book.id
    review.delete()
    messages.success(request, 'Review deleted successfully!')
    return redirect('book_detail', book_id=book_id)
