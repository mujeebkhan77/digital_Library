from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import ReadingHistory


@login_required
def reading_history(request):
    """List user's reading history"""
    history = ReadingHistory.objects.filter(user=request.user).order_by('-last_read_at')
    
    # Pagination
    paginator = Paginator(history, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'reading_history.html', context)
