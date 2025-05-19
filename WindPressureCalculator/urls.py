from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculator.urls')),
    path('roof/', include('roof_calculator.urls')),
    path('hipped_roof/', include('Wind_load_analysis_on_hipped_roof.urls')),
]