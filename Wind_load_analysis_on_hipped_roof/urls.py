# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.wind_load_analysis_on_hipped_roof, name='wind_load_analysis_on_hipped_roof'),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.wind_load_analysis_on_hipped_roof, name='wind_load_analysis_on_hipped_roof'),
]