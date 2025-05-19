from django import forms

class FlatRoofForm(forms.Form):
    TERRAIN_CHOICES = [
        ('0', '0 - Sea or coastal area'),
        ('I', 'I - Open terrain with scattered obstructions'),
        ('II', 'II - Farmland with scattered buildings or trees'),
        ('III', 'III - Urban or industrial areas'),
        ('IV', 'IV - Dense urban or forest areas')
    ]
    
    terrain_category = forms.ChoiceField(
        choices=TERRAIN_CHOICES,
        label="Terrain Category",
        initial='II',
        help_text=(
            "<strong>Meaning:</strong> The terrain category describes the surrounding environment’s roughness, as defined in EN 1991-1-4 Table 4.1. Categories range from 0 (sea) to IV (dense urban/forest), affecting wind flow. "
            "<br>"
            "<strong>Impact:</strong> Determines roughness length (z_0) and minimum height (z_min), influencing terrain factor (k_r) and roughness factor (c_r). Rougher terrains (higher categories) reduce wind velocity and peak pressure (q_p), lowering wind loads."
        )
    )
    basic_wind_velocity = forms.FloatField(
        label="Basic Wind Velocity (m/s)",
        min_value=0,
        initial=27.0,
        help_text=(
            "<strong>Meaning:</strong> The basic wind velocity (v_b) is the 10-minute mean wind speed at 10 m above ground in terrain category II, per EN 1991-1-4 Section 4.2. It includes directional (c_dir) and seasonal (c_season) factors. "
            "<br>"
            "<strong>Impact:</strong> Directly affects mean wind velocity (v_m) and basic velocity pressure (q_b). Higher v_b increases q_b and peak pressure (q_p), resulting in greater wind loads on the roof."
        )
    )
    wind_direction_dimension = forms.FloatField(
        label="Horizontal Dimension Parallel to Wind (d, m)",
        min_value=0,
        initial=10.0,
        help_text=(
            "<strong>Meaning:</strong> The building’s horizontal dimension parallel to the wind direction, as per EN 1991-1-4 Section 7.2.3. It defines the roof’s plan length along the wind path. "
            "<br>"
            "<strong>Impact:</strong> Influences zone definitions indirectly via characteristic length (e = min(b, 2h)). Smaller d may alter zone extents, affecting pressure distribution, though b typically governs e for flat roofs."
        )
    )
    crosswind_dimension = forms.FloatField(
        label="Horizontal Dimension Perpendicular to Wind (b, m)",
        min_value=0,
        initial=20.0,
        help_text=(
            "<strong>Meaning:</strong> The building’s crosswind dimension (b), perpendicular to the wind direction, per EN 1991-1-4 Section 7.2.3. It defines the roof’s width. "
            "<br>"
            "<strong>Impact:</strong> Determines characteristic length (e = min(b, 2h)), which sets the extent of pressure zones (F, G, H, I). Larger b increases zone sizes, potentially altering pressure distribution and load magnitudes."
        )
    )
    building_height = forms.FloatField(
        label="Building Height (h, m)",
        min_value=0,
        initial=5.0,
        help_text=(
            "<strong>Meaning:</strong> The height from ground to roof level, as per EN 1991-1-4 Section 7.2.3. It represents the building’s vertical dimension. "
            "<br>"
            "<strong>Impact:</strong> Affects reference height (z_e = h + h_p) and characteristic length (e = min(b, 2h)). Higher h increases z_e, raising wind velocity (v_m) and peak pressure (q_p), thus increasing wind loads."
        )
    )
    parapet_height = forms.FloatField(
        label="Parapet Height (h_p, m)",
        min_value=0,
        initial=0.0,
        help_text=(
            "<strong>Meaning:</strong> The additional height of parapets above the roof level, per EN 1991-1-4 Section 7.2.3. Parapets influence wind flow over the roof. "
            "<br>"
            "<strong>Impact:</strong> Increases reference height (z_e = h + h_p) and parapet height ratio (h_p/h), affecting external pressure coefficients (c_pe). Higher h_p increases c_pe magnitudes, leading to greater suction (uplift) pressures."
        )
    )
    loaded_area = forms.ChoiceField(
        choices=[('1', '≤ 1 m² (c_pe,1)'), ('10', '≥ 10 m² (c_pe,10)')],
        label="Loaded Area",
        initial='10',
        help_text=(
            "<strong>Meaning:</strong> The size of the loaded area for which wind pressure is calculated, per EN 1991-1-4 Section 7.2.1. Options are ≤ 1 m² (local, c_pe,1) or ≥ 10 m² (global, c_pe,10). "
            "<br>"
            "<strong>Impact:</strong> Determines external pressure coefficients (c_pe). c_pe,1 is higher for small areas (e.g., fixings), increasing local loads. c_pe,10 is lower, used for overall structural design, reducing global loads."
        )
    )
    orography_factor = forms.FloatField(
        label="Orography Factor (c_0)",
        min_value=1.0,
        initial=1.0,
        help_text=(
            "<strong>Meaning:</strong> The orography factor accounts for wind speed increases due to terrain features like hills, per EN 1991-1-4 Section 4.3.3. Default is 1.0 for flat terrain. "
            "<br>"
            "<strong>Impact:</strong> Multiplies mean wind velocity (v_m = c_r · c_0 · v_b). Higher c_0 increases v_m and peak pressure (q_p), amplifying wind loads across all zones."
        )
    )
    dominant_face = forms.BooleanField(
        label="Building with Dominant Face",
        required=False,
        initial=False,
        help_text=(
            "<strong>Meaning:</strong> Indicates if the building has a dominant face with openings at least twice the area of other faces, per EN 1991-1-4 Section 7.2.9. "
            "<br>"
            "<strong>Impact:</strong> If checked, internal pressure coefficients (c_pi) may be calculated based on opening ratios, potentially increasing c_pi values. If unchecked, default c_pi,min (-0.3) and c_pi,max (+0.2) are used, simplifying the calculation."
        )
    )
    c_pi_min = forms.FloatField(
        label="Minimum Internal Pressure Coefficient (c_pi,min)",
        initial=-0.3,
        help_text=(
            "<strong>Meaning:</strong> The minimum internal pressure coefficient (c_pi,min) represents the most negative internal pressure due to openings, per EN 1991-1-4 Section 7.2.9. Default is -0.3. "
            "<br>"
            "<strong>Impact:</strong> Used with positive external pressure coefficients (c_pe) to calculate net pressure (w_net). A more negative c_pi,min increases w_net for positive c_pe (e.g., Zone I), amplifying downward loads."
        )
    )
    c_pi_max = forms.FloatField(
        label="Maximum Internal Pressure Coefficient (c_pi,max)",
        initial=0.2,
        help_text=(
            "<strong>Meaning:</strong> The maximum internal pressure coefficient (c_pi,max) represents the most positive internal pressure due to openings, per EN 1991-1-4 Section 7.2.9. Default is +0.2. "
            "<br>"
            "<strong>Impact:</strong> Used with negative external pressure coefficients (c_pe) to calculate net pressure (w_net). A more positive c_pi,max increases w_net for negative c_pe (e.g., Zones F, G, H), amplifying uplift loads."
        )
    )
    air_density = forms.FloatField(
        label="Air Density (kg/m³)",
        min_value=0,
        initial=1.25,
        help_text=(
            "<strong>Meaning:</strong> The air density (ρ) is the mass per unit volume of air, typically 1.25 kg/m³ at sea level, per EN 1991-1-4 Section 4.5. "
            "<br>"
            "<strong>Impact:</strong> Affects basic (q_b) and peak (q_p) velocity pressures via q = (1/2) · ρ · v². Higher ρ increases q_b and q_p, resulting in greater wind pressures across all zones."
        )
    )