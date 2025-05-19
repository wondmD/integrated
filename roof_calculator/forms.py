from django import forms

class DuopitchRoofForm(forms.Form):
    building_length = forms.FloatField(label='Building Length (L, m)', min_value=0, initial=30.0)
    building_width = forms.FloatField(label='Building Width (b, m)', min_value=0, initial=12.0)
    ridge_height = forms.FloatField(label='Ridge Height (h, m)', min_value=0, initial=6.1)
    pitch_angle = forms.FloatField(label='Pitch Angle (α, degrees)', min_value=-75, max_value=75, initial=15.0)
    site_altitude = forms.FloatField(label='Site Altitude (h_o, m)', min_value=0, initial=1650.0)
    terrain_category = forms.ChoiceField(
        label='Terrain Category',
        choices=[(1, 'I (Sea, flat country)'), (2, 'II (Farmland, hedges)'),
                 (3, 'III (Suburban, forests)'), (4, 'IV (Urban, skyscrapers)')],
        initial=3
    )
    upwind_slope = forms.FloatField(label='Upwind Slope (H/L_u)', min_value=0, initial=0.06)
    horizontal_distance = forms.FloatField(label='Horizontal Distance from Crest (x, m)', initial=-200.0)
    effective_height = forms.FloatField(label='Effective Height of Hill (H, m)', min_value=0, initial=30.0)
    upwind_slope_length = forms.FloatField(label='Upwind Slope Length (L_u, m)', min_value=0, initial=500.0)
    windward_openings_area = forms.FloatField(label='Windward Openings Area (mm²)', min_value=0, initial=41.25)
    leeward_openings_area = forms.FloatField(label='Leeward Openings Area (mm²)', min_value=0, initial=41.25)
    parallel_openings_area = forms.FloatField(label='Parallel Openings Area (mm²)', min_value=0, initial=37.0)
    purlin_spacing = forms.FloatField(label='Purlin Spacing (m)', min_value=0, initial=1.5525)
    truss_spacing = forms.FloatField(label='Truss Spacing (m)', min_value=0, initial=3.0)
    basic_wind_velocity = forms.FloatField(label='Basic Wind Velocity (V_b,o, m/s)', min_value=0, initial=22.0)
    structural_factor = forms.FloatField(label='Structural Factor (C_sC_d)', min_value=0, initial=1.0)