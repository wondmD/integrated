from django import forms

class WindPressureForm(forms.Form):
    height = forms.FloatField(label='Height (h, m)', min_value=0, initial=19.871)
    in_wind_depth = forms.FloatField(label='In-wind Depth (b, m)', min_value=0, initial=30.6)
    width = forms.FloatField(label='Width (d, m)', min_value=0, initial=19.26)
    site_altitude = forms.FloatField(label='Site Altitude (h_o, m)', min_value=0, initial=0)
    terrain_category = forms.ChoiceField(
        label='Terrain Category',
        choices=[(1, '1 (Sea, flat country)'), (2, '2 (Farmland, hedges)'),
                 (3, '3 (Suburban, forests)'), (4, '4 (Urban, skyscrapers)')],
        initial=3
    )
    upwind_slope = forms.FloatField(label='Upwind Slope (ø)', min_value=0, initial=0)
    orographic_factor = forms.FloatField(label='Orographic Factor (s)', min_value=0, initial=0)
    structural_factor = forms.FloatField(label='Structural Factor (C_sC_d)', min_value=0, initial=1)
    windward_openings = forms.IntegerField(label='Windward Openings (n_1)', min_value=0, initial=24)
    leeward_openings = forms.IntegerField(label='Leeward Openings (n_2)', min_value=0, initial=1)
    parallel_openings = forms.IntegerField(label='Parallel Openings (n_3)', min_value=0, initial=5)
    windward_area = forms.FloatField(label='Windward Area (A_w, mm²)', min_value=0, initial=1.7514)
    leeward_area = forms.FloatField(label='Leeward Area (A_l, mm²)', min_value=0, initial=37.43)
    parallel_area = forms.FloatField(label='Parallel Area (A_p, mm²)', min_value=0, initial=1.7514)
    internal_pressure_coeff = forms.FloatField(label='Internal Pressure Coefficient (C_pi)', initial=0.35)
    basic_wind_velocity = forms.FloatField(label='Basic Wind Velocity (V_b,o, m/s)', min_value=0, initial=22)

class DuoPitchRoofForm(forms.Form):
    height = forms.FloatField(label='Ridge Height (h, m)', min_value=0, initial=6.1)
    in_wind_depth = forms.FloatField(label='In-wind Depth (b, m)', min_value=0, initial=12)
    width = forms.FloatField(label='Width (d, m)', min_value=0, initial=30)
    pitch_angle = forms.FloatField(label='Pitch Angle (α, degrees)', min_value=-75, max_value=75, initial=15)
    site_altitude = forms.FloatField(label='Site Altitude (h_o, m)', min_value=0, initial=0)
    terrain_category = forms.ChoiceField(
        label='Terrain Category',
        choices=[(1, '1 (Sea, flat country)'), (2, '2 (Farmland, hedges)'),
                 (3, '3 (Suburban, forests)'), (4, '4 (Urban, skyscrapers)')],
        initial=3
    )
    upwind_slope = forms.FloatField(label='Upwind Slope (ø)', min_value=0, initial=0.06)
    orographic_distance = forms.FloatField(label='Distance from Crest (x, m)', initial=-200)
    effective_height = forms.FloatField(label='Effective Terrain Height (H, m)', min_value=0, initial=30)
    upwind_length = forms.FloatField(label='Upwind Slope Length (L_u, m)', min_value=0, initial=500)
    structural_factor = forms.FloatField(label='Structural Factor (C_sC_d)', min_value=0, initial=1)
    windward_openings_long = forms.IntegerField(label='Long Side Openings (Windows)', min_value=0, initial=6)
    windward_opening_area_long = forms.FloatField(label='Long Side Window Area (m²)', min_value=0, initial=6.875)
    windward_openings_short = forms.IntegerField(label='Short Side Openings (Windows)', min_value=0, initial=2)
    windward_opening_area_short = forms.FloatField(label='Short Side Window Area (m²)', min_value=0, initial=5.5)
    door_openings_short = forms.IntegerField(label='Short Side Doors', min_value=0, initial=1)
    door_area_short = forms.FloatField(label='Short Side Door Area (m²)', min_value=0, initial=7.5)
    truss_spacing = forms.FloatField(label='Truss Spacing (m)', min_value=0, initial=3)
    purlin_spacing = forms.FloatField(label='Purlin Spacing (m)', min_value=0, initial=1.5525)
    basic_wind_velocity = forms.FloatField(label='Basic Wind Velocity (V_b,o, m/s)', min_value=0, initial=22)