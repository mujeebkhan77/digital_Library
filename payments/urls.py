from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:book_id>/', views.create_checkout_session, name='create_checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('purchased/', views.purchased_books, name='purchased_books'),
]

