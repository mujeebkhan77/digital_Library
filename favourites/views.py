from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from books.models import Book
from .models import Favourite


@login_required
def toggle_favourite(request, book_id):
    """Add or remove book from favorites"""
    book = get_object_or_404(Book, id=book_id, is_approved=True)
    favourite, created = Favourite.objects.get_or_create(user=request.user, book=book)
    
    if not created:
        favourite.delete()
        messages.info(request, f'Removed "{book.title}" from favorites.')
    else:
        messages.success(request, f'Added "{book.title}" to favorites.')
    
    return redirect('book_detail', book_id=book_id)


@login_required
def favourites_list(request):
    """List all user's favorite books"""
    favourites = Favourite.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(favourites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'favourites_list.html', context)
