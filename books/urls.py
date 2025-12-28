from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('books/', views.book_list_view, name='book_list'),
    path('books/<int:book_id>/', views.book_detail_view, name='book_detail'),
    path('books/<int:book_id>/read/', views.read_book_view, name='read_book'),
    path('books/<int:book_id>/pdf/', views.serve_pdf, name='serve_pdf'),
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/books/', views.admin_book_list, name='admin_book_list'),
    path('admin/books/add/', views.admin_add_book, name='admin_add_book'),
    path('admin/books/<int:book_id>/edit/', views.admin_edit_book, name='admin_edit_book'),
    path('admin/books/<int:book_id>/delete/', views.admin_delete_book, name='admin_delete_book'),
    path('admin/books/<int:book_id>/approve/', views.admin_approve_book, name='admin_approve_book'),
    path('admin/reviews/', views.admin_review_list, name='admin_review_list'),
    path('admin/reviews/<int:review_id>/delete/', views.admin_delete_review, name='admin_delete_review'),
]

