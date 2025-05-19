from django.urls import path
from . import views

urlpatterns = [
    path('', views.roof_calculate, name='roof_calculate'),
]