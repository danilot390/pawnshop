from django.urls import path
from login.views import login_view, log_out, user_view, create_new_user_view, list_user_view

app_name = 'login'

urlpatterns = [
    path('logg/', login_view, name='logg'),
    path('logout/', log_out, name='logout'),
    path('profile/<int:id>', user_view, name='profile'),
    path('new/', create_new_user_view, name='create_new_user'),
    path('list/', list_user_view, name='list_users'),
]