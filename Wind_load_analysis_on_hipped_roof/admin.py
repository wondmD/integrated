from django.contrib import admin
from .models import WindLoadCalculation

@admin.register(WindLoadCalculation)
class WindLoadCalculationAdmin(admin.ModelAdmin):
    list_display = ('calculation_name', 'vb0', 'terrain_category', 'h_e', 'h_r', 'created_at')
    list_filter = ('terrain_category', 'created_at')
    search_fields = ('calculation_name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('calculation_name', 'notes')
        }),
        ('Wind Parameters', {
            'fields': ('vb0', 'c_direction', 'c_season', 'rho')
        }),
        ('Building Parameters', {
            'fields': ('terrain_category', 'h_e', 'h_r')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
