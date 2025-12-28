from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, FileResponse
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import os
import logging
from .models import Book
from .decorators import admin_required
from .forms import BookForm
from users.models import User
from reviews.models import Review
from favourites.models import Favourite
from history.models import ReadingHistory
from payments.models import Purchase

logger = logging.getLogger(__name__)


def home_view(request):
    """Home page with featured books"""
    featured_books = Book.objects.filter(is_approved=True).order_by('-view_count')[:6]
    recent_books = Book.objects.filter(is_approved=True).order_by('-created_at')[:6]
    
    context = {
        'featured_books': featured_books,
        'recent_books': recent_books,
    }
    return render(request, 'home.html', context)


def book_list_view(request):
    """List all approved books with search and filters"""
    books = Book.objects.filter(is_approved=True)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        books = books.filter(category=category)
    
    # Filter by author
    author = request.GET.get('author', '')
    if author:
        books = books.filter(author__icontains=author)
    
    # Filter by type (free/paid)
    book_type = request.GET.get('type', '')
    if book_type:
        books = books.filter(type=book_type)
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique authors and categories for filters
    authors = Book.objects.filter(is_approved=True).values_list('author', flat=True).distinct()
    categories = Book.CATEGORY_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_category': category,
        'selected_author': author,
        'selected_type': book_type,
        'authors': authors,
        'categories': categories,
    }
    return render(request, 'book_list.html', context)


def book_detail_view(request, book_id):
    """Book detail page"""
    book = get_object_or_404(Book, id=book_id, is_approved=True)
    
    # Increment view count
    book.view_count += 1
    book.save(update_fields=['view_count'])
    
    # Get reviews
    reviews = Review.objects.filter(book=book).order_by('-created_at')
    
    # Check if user has favorited this book
    is_favorited = False
    user_review = None
    is_purchased = False
    if request.user.is_authenticated:
        is_favorited = Favourite.objects.filter(user=request.user, book=book).exists()
        try:
            user_review = Review.objects.get(user=request.user, book=book)
        except Review.DoesNotExist:
            pass
        # Check if user has purchased this book (for paid books)
        if book.type == 'paid':
            is_purchased = Purchase.objects.filter(user=request.user, book=book, is_paid=True).exists()
    
    context = {
        'book': book,
        'reviews': reviews,
        'is_favorited': is_favorited,
        'user_review': user_review,
        'average_rating': book.get_average_rating(),
        'is_purchased': is_purchased,
    }
    return render(request, 'book_detail.html', context)


@login_required
def read_book_view(request, book_id):
    """
    Protected PDF reader view page.
    Renders the reader template with the book and secure PDF URL.
    """
    book = get_object_or_404(Book, id=book_id, is_approved=True)
    
    # Check if book is free OR user has purchased it
    if book.type == 'paid':
        # Check if user has purchased this book
        is_purchased = Purchase.objects.filter(user=request.user, book=book, is_paid=True).exists()
        if not is_purchased:
            return render(request, 'reader.html', {
                'book': book,
                'error': 'This is a paid book. Reading restricted.'
            })
    
    # Verify PDF file exists
    if not book.pdf_file:
        logger.error(f"Book {book_id} has no PDF file attached")
        return render(request, 'reader.html', {
            'book': book,
            'error': 'PDF file not found for this book.'
        })
    
    # Check if file exists on disk
    try:
        pdf_path = book.pdf_file.path
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found at path: {pdf_path}")
            return render(request, 'reader.html', {
                'book': book,
                'error': 'PDF file not found on server.'
            })
    except Exception as e:
        logger.error(f"Error accessing PDF file for book {book_id}: {str(e)}")
        return render(request, 'reader.html', {
            'book': book,
            'error': 'Error loading PDF file.'
        })
    
    # Track reading history
    if request.user.is_authenticated:
        ReadingHistory.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={}
        )
    
    # Pass the secure PDF URL to template (not direct media URL)
    pdf_url = reverse('serve_pdf', args=[book.id])
    
    return render(request, 'reader.html', {
        'book': book,
        'pdf_url': pdf_url
    })


