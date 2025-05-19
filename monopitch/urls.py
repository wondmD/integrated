from django.urls import path
from . import views

urlpatterns = [
    path('', views.monopitch_calculate, name='monopitch_calculate'),
   
]