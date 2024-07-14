from django.urls import path
from mydocuments.views import *

app_name = 'mydocuments'

urlpatterns = [
    path('purchase_sale/<id>', contract_view, name='contract_pdf'),
]