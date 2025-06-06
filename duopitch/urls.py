from django.urls import path
from . import views

app_name = 'duopitch'

urlpatterns = [
    path('', views.wind_load_calculator, name='wind_load_calculator'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('list/', views.wind_load_list, name='wind_load_list'),
    path('detail/<int:pk>/', views.wind_load_detail, name='wind_load_detail'),
    path('delete/<int:pk>/', views.wind_load_delete, name='wind_load_delete'),
]