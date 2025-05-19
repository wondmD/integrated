from django import forms

class MonopitchRoofForm(forms.Form):
    TERRAIN_CHOICES = [
        ('1', 'I - Open terrain with scattered obstructions'),
        ('2', 'II - Farmland with scattered buildings or trees'),
        ('3', 'III - Urban or industrial areas'),
        ('4', 'IV - Dense urban or forest areas')
    ]

    basic_wind_velocity = forms.FloatField(
        label="Basic Wind Velocity (m/s)",
        min_value=0,
        initial=21.0,
        help_text=(
            "<strong>Meaning:</strong> The basic wind velocity (v_b,0) is the 10-minute mean wind speed at 10 m above ground in terrain category II, per EN 1991-1-4 Section 4.2. It is adjusted by directional (c_dir) and seasonal (c_season) factors to obtain v_b. "
            "<br>"
            "<strong>Impact:</strong> Directly influences basic wind velocity (v_b), which affects mean wind velocity (v_m) and velocity pressures (q_b, q_p). Higher values increase wind pressures and loads on the roof."
        )
    )
    building_length = forms.FloatField(
        label="Building Length (m)",
        min_value=0,
        initial=30.0,
        help_text=(
            "<strong>Meaning:</strong> The horizontal dimension of the building parallel to the roof’s ridge, per EN 1991-1-4 Section 7.2. "
            "<br>"
            "<strong>Impact:</strong> Affects structural response indirectly but does not directly influence zone definitions or pressure coefficients, which depend on width (b) and height (h)."
        )
    )
    building_width = forms.FloatField(
        label="Building Width (b, m)",
        min_value=0,
        initial=12.0,
        help_text=(
            "<strong>Meaning:</strong> The building’s horizontal dimension perpendicular to the roof’s ridge, as per EN 1991-1-4 Section 7.2.4. It defines the roof’s width. "
            "<br>"
            "<strong>Impact:</strong> Determines characteristic length (e = min(b, 2h)), which sets pressure zone extents (F, G, H). Larger b increases zone sizes and influences external pressure coefficients (c_pe)."
        )
    )
    ridge_height = forms.FloatField(
        label="Ridge Height (h, m)",
        min_value=0,
        initial=6.1,
        help_text=(
            "<strong>Meaning:</strong> The height from ground to the roof’s ridge, per EN 1991-1-4 Section 7.2.2. It is the reference height (z_e) for wind calculations. "
            "<br>"
            "<strong>Impact:</strong> Affects z_e, characteristic length (e = min(b, 2h)), and height-to-width ratio (h/d). Higher h increases wind velocity (v_m) and peak pressure (q_p), amplifying wind loads."
        )
    )
    pitch_angle = forms.FloatField(
        label="Pitch Angle (α, °)",
        min_value=-5,
        max_value=75,
        initial=15.0,
        help_text=(
            "<strong>Meaning:</strong> The angle of the roof slope relative to the horizontal, per EN 1991-1-4 Section 7.2.4. It defines the monopitch roof’s geometry. "
            "<br>"
            "<strong>Impact:</strong> Determines external pressure coefficients (c_pe) via interpolation in Table 7.1. Steeper angles may increase positive c_pe (downward pressure) or reduce negative c_pe (uplift), altering net pressures."
        )
    )
    site_altitude = forms.FloatField(
        label="Site Altitude (m)",
        min_value=0,
        initial=0.0,
        help_text=(
            "<strong>Meaning:</strong> The elevation of the site above sea level, per EN 1991-1-4 Section 4.5. It affects air density. "
            "<br>"
            "<strong>Impact:</strong> Reduces air density (ρ = 1.25 · (1 - 0.0001 · altitude)), lowering velocity pressures (q_b, q_p). Higher altitudes decrease wind loads slightly."
        )
    )
    terrain_category = forms.ChoiceField(
        choices=TERRAIN_CHOICES,
        label="Terrain Category",
        initial='2',
        help_text=(
            "<strong>Meaning:</strong> The terrain category describes the surrounding environment’s roughness, per EN 1991-1-4 Table 4.1. Categories I to IV range from open to dense terrains. "
            "<br>"
            "<strong>Impact:</strong> Sets roughness length (z_0) and minimum height (z_min), affecting terrain factor (k_r) and roughness factor (c_r). Rougher terrains reduce wind velocity and peak pressure, lowering loads."
        )
    )
    upwind_slope = forms.FloatField(
        label="Upwind Slope (φ)",
        min_value=0,
        initial=0.1,
        help_text=(
            "<strong>Meaning:</strong> The slope of the terrain upwind of the building, per EN 1991-1-4 Section 4.3.3. It influences orography effects. "
            "<br>"
            "<strong>Impact:</strong> Affects orography factor (c_0). Steeper slopes (0.05 ≤ φ < 0.3) increase c_0, raising wind velocity (v_m) and peak pressure (q_p), thus increasing wind loads."
        )
    )
    horizontal_distance = forms.FloatField(
        label="Horizontal Distance from Crest (m)",
        initial=0.0,
        help_text=(
            "<strong>Meaning:</strong> The horizontal distance from the building to the crest of upwind terrain, per EN 1991-1-4 Section 4.3.3. "
            "<br>"
            "<strong>Impact:</strong> Used in orography calculations if applicable. Typically zero for flat terrain, having no impact unless terrain features are significant."
        )
    )
    effective_height = forms.FloatField(
        label="Effective Height of Crest (m)",
        initial=0.0,
        help_text=(
            "<strong>Meaning:</strong> The vertical height of the upwind terrain crest relative to the site, per EN 1991-1-4 Section 4.3.3. "
            "<br>"
            "<strong>Impact:</strong> Influences orography factor (c_0) if terrain is significant. Typically zero for flat terrain, with no impact on calculations."
        )
    )
    upwind_slope_length = forms.FloatField(
        label="Upwind Slope Length (m)",
        initial=0.0,
        help_text=(
            "<strong>Meaning:</strong> The length of the upwind terrain slope, per EN 1991-1-4 Section 4.3.3. "
            "<br>"
            "<strong>Impact:</strong> Affects orography calculations if terrain features are present. Zero for flat terrain, with no impact on wind loads."
        )
    )
    windward_openings_area = forms.FloatField(
        label="Windward Openings Area (mm²)",
        min_value=0,
        initial=0.0,
        help_text=(
            "<strong>Meaning:</strong> The total area of openings on the windward face, per EN 1991-1-4 Section 7.2.9. "
            "<br>"
            "<strong>Impact:</strong> Influences internal pressure coefficient (c_pi) via opening ratio (μ). Larger areas may increase c_pi, affecting net pressure (w_net), especially for internal suction."
        )
    )
    leeward_openings_area = forms.FloatField(
        label="Leeward Openings Area (mm²)",
        min_value=0,
        initial=0.0,
        help_text=(
            "<strong>Meaning:</strong> The total area of openings on the leeward face, per EN 1991-1-4 Section 7.2.9. "
            "<br>"
            "<strong>Impact:</strong> Contributes to opening ratio (μ) for internal pressure coefficient (c_pi). Larger areas may alter c_pi, impacting net pressure calculations."
        )
    )
    parallel_openings_area = forms.FloatField(
        label="Parallel Openings Area (mm²)",
        min_value=0,
        initial=0.0,
        help_text=(
            "<strong>Meaning:</strong> The total area of openings on faces parallel to the wind, per EN 1991-1-4 Section 7.2.9. "
            "<br>"
            "<strong>Impact:</strong> Affects opening ratio (μ) for internal pressure coefficient (c_pi). Larger areas may modify c_pi, influencing net pressure (w_net)."
        )
    )
    structural_factor = forms.FloatField(
        label="Structural Factor (c_s c_d)",
        min_value=0,
        initial=1.0,
        help_text=(
            "<strong>Meaning:</strong> The structural factor accounts for the building’s dynamic response to wind, per EN 1991-1-4 Section 6. Default is 1.0 for simple structures. "
            "<br>"
            "<strong>Impact:</strong> Multiplies net pressure (w_e) in load calculations. Higher values increase design loads on purlins and trusses."
        )
    )
    purlin_spacing = forms.FloatField(
        label="Purlin Spacing (m)",
        min_value=0,
        initial=1.2,
        help_text=(
            "<strong>Meaning:</strong> The distance between purlins supporting the roof, per EN 1991-1-4. "
            "<br>"
            "<strong>Impact:</strong> Multiplies net pressure (w_e) to calculate load per unit length on purlins (F_w,purlin). Larger spacing increases purlin loads, affecting structural design."
        )
    )
    truss_spacing = forms.FloatField(
        label="Truss Spacing (m)",
        min_value=0,
        initial=6.0,
        help_text=(
            "<strong>Meaning:</strong> The distance between trusses supporting the roof, per EN 1991-1-4. "
            "<br>"
            "<strong>Impact:</strong> Multiplies purlin load (F_w,purlin) to calculate point load on trusses (F_w,truss). Larger spacing increases truss loads, critical for structural design."
        )
    )