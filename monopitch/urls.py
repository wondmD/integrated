from django.urls import path
from . import views

app_name = 'monopitch'

urlpatterns = [
    path('calculate/', views.wind_load_analysis_on_monopitch_roof, name='monopitch_calculate'),
    path('list/', views.wind_load_list, name='wind_load_list'),
    path('detail/<int:pk>/', views.wind_load_detail, name='wind_load_detail'),
]