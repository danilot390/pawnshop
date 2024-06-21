from django.urls import path
from box.views import *

app_name = 'box'

urlpatterns = [
    path('box', box_view, name='box',),
    path('recharge', recharge_box, name='recharge'),
    path('recharge_p', recharge_box_post, name='recharge_post'),
    path('expenses_box', expenses_box_view, name='expenses_box'),
    path('expenses_p', expenses_box_post, name='expenses_post')
]