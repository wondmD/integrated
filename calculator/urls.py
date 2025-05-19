from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculate, name='wall_calculate'),
   
]