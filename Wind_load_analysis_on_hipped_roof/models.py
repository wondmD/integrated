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
#             'terrain_category': 'Describes the surrounding environment's roughness.',
#             'h_e': 'Height from ground to the eaves of the roof.',
#             'h_r': 'Height from the eaves to the roof ridge.'
#         }

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class WindLoadCalculation(models.Model):
    TERRAIN_CHOICES = [
        ('0', '0 - Sea or coastal area'),
        ('I', 'I - Low vegetation'),
        ('II', 'II - Regular vegetation'),
        ('III', 'III - Suburban'),
        ('IV', 'IV - Urban')
    ]

    # Basic wind parameters
    vb0 = models.FloatField(
        verbose_name="Fundamental Basic Wind Velocity (V_b0)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="The 10-minute mean wind speed at 10 m above ground (m/s)"
    )
    c_direction = models.FloatField(
        verbose_name="Directional Factor (C_direction)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Factor accounting for wind direction effects"
    )
    c_season = models.FloatField(
        verbose_name="Seasonal Factor (C_season)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Factor accounting for seasonal wind variations"
    )
    rho = models.FloatField(
        verbose_name="Air Density (ρ)",
        validators=[MinValueValidator(1.0), MaxValueValidator(1.5)],
        help_text="Density of air at the site (kg/m³)"
    )
    
    # Terrain and height parameters
    terrain_category = models.CharField(
        max_length=3,
        verbose_name="Terrain Category",
        choices=TERRAIN_CHOICES,
        help_text="Describes the surrounding environment's roughness"
    )
    h_e = models.FloatField(
        verbose_name="Height to Eaves (h_e)",
        validators=[MinValueValidator(0.0)],
        help_text="Height from ground to the eaves of the roof (m)"
    )
    h_r = models.FloatField(
        verbose_name="Height from Eaves to Ridge (h_r)",
        validators=[MinValueValidator(0.0)],
        help_text="Height from the eaves to the roof ridge (m)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    calculation_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional name for this calculation"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this calculation"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Wind Load Calculation"
        verbose_name_plural = "Wind Load Calculations"

    def __str__(self):
        if self.calculation_name:
            return f"{self.calculation_name} ({self.created_at.strftime('%Y-%m-%d')})"
        return f"Calculation {self.id} ({self.created_at.strftime('%Y-%m-%d')})"

    def get_total_height(self):
        """Calculate total height from ground to ridge"""
        return self.h_e + self.h_r

    def get_terrain_description(self):
        """Get the full description of the terrain category"""
        return dict(self.TERRAIN_CHOICES).get(self.terrain_category, '')