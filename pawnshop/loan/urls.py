from django.urls import path
from loan.views import *

app_name = 'loan'

urlpatterns = [
    path('', index_loan, name='loan_index'),
]