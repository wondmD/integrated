# from django import forms

# class WindLoadInputForm(forms.Form):
#     vb0 = forms.FloatField(
#         label='Fundamental Basic Wind Velocity (V_b,0, m/s)',
#         min_value=0,
#         initial=22.0,
#         help_text=(
#             "<strong>Meaning:</strong> The 10-minute mean wind speed at 10 m above ground in terrain category II, per ES EN 1991-1-4:2015 Section 4.2. "
#             "<strong>Impact:</strong> Directly influences mean wind velocity (v_m) and velocity pressures (q_b, q_p). Higher values increase wind loads."
#         )
#     )
#     c_direction = forms.FloatField(
#         label='Directional Factor (C_dir)',
#         min_value=0,
#         initial=1.0,
#         help_text=(
#             "<strong>Meaning:</strong> The factor accounting for wind direction effects, per ES EN 1991-1-4:2015 Section 4.2. "
#             "<strong>Impact:</strong> Adjusts basic wind velocity (V_b). Typically 1.0 unless site-specific data suggests otherwise."
#         )
#     )
#     c_season = forms.FloatField(
#         label='Seasonal Factor (C_season)',
#         min_value=0,
#         initial=1.0,
#         help_text=(
#             "<strong>Meaning:</strong> The factor accounting for seasonal wind variations, per ES EN 1991-1-4:2015 Section 4.2. "
#             "<strong>Impact:</strong> Modifies basic wind velocity (V_b). Typically 1.0 for annual maximum winds."
#         )
#     )
#     rho = forms.FloatField(
#         label='Air Density (ρ, kg/m³)',
#         min_value=0,
#         initial=1.25,
#         help_text=(
#             "<strong>Meaning:</strong> The density of air at the site, per ES EN 1991-1-4:2015 Section 4.5. "
#             "<strong>Impact:</strong> Affects velocity pressures (q_b, q_p). Lower values (e.g., at high altitudes) reduce wind loads."
#         )
#     )
#     terrain_category = forms.ChoiceField(
#         label='Terrain Category',
#         choices=[
#             ('0', '0 - Sea or coastal area exposed to sea winds'),
#             ('I', 'I - Lakes or flat terrain with negligible vegetation'),
#             ('II', 'II - Open terrain with scattered obstacles'),
#             ('III', 'III - Suburban or industrial areas with low-rise buildings'),
#             ('IV', 'IV - Urban areas with high-rise buildings or dense obstacles')
#         ],
#         initial='III',
#         help_text=(
#             "<strong>Meaning:</strong> The terrain category describes the surrounding environment’s roughness, per ES EN 1991-1-4:2015 Table 4.1. "
#             "<strong>Impact:</strong> Sets roughness length (z_0) and minimum height (z_min), affecting terrain factor (k_r) and roughness factor (c_r). Rougher terrains reduce wind loads."
#         )
#     )
#     h_e = forms.FloatField(
#         label='Height to Eaves (h_e, m)',
#         min_value=0,
#         initial=6.8,
#         help_text=(
#             "<strong>Meaning:</strong> The height from ground to the eaves of the roof, per ES EN 1991-1-4:2015 Section 7.2.5. "
#             "<strong>Impact:</strong> Contributes to reference height (z = h_e + h_r), affecting wind velocity (v_m) and peak pressure (q_p)."
#         )
#     )
#     h_r = forms.FloatField(
#         label='Height from Eaves to Ridge (h_r, m)',
#         min_value=0,
#         initial=2.95,
#         help_text=(
#             "<strong>Meaning:</strong> The height from the eaves to the roof ridge, per ES EN 1991-1-4:2015 Section 7.2.5. "
#             "<strong>Impact:</strong> Contributes to reference height (z = h_e + h_r), influencing wind velocity (v_m) and peak pressure (q_p)."
#         )
#     )

from django import forms
from .models import WindLoadCalculation

class WindLoadInputForm(forms.ModelForm):
    class Meta:
        model = WindLoadCalculation
        fields = ['vb0', 'c_direction', 'c_season', 'rho', 'terrain_category', 'h_e', 'h_r']
        widgets = {
            'terrain_category': forms.Select(choices=[
                ('0', '0 - Sea or coastal area'),
                ('I', 'I - Low vegetation'),
                ('II', 'II - Regular vegetation'),
                ('III', 'III - Suburban'),
                ('IV', 'IV - Urban')
            ])
        }
        labels = {
            'vb0': 'Fundamental Basic Wind Velocity (V_b0, m/s)',
            'c_direction': 'Directional Factor (C_direction)',
            'c_season': 'Seasonal Factor (C_season)',
            'rho': 'Air Density (ρ, kg/m³)',
            'terrain_category': 'Terrain Category',
            'h_e': 'Height to Eaves (h_e, m)',
            'h_r': 'Height from Eaves to Ridge (h_r, m)',
        }
        help_texts = {
            'vb0': 'The 10-minute mean wind speed at 10 m above ground.',
            'c_direction': 'Factor accounting for wind direction effects.',
            'c_season': 'Factor accounting for seasonal wind variations.',
            'rho': 'Density of air at the site.',
            'terrain_category': 'Describes the surrounding environment’s roughness.',
            'h_e': 'Height from ground to the eaves of the roof.',
            'h_r': 'Height from the eaves to the roof ridge.'
        }