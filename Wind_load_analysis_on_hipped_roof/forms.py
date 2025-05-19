from django import forms
from .models import WindLoadInput

class WindLoadInputForm(forms.ModelForm):
    class Meta:
        model = WindLoadInput
        fields = ['vb0', 'c_direction', 'c_season', 'rho', 'terrain_category', 'h_e', 'h_r']