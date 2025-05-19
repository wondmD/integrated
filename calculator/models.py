from django.db import models

class WindPressureCalculation(models.Model):
    height = models.FloatField()
    in_wind_depth = models.FloatField()
    width = models.FloatField()
    site_altitude = models.FloatField(default=0)
    terrain_category = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])
    upwind_slope = models.FloatField(default=0)
    orographic_factor = models.FloatField(default=0)
    structural_factor = models.FloatField(default=1)
    windward_openings = models.IntegerField(default=0)
    leeward_openings = models.IntegerField(default=0)
    parallel_openings = models.IntegerField(default=0)
    windward_area = models.FloatField(default=0)
    leeward_area = models.FloatField(default=0)
    parallel_area = models.FloatField(default=0)
    internal_pressure_coeff = models.FloatField(default=0)
    basic_wind_velocity = models.FloatField()
    rho = models.FloatField(null=True)
    vb = models.FloatField(null=True)
    qb = models.FloatField(null=True)
    cez = models.FloatField(null=True)
    qp = models.FloatField(null=True)
    e = models.FloatField(null=True)

    def __str__(self):
        return f"Calculation {self.id}"