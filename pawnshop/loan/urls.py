from django.urls import path
from loan import views

app_name = 'loan'

urlpatterns = [
    path('', views.index_loan, name='loan_index'),
    path('loan/', views.loan_view, name='loan'),
    path('check_person/', views.check_person_post, name='check_person'),
    path('person/<str:ci>', views.person_view, name='person'),
    path('person_post/', views.create_person, name='create_person'),
    path('loan_p/<int:id_person>', views.loan_post, name='loan_post'),
    path('contracts/<int:id>', views.save_contracts, name='save_contracts'),
    path('list_loans', views.list_loans, name='list_loans'),
    path('loan_detail/<int:id>', views.loan_detail, name='loan_detail'),
    path('loan_paid/<int:id>', views.loan_paid, name='loan_paid'),
    path('loan_renewal/<int:id>', views.loan_renewal, name='loan_renewal'),
    path('list_havings/', views.list_havings, name='list_havings'),
    path('article_purchase/<int:id>', views.article_sell, name='article_purchase'),
    path('black_list/', views.black_list, name='black_list'),
    path('add_black_list/', views.add_black_list, name='add_black_list'),
    path('delete_black_list/<int:id>', views.delete_black_list, name='delete_black_list'),
]   