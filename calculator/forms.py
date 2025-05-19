from django import forms

class WindPressureForm(forms.Form):
    height = forms.FloatField(
        label='Height (h, m)',
        min_value=0,
        initial=19.871,
        help_text=(
            "<strong>Meaning:</strong> The height from ground to the top of the wall, per ES EN 1991-1-4:2015 Section 7.2.1. It is the reference height (z_e). "
            "<strong>Impact:</strong> Affects z_e and scaling factor (e = min(b, 2h)). Higher h increases wind velocity (v_m) and peak pressure (q_p)."
        )
    )
    in_wind_depth = forms.FloatField(
        label='In-wind Depth (b, m)',
        min_value=0,
        initial=30.6,
        help_text=(
            "<strong>Meaning:</strong> The building’s horizontal dimension perpendicular to the wind direction, per ES EN 1991-1-4:2015 Section 7.2.1. "
            "<strong>Impact:</strong> Determines scaling factor (e = min(b, 2h)), which sets zone extents (A, B, C). Larger b increases zone sizes."
        )
    )
    width = forms.FloatField(
        label='Width (d, m)',
        min_value=0,
        initial=19.26,
        help_text=(
            "<strong>Meaning:</strong> The building’s horizontal dimension parallel to the wind direction, per ES EN 1991-1-4:2015 Section 7.2.1. "
            "<strong>Impact:</strong> Influences zone definitions via scaling factor (e = min(b, 2h)). Larger d may increase zone A’s extent."
        )
    )
    site_altitude = forms.FloatField(
        label='Site Altitude (h_o, m)',
        min_value=0,
        initial=0,
        help_text=(
            "<strong>Meaning:</strong> The altitude above sea level, per ES EN 1991-1-4:2015 Section 4.2. "
            "<strong>Impact:</strong> Reduces air density (ρ), lowering velocity pressures (q_b, q_p) and wind loads."
        )
    )
    terrain_category = forms.ChoiceField(
        label='Terrain Category',
        choices=[(1, '1 (Sea, flat country)'), (2, '2 (Farmland, hedges)'),
                 (3, '3 (Suburban, forests)'), (4, '4 (Urban, skyscrapers)')],
        initial=3,
        help_text=(
            "<strong>Meaning:</strong> The terrain category describes the surrounding environment’s roughness, per ES EN 1991-1-4:2015 Table 4.1. "
            "<strong>Impact:</strong> Sets roughness length (z_0) and minimum height (z_min), affecting terrain factor (k_r) and roughness factor (c_r). Rougher terrains reduce wind loads."
        )
    )
    upwind_slope = forms.FloatField(
        label='Upwind Slope (φ)',
        min_value=0,
        initial=0,
        help_text=(
            "<strong>Meaning:</strong> The slope of the upwind terrain, per ES EN 1991-1-4:2015 Annex A. "
            "<strong>Impact:</strong> Influences orography factor (c_0). Steeper slopes increase c_0, amplifying wind loads."
        )
    )
    orographic_factor = forms.FloatField(
        label='Orographic Factor (s)',
        min_value=0,
        initial=0,
        help_text=(
            "<strong>Meaning:</strong> The orographic factor accounts for wind speed increases due to terrain features, per ES EN 1991-1-4:2015 Annex A. "
            "<strong>Impact:</strong> Multiplies mean wind velocity (v_m). Higher s increases v_m and peak pressure (q_p)."
        )
    )
    structural_factor = forms.FloatField(
        label='Structural Factor (C_sC_d)',
        min_value=0,
        initial=1,
        help_text=(
            "<strong>Meaning:</strong> The structural factor accounts for dynamic response and size effects, per ES EN 1991-1-4:2015 Section 6. "
            "<strong>Impact:</strong> Multiplies net pressure to calculate wind force (F_w). Typically 1.0 for small structures."
        )
    )
    windward_openings = forms.IntegerField(
        label='Windward Openings (n_1)',
        min_value=0,
        initial=24,
        help_text=(
            "<strong>Meaning:</strong> The number of openings on the windward face, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Influences internal pressure coefficient (c_pi). More openings increase c_pi, affecting net pressures."
        )
    )
    leeward_openings = forms.IntegerField(
        label='Leeward Openings (n_2)',
        min_value=0,
        initial=1,
        help_text=(
            "<strong>Meaning:</strong> The number of openings on the leeward face, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Affects internal pressure coefficient (c_pi). More openings influence c_pi and net pressures."
        )
    )
    parallel_openings = forms.IntegerField(
        label='Parallel Openings (n_3)',
        min_value=0,
        initial=5,
        help_text=(
            "<strong>Meaning:</strong> The number of openings on faces parallel to the wind, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Contributes to internal pressure coefficient (c_pi), affecting net pressures."
        )
    )
    windward_area = forms.FloatField(
        label='Windward Area (A_w, mm²)',
        min_value=0,
        initial=1.7514,
        help_text=(
            "<strong>Meaning:</strong> The total area of windward openings, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Influences internal pressure coefficient (c_pi). Larger areas increase c_pi."
        )
    )
    leeward_area = forms.FloatField(
        label='Leeward Area (A_l, mm²)',
        min_value=0,
        initial=37.43,
        help_text=(
            "<strong>Meaning:</strong> The total area of leeward openings, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Affects internal pressure coefficient (c_pi). Larger areas influence c_pi."
        )
    )
    parallel_area = forms.FloatField(
        label='Parallel Area (A_p, mm²)',
        min_value=0,
        initial=1.7514,
        help_text=(
            "<strong>Meaning:</strong> The total area of openings on parallel faces, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Contributes to internal pressure coefficient (c_pi), affecting net pressures."
        )
    )
    internal_pressure_coeff = forms.FloatField(
        label='Internal Pressure Coefficient (C_pi)',
        initial=0.35,
        help_text=(
            "<strong>Meaning:</strong> The internal pressure coefficient accounts for pressure inside the building, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Affects net pressure (W_net = W_e - W_i). Higher c_pi increases internal pressure (W_i)."
        )
    )
    basic_wind_velocity = forms.FloatField(
        label='Basic Wind Velocity (V_b,o, m/s)',
        min_value=0,
        initial=22,
        help_text=(
            "<strong>Meaning:</strong> The 10-minute mean wind speed at 10 m above ground in terrain category II, per ES EN 1991-1-4:2015 Section 4.2. "
            "<strong>Impact:</strong> Directly influences mean wind velocity (v_m) and velocity pressures (q_b, q_p). Higher values increase wind loads."
        )
    )