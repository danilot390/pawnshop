from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login:logg')
def index_loan(request):
    message = f'Welcome back dear {request.user.person.name}.'
    context = {
        'message' : message,
    }
    return render(request, 'loan/index.html', context)

def box_view(request):
    pass


