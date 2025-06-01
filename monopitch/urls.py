from django.urls import path
from . import views

urlpatterns = [
    path('', views.wind_load_analysis_on_monopitch_roof, name='monopitch_calculate'),
   
]