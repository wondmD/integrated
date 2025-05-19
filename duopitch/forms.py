from django import forms

class DuopitchRoofForm(forms.Form):
    building_length = forms.FloatField(
        label='Building Length (L, m)',
        min_value=0,
        initial=30.0,
        help_text=(
            "<strong>Meaning:</strong> The horizontal dimension parallel to the roof’s ridge, per ES EN 1991-1-4:2015 Section 7.2.5. "
            "<strong>Impact:</strong> Affects structural response but does not directly influence zone definitions, which depend on width (b) and height (h)."
        )
    )
    building_width = forms.FloatField(
        label='Building Width (b, m)',
        min_value=0,
        initial=12.0,
        help_text=(
            "<strong>Meaning:</strong> The horizontal dimension perpendicular to the roof’s ridge, per ES EN 1991-1-4:2015 Section 7.2.5. "
            "<strong>Impact:</strong> Determines characteristic length (e = min(b, 2h)), setting pressure zone extents (F, G, H, I, J). Larger b increases zone sizes."
        )
    )
    ridge_height = forms.FloatField(
        label='Ridge Height (h, m)',
        min_value=0,
        initial=6.1,
        help_text=(
            "<strong>Meaning:</strong> The height from ground to the roof’s ridge, per ES EN 1991-1-4:2015 Section 7.2.5. It is the reference height (z_e). "
            "<strong>Impact:</strong> Affects z_e and characteristic length (e = min(b, 2h)). Higher h increases wind velocity (v_m) and peak pressure (q_p)."
        )
    )
    pitch_angle = forms.FloatField(
        label='Pitch Angle (α, degrees)',
        min_value=-75,
        max_value=75,
        initial=15.0,
        help_text=(
            "<strong>Meaning:</strong> The angle of the roof slope, per ES EN 1991-1-4:2015 Section 7.2.5. It defines the duopitch roof’s geometry. "
            "<strong>Impact:</strong> Determines external pressure coefficients (c_pe) via Table 7.4a/b. Steeper angles affect suction or downward pressures."
        )
    )
    site_altitude = forms.FloatField(
        label='Site Altitude (h_o, m)',
        min_value=0,
        initial=1650.0,
        help_text=(
            "<strong>Meaning:</strong> The altitude above sea level, per ES EN 1991-1-4:2015 Section 4.2. "
            "<strong>Impact:</strong> Reduces air density (ρ), lowering velocity pressures (q_b, q_p) and wind loads."
        )
    )
    terrain_category = forms.ChoiceField(
        label='Terrain Category',
        choices=[(1, 'I (Sea, flat country)'), (2, 'II (Farmland, hedges)'),
                 (3, 'III (Suburban, forests)'), (4, 'IV (Urban, skyscrapers)')],
        initial=3,
        help_text=(
            "<strong>Meaning:</strong> The terrain category describes the surrounding environment’s roughness, per ES EN 1991-1-4:2015 Table 4.1. "
            "<strong>Impact:</strong> Sets roughness length (z_0) and minimum height (z_min), affecting terrain factor (k_r) and roughness factor (c_r). Rougher terrains reduce wind loads."
        )
    )
    upwind_slope = forms.FloatField(
        label='Upwind Slope (H/L_u)',
        min_value=0,
        initial=0.06,
        help_text=(
            "<strong>Meaning:</strong> The slope of the upwind terrain (H/L_u), per ES EN 1991-1-4:2015 Annex A. "
            "<strong>Impact:</strong> Influences orography factor (c_0). Steeper slopes increase c_0, amplifying wind velocity (v_m) and loads."
        )
    )
    horizontal_distance = forms.FloatField(
        label='Horizontal Distance from Crest (x, m)',
        initial=-200.0,
        help_text=(
            "<strong>Meaning:</strong> The distance from the hill crest to the site, per ES EN 1991-1-4:2015 Annex A. "
            "<strong>Impact:</strong> Affects orographic factor (s). Locations closer to the crest may increase wind loads."
        )
    )
    effective_height = forms.FloatField(
        label='Effective Height of Hill (H, m)',
        min_value=0,
        initial=30.0,
        help_text=(
            "<strong>Meaning:</strong> The effective height of the upwind hill, per ES EN 1991-1-4:2015 Annex A. "
            "<strong>Impact:</strong> Influences orographic factor (s). Taller hills increase c_0, raising wind loads."
        )
    )
    upwind_slope_length = forms.FloatField(
        label='Upwind Slope Length (L_u, m)',
        min_value=0,
        initial=500.0,
        help_text=(
            "<strong>Meaning:</strong> The length of the upwind slope, per ES EN 1991-1-4:2015 Annex A. "
            "<strong>Impact:</strong> Affects upwind slope (H/L_u) and orographic factor (s), influencing wind loads."
        )
    )
    windward_openings_area = forms.FloatField(
        label='Windward Openings Area (mm²)',
        min_value=0,
        initial=41.25,
        help_text=(
            "<strong>Meaning:</strong> The total area of openings on the windward face, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Influences internal pressure coefficient (c_pi). Larger areas increase c_pi, affecting net pressures."
        )
    )
    leeward_openings_area = forms.FloatField(
        label='Leeward Openings Area (mm²)',
        min_value=0,
        initial=41.25,
        help_text=(
            "<strong>Meaning:</strong> The total area of openings on the leeward face, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Affects internal pressure coefficient (c_pi). Larger areas influence c_pi and net pressures."
        )
    )
    parallel_openings_area = forms.FloatField(
        label='Parallel Openings Area (mm²)',
        min_value=0,
        initial=37.0,
        help_text=(
            "<strong>Meaning:</strong> The total area of openings on faces parallel to the wind, per ES EN 1991-1-4:2015 Section 7.2.9. "
            "<strong>Impact:</strong> Contributes to internal pressure coefficient (c_pi), affecting net pressures."
        )
    )
    purlin_spacing = forms.FloatField(
        label='Purlin Spacing (m)',
        min_value=0,
        initial=1.5525,
        help_text=(
            "<strong>Meaning:</strong> The distance between purlins supporting the roof, per ES EN 1991-1-4:2015. "
            "<strong>Impact:</strong> Multiplies net pressure (w_e) to calculate load per unit length on purlins (F_w,purlin). Larger spacing increases loads."
        )
    )
    truss_spacing = forms.FloatField(
        label='Truss Spacing (m)',
        min_value=0,
        initial=3.0,
        help_text=(
            "<strong>Meaning:</strong> The distance between trusses supporting the roof, per ES EN 1991-1-4:2015. "
            "<strong>Impact:</strong> Multiplies purlin load (F_w,purlin) to calculate point load on trusses (F_w,truss). Larger spacing increases loads."
        )
    )
    basic_wind_velocity = forms.FloatField(
        label='Basic Wind Velocity (V_b,o, m/s)',
        min_value=0,
        initial=22.0,
        help_text=(
            "<strong>Meaning:</strong> The 10-minute mean wind speed at 10 m above ground in terrain category II, per ES EN 1991-1-4:2015 Section 4.2. "
            "<strong>Impact:</strong> Directly influences mean wind velocity (v_m) and velocity pressures (q_b, q_p). Higher values increase wind loads."
        )
    )
    structural_factor = forms.FloatField(
        label='Structural Factor (C_sC_d)',
        min_value=0,
        initial=1.0,
        help_text=(
            "<strong>Meaning:</strong> The structural factor accounts for dynamic response and size effects, per ES EN 1991-1-4:2015 Section 6. "
            "<strong>Impact:</strong> Multiplies net pressure to calculate wind force (F_w). Typically 1.0 for small structures."
        )
    )