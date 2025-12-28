from django.urls import path
from . import views

urlpatterns = [
    path('toggle/<int:book_id>/', views.toggle_favourite, name='toggle_favourite'),
    path('', views.favourites_list, name='favourites_list'),
]

