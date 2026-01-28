from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """Vista del dashboard principal del CRM."""
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)
