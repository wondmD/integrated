from django.contrib import admin
from .models import WindLoadCalculation

@admin.register(WindLoadCalculation)
class WindLoadCalculationAdmin(admin.ModelAdmin):
    list_display = ('calculation_name', 'vb0', 'terrain_category', 'ridge_height', 'pitch_angle', 'created_at')
    list_filter = ('terrain_category', 'created_at')
    search_fields = ('calculation_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('calculation_name', 'notes')
        }),
        ('Wind Parameters', {
            'fields': ('vb0', 'c_direction', 'c_season', 'rho')
        }),
        ('Building Parameters', {
            'fields': ('terrain_category', 'ridge_height', 'building_length', 'building_width', 'pitch_angle')
        }),
        ('Site Parameters', {
            'fields': ('site_altitude', 'upwind_slope', 'horizontal_distance', 'effective_height', 'upwind_slope_length')
        }),
        ('Opening Parameters', {
            'fields': ('windward_openings_area', 'leeward_openings_area', 'parallel_openings_area')
        }),
        ('Structural Parameters', {
            'fields': ('structural_factor', 'purlin_spacing', 'truss_spacing')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
