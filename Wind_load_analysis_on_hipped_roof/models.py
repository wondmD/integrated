
# from django import forms
# from .models import WindLoadCalculation

# class WindLoadInputForm(forms.ModelForm):
#     class Meta:
#         model = WindLoadCalculation
#         fields = ['vb0', 'c_direction', 'c_season', 'rho', 'terrain_category', 'h_e', 'h_r']
#         widgets = {
#             'terrain_category': forms.Select(choices=[
#                 ('0', '0 - Sea or coastal area'),
#                 ('I', 'I - Low vegetation'),
#                 ('II', 'II - Regular vegetation'),
#                 ('III', 'III - Suburban'),
#                 ('IV', 'IV - Urban')
#             ])
#         }
#         labels = {
#             'vb0': 'Fundamental Basic Wind Velocity (V_b0, m/s)',
#             'c_direction': 'Directional Factor (C_direction)',
#             'c_season': 'Seasonal Factor (C_season)',
#             'rho': 'Air Density (ρ, kg/m³)',
#             'terrain_category': 'Terrain Category',
#             'h_e': 'Height to Eaves (h_e, m)',
#             'h_r': 'Height from Eaves to Ridge (h_r, m)',
#         }
#         help_texts = {
#             'vb0': 'The 10-minute mean wind speed at 10 m above ground.',
#             'c_direction': 'Factor accounting for wind direction effects.',
#             'c_season': 'Factor accounting for seasonal wind variations.',
#             'rho': 'Density of air at the site.',
#             'terrain_category': 'Describes the surrounding environment’s roughness.',
#             'h_e': 'Height from ground to the eaves of the roof.',
#             'h_r': 'Height from the eaves to the roof ridge.'
#         }

from django.db import models

class WindLoadCalculation(models.Model):
    vb0 = models.FloatField(verbose_name="Fundamental Basic Wind Velocity (V_b0)")
    c_direction = models.FloatField(verbose_name="Directional Factor (C_direction)")
    c_season = models.FloatField(verbose_name="Seasonal Factor (C_season)")
    rho = models.FloatField(verbose_name="Air Density (ρ)")
    terrain_category = models.CharField(max_length=3, verbose_name="Terrain Category")
    h_e = models.FloatField(verbose_name="Height to Eaves (h_e)")
    h_r = models.FloatField(verbose_name="Height from Eaves to Ridge (h_r)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calculation ID: {self.id}"