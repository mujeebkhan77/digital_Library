from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import stripe
import logging
import os
from books.models import Book
from .models import Purchase

logger = logging.getLogger(__name__)

# Initialize Stripe API key with validation
# Priority: environment variable > settings.py
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', getattr(settings, 'STRIPE_SECRET_KEY', None))

if not STRIPE_SECRET_KEY:
    logger.error("STRIPE_SECRET_KEY is not configured. Please set it in settings.py or environment variable.")
elif not STRIPE_SECRET_KEY.startswith('sk_test_') and not STRIPE_SECRET_KEY.startswith('sk_live_'):
    logger.warning(f"Stripe secret key format may be incorrect. Key starts with: {STRIPE_SECRET_KEY[:7]}...")
else:
    # Mask key for logging (show first 6 and last 4 characters)
    masked_key = f"{STRIPE_SECRET_KEY[:6]}...{STRIPE_SECRET_KEY[-4:]}" if len(STRIPE_SECRET_KEY) > 10 else "***"
    logger.info(f"Stripe API key initialized (masked: {masked_key})")

stripe.api_key = STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, book_id):
    """
    Create Stripe Checkout Session for book purchase.
    Validates Stripe API key and handles errors gracefully.
    """
    # Validate Stripe API key is configured
    if not stripe.api_key or stripe.api_key == 'sk_test_YOUR_STRIPE_SECRET_KEY_HERE':
        logger.error("Stripe API key not properly configured")
        messages.error(request, 'Payment system is not configured. Please contact the administrator.')
        return redirect('book_detail', book_id=book_id)
    
    book = get_object_or_404(Book, id=book_id, is_approved=True)
    
    # Check if book is paid
    if book.type != 'paid':
        messages.error(request, 'This book is free and does not require payment.')
        return redirect('book_detail', book_id=book_id)
    
    # Check if user already purchased this book
    if Purchase.objects.filter(user=request.user, book=book, is_paid=True).exists():
        messages.info(request, 'You have already purchased this book.')
        return redirect('book_detail', book_id=book_id)
    
    try:
        logger.info(f"Creating Stripe checkout session for book {book_id} by user {request.user.userId}")
        
        # Build cover image URL if available
        cover_image_url = None
        if book.cover_image:
            try:
                cover_image_url = request.build_absolute_uri(book.cover_image.url)
            except Exception as e:
                logger.warning(f"Could not build cover image URL: {e}")
        
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': book.title,
                        'description': f'by {book.author}',
                        'images': [cover_image_url] if cover_image_url else [],
                    },
                    'unit_amount': 999,  # $9.99 in cents (you can make this configurable)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payment_cancelled')),
            metadata={
                'book_id': str(book.id),
                'user_id': str(request.user.id),
            },
        )
        
        # Store session ID in session for verification
        request.session['checkout_session_id'] = checkout_session.id
        request.session['book_id'] = book_id
        
        return redirect(checkout_session.url)
    
    except stripe.error.AuthenticationError as e:
        logger.exception(f"Stripe authentication error (check API key): {str(e)}")
        messages.error(request, 'Payment authentication failed. Please contact the administrator.')
        return redirect('book_detail', book_id=book_id)
    except stripe.error.InvalidRequestError as e:
        logger.exception(f"Stripe invalid request error: {str(e)}")
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('book_detail', book_id=book_id)
    except stripe.error.StripeError as e:
        logger.exception(f"Stripe API error: {str(e)}")
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('book_detail', book_id=book_id)
    except Exception as e:
        logger.exception(f"Unexpected error creating checkout session: {str(e)}")
        messages.error(request, 'An unexpected error occurred. Please try again later.')
        return redirect('book_detail', book_id=book_id)


@login_required
def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('home')
    
    try:
        # Retrieve the checkout session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Verify the session belongs to the current user
        if checkout_session.metadata.get('user_id') != str(request.user.id):
            messages.error(request, 'Payment verification failed.')
            return redirect('home')
        
        book_id = checkout_session.metadata.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        
        # Check if purchase already exists
        purchase, created = Purchase.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={
                'stripe_payment_id': checkout_session.payment_intent if checkout_session.payment_intent else session_id,
                'is_paid': True,
            }
        )
        
        if not created:
            # Update existing purchase
            purchase.stripe_payment_id = checkout_session.payment_intent if checkout_session.payment_intent else session_id
            purchase.is_paid = True
            purchase.save()
        
        messages.success(request, f'Payment successful! You can now read "{book.title}".')
        
        # Clear session data
        if 'checkout_session_id' in request.session:
            del request.session['checkout_session_id']
        if 'book_id' in request.session:
            del request.session['book_id']
        
        return render(request, 'payment_success.html', {
            'book': book,
            'purchase': purchase,
        })
    
    except stripe.error.AuthenticationError as e:
        logger.exception(f"Stripe authentication error during payment verification: {str(e)}")
        messages.error(request, 'Payment verification failed due to authentication error.')
        return redirect('home')
    except stripe.error.StripeError as e:
        logger.exception(f"Stripe API error during payment verification: {str(e)}")
        messages.error(request, f'Payment verification error: {str(e)}')
        return redirect('home')
    except Exception as e:
        logger.exception(f"Unexpected error during payment verification: {str(e)}")
        messages.error(request, 'An error occurred while verifying payment.')
        return redirect('home')


@login_required
def payment_cancelled(request):
    """Handle cancelled payment"""
    messages.info(request, 'Payment was cancelled.')
    return render(request, 'payment_cancelled.html')


@login_required
def purchased_books(request):
    """Show all books purchased by the user"""
    purchases = Purchase.objects.filter(user=request.user, is_paid=True).order_by('-purchased_at')
    
    context = {
        'purchases': purchases,
    }
    return render(request, 'purchased_books.html', context)