@login_required
def serve_pdf(request, book_id):
    """
    Protected PDF serving view with proper access control.
    Streams PDF file with security headers to prevent download/caching.
    """
    try:
        book = get_object_or_404(Book, id=book_id, is_approved=True)
        
        # Verify user authentication
        if not request.user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to book {book_id}")
            raise Http404("You must be logged in to read this book.")
        
        # Check if book is free OR user has purchased it
        if book.type == 'paid':
            is_purchased = Purchase.objects.filter(user=request.user, book=book, is_paid=True).exists()
            if not is_purchased:
                logger.warning(f"User {request.user.userId} attempted to access unpaid book {book_id}")
                raise Http404("This is a paid book. Purchase required to access.")
        
        # Get PDF file path
        if not book.pdf_file:
            logger.error(f"Book {book_id} has no PDF file attached")
            raise Http404("PDF file not found.")
        
        pdf_path = book.pdf_file.path
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found at path: {pdf_path}")
            raise Http404("PDF file not found.")
        
        # Open file properly and serve with security headers
        pdf_file = open(pdf_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        
        # Set security headers to prevent download and caching
        safe_filename = book.title.replace('"', "'").replace('\n', ' ').replace('\r', '')
        response['Content-Disposition'] = f'inline; filename="{safe_filename}.pdf"'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'  # Allow iframe embedding from same origin
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        logger.info(f"PDF served successfully for book {book_id} to user {request.user.userId}")
        return response
    
    except Http404:
        raise
    except Exception as e:
        logger.exception(f"Error serving PDF for book {book_id}: {str(e)}")
        raise Http404("An error occurred while loading the PDF.")


# Admin Views
@admin_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    total_books = Book.objects.count()
    approved_books = Book.objects.filter(is_approved=True).count()
    pending_books = Book.objects.filter(is_approved=False).count()
    total_users = User.objects.filter(role='user').count()
    total_reviews = Review.objects.count()
    total_favorites = Favourite.objects.count()
    total_reads = ReadingHistory.objects.count()
    
    # Recent books
    recent_books = Book.objects.order_by('-created_at')[:5]
    
    # Books pending approval
    pending_approval = Book.objects.filter(is_approved=False).order_by('-created_at')
    
    context = {
        'total_books': total_books,
        'approved_books': approved_books,
        'pending_books': pending_books,
        'total_users': total_users,
        'total_reviews': total_reviews,
        'total_favorites': total_favorites,
        'total_reads': total_reads,
        'recent_books': recent_books,
        'pending_approval': pending_approval,
    }
    return render(request, 'admin/dashboard.html', context)


@admin_required
def admin_book_list(request):
    """List all books for admin"""
    books = Book.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # Filter by approval status
    approval_status = request.GET.get('approval', '')
    if approval_status == 'approved':
        books = books.filter(is_approved=True)
    elif approval_status == 'pending':
        books = books.filter(is_approved=False)
    
    # Pagination
    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'approval_status': approval_status,
    }
    return render(request, 'admin/book_list.html', context)


@admin_required
def admin_add_book(request):
    """Add a new book"""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('admin_book_list')
    else:
        form = BookForm()
    
    context = {'form': form}
    return render(request, 'admin/book_form.html', context)


@admin_required
def admin_edit_book(request, book_id):
    """Edit an existing book"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('admin_book_list')
    else:
        form = BookForm(instance=book)
    
    context = {'form': form, 'book': book}
    return render(request, 'admin/book_form.html', context)


@admin_required
def admin_delete_book(request, book_id):
    """Delete a book"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted successfully!')
        return redirect('admin_book_list')
    
    context = {'book': book}
    return render(request, 'admin/book_confirm_delete.html', context)


@admin_required
def admin_approve_book(request, book_id):
    """Approve a book"""
    book = get_object_or_404(Book, id=book_id)
    book.is_approved = True
    book.save()
    messages.success(request, f'Book "{book.title}" approved successfully!')
    return redirect('admin_dashboard')


@admin_required
def admin_review_list(request):
    """List all reviews for admin management"""
    reviews = Review.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        reviews = reviews.filter(
            Q(book__title__icontains=search_query) |
            Q(user__userId__icontains=search_query) |
            Q(comment__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin/review_list.html', context)


@admin_required
def admin_delete_review(request, review_id):
    """Delete a review (admin only)"""
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('admin_review_list')
    
    context = {'review': review}
    return render(request, 'admin/review_confirm_delete.html', context)
