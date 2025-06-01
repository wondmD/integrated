from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
        help_text="The 10-minute mean wind speed at 10 m above ground (m/s)",
        default=22.0
    )
    c_direction = models.FloatField(
        verbose_name="Directional Factor (C_direction)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Factor accounting for wind direction effects",
        default=1.0
    )
    c_season = models.FloatField(
        verbose_name="Seasonal Factor (C_season)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Factor accounting for seasonal wind variations",
        default=1.0
    )
    rho = models.FloatField(
        verbose_name="Air Density (ρ)",
        validators=[MinValueValidator(1.0), MaxValueValidator(1.5)],
        help_text="Density of air at the site (kg/m³)",
        default=1.25
    )
    
    # Terrain and height parameters
    terrain_category = models.CharField(
        max_length=3,
        verbose_name="Terrain Category",
        choices=TERRAIN_CHOICES,
        help_text="Describes the surrounding environment's roughness",
        default='II'
    )
    ridge_height = models.FloatField(
        verbose_name="Ridge Height (h)",
        validators=[MinValueValidator(0.0)],
        help_text="Height from ground to the roof's ridge (m)",
        default=6.1
    )

    # Building geometry
    building_length = models.FloatField(
        verbose_name="Building Length (L)",
        validators=[MinValueValidator(0.0)],
        help_text="Length of the building parallel to the ridge (m)",
        default=30.0
    )
    building_width = models.FloatField(
        verbose_name="Building Width (b)",
        validators=[MinValueValidator(0.0)],
        help_text="Width of the building perpendicular to the ridge (m)",
        default=12.0
    )
    pitch_angle = models.FloatField(
        verbose_name="Pitch Angle (α)",
        validators=[MinValueValidator(-75.0), MaxValueValidator(75.0)],
        help_text="Angle of the roof slope relative to horizontal (degrees)",
        default=15.0
    )

    # Site parameters
    site_altitude = models.FloatField(
        verbose_name="Site Altitude",
        validators=[MinValueValidator(0.0)],
        help_text="Elevation of the site above sea level (m)",
        default=1650.0
    )
    upwind_slope = models.FloatField(
        verbose_name="Upwind Slope (φ)",
        validators=[MinValueValidator(0.0)],
        help_text="Slope of the terrain upwind of the building",
        default=0.06
    )
    horizontal_distance = models.FloatField(
        verbose_name="Horizontal Distance from Crest",
        validators=[MinValueValidator(0.0)],
        help_text="Distance from building to crest of upwind terrain (m)",
        default=-200.0
    )
    effective_height = models.FloatField(
        verbose_name="Effective Height of Crest",
        validators=[MinValueValidator(0.0)],
        help_text="Height of upwind terrain crest relative to site (m)",
        default=30.0
    )
    upwind_slope_length = models.FloatField(
        verbose_name="Upwind Slope Length",
        validators=[MinValueValidator(0.0)],
        help_text="Length of the upwind terrain slope (m)",
        default=500.0
    )

    # Opening parameters
    windward_openings_area = models.FloatField(
        verbose_name="Windward Openings Area",
        validators=[MinValueValidator(0.0)],
        help_text="Total area of openings on windward face (m²)",
        default=41.25
    )
    leeward_openings_area = models.FloatField(
        verbose_name="Leeward Openings Area",
        validators=[MinValueValidator(0.0)],
        help_text="Total area of openings on leeward face (m²)",
        default=41.25
    )
    parallel_openings_area = models.FloatField(
        verbose_name="Parallel Openings Area",
        validators=[MinValueValidator(0.0)],
        help_text="Total area of openings on parallel faces (m²)",
        default=37.0
    )

    # Structural parameters
    structural_factor = models.FloatField(
        verbose_name="Structural Factor (c_s c_d)",
        validators=[MinValueValidator(0.0)],
        help_text="Factor accounting for building's dynamic response",
        default=1.0
    )
    purlin_spacing = models.FloatField(
        verbose_name="Purlin Spacing",
        validators=[MinValueValidator(0.0)],
        help_text="Distance between purlins supporting the roof (m)",
        default=1.5525
    )
    truss_spacing = models.FloatField(
        verbose_name="Truss Spacing",
        validators=[MinValueValidator(0.0)],
        help_text="Distance between trusses supporting the roof (m)",
        default=3.0
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

    def get_terrain_description(self):
        """Get the full description of the terrain category"""
        return dict(self.TERRAIN_CHOICES).get(self.terrain_category, '')
