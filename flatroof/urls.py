from django.urls import path
from . import views



urlpatterns = [
    path('', views.flatroof_calculate, name='flatroof_calculate'),
]