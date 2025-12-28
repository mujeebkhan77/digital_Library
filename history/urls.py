from django.urls import path
from . import views

urlpatterns = [
    path('', views.reading_history, name='reading_history'),
]

