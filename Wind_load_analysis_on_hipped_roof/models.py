from django.db import models

class WindLoadInput(models.Model):
    vb0 = models.FloatField(default=22.0, help_text="Fundamental basic wind velocity (m/s)")
    c_direction = models.FloatField(default=1.0, help_text="Directional factor")
    c_season = models.FloatField(default=1.0, help_text="Season factor")
    rho = models.FloatField(default=1.25, help_text="Air density (kg/m³)")
    terrain_category = models.CharField(
        max_length=3,
        choices=[
            ('0', '0 - Sea'),
            ('I', 'I - Low vegetation'),
            ('II', 'II - Regular vegetation'),
            ('III', 'III - Suburban'),
            ('IV', 'IV - Urban')
        ],
        default='III',
        help_text="Terrain category"
    )
    h_e = models.FloatField(help_text="Height to eaves (m)")
    h_r = models.FloatField(help_text="Height from eaves to ridge (m)")