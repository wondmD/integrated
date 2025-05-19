from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wall/', include('calculator.urls')),
    path('roof/', include('roof_calculator.urls')),
    path('', include('home.urls')),
    path('monopitch/', include('monopitch.urls')),
    path('flatroof/', include('flatroof.urls')),
    path('duopitch/', include('duopitch.urls')),
    path('hipped_roof/', include('Wind_load_analysis_on_hipped_roof.urls')),
]
