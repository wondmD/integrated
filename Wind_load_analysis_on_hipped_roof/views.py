from django.shortcuts import render
from .forms import WindLoadInputForm
import math

def wind_load_analysis_on_hipped_roof(request):
    """
    Handle wind load analysis for a hipped roof, processing form inputs and rendering results.
    For GET requests, display the input form. For POST requests, calculate wind loads and display results.
    """
    if request.method == 'POST':
        form = WindLoadInputForm(request.POST)
        if form.is_valid():
            # Extract input parameters
            vb0 = form.cleaned_data['vb0']
            c_direction = form.cleaned_data['c_direction']
            c_season = form.cleaned_data['c_season']
            rho = form.cleaned_data['rho']
            terrain_category = form.cleaned_data['terrain_category']
            h_e = form.cleaned_data['h_e']
            h_r = form.cleaned_data['h_r']

            # Step 1: Basic Wind Velocity (V_b)
            V_b = c_direction * c_season * vb0
            step1 = {
                'title': 'Step 1: Basic Wind Velocity',
                'formula': r'V_b = C_{\text{direction}} \times C_{\text{season}} \times V_{b,0}',
                'explanation': (
                    "Calculates the effective wind speed considering directional and seasonal effects."
                ),
                'calculation': f'{c_direction} \times {c_season} \times {vb0}',
                'result': f'{V_b:.2f} \, \text{'m/s'}',
                'constants': {
                    'V_{b,0}': 'Fundamental wind velocity (m/s), typically from meteorological data.',
                    'C_{\text{direction}}': 'Directional factor, often 1.0 unless specific data is available.',
                    'C_{\text{season}}': 'Seasonal factor, typically 1.0 for annual maximum winds.'
                },
                'detailed_explanation': (
                    "The basic wind velocity \( V_b \) is the reference wind speed used for wind load calculations, adjusted for wind direction and seasonal factors. "
                    "According to ES EN 1991-1-4:2015 section 4.2, it accounts for the likelihood of wind from different directions (\( C_{\text{direction}} \)) and seasonal wind patterns (\( C_{\text{season}} \)). "
                    "For the site in Adama, Ethiopia, meteorological data suggests \( V_{b,0} = 22 \, \text{m/s} \), with recommended values of \( C_{\text{direction}} = 1.0 \) and \( C_{\text{season}} = 1.0 \), resulting in \( V_b = 22 \, \text{m/s} \). "
                    "This step establishes the baseline wind speed for all subsequent calculations, directly influencing the magnitude of wind loads."
                )
            }

            # Step 2: Basic Velocity Pressure (q_b)
            q_b = 0.5 * rho * V_b**2 / 1000  # Convert Pa to kN/m²
            step2 = {
                'title': 'Step 2:   Basic Velocity Pressure',
                'formula': r'q_b = \frac{1}{2} \rho V_b^2',
                'explanation': (
                    "Converts wind speed to pressure using air density."
                ),
                'calculation': f'0.5 \times {rho} \times {V_b:.2f}^2 / 1000',
                'result': f'{q_b:.4f} \, \text{'kN/m'}^2',
                'constants': {
                    '\rho': 'Air density (kg/m³), standard value 1.25 kg/m³.'
                },
                'detailed_explanation': (
                    "The basic velocity pressure \( q_b \) converts the basic wind velocity into a dynamic pressure using the air density \( \rho \). "
                    "The formula derives from the kinetic energy of the wind, where the square of the velocity amplifies the effect of wind speed. "
                    "For \( V_b = 22 \, \text{m/s} \) and \( \rho = 1.25 \, \text{kg/m}^3 \), the calculation is \( q_b = \frac{1}{2} \times 1.25 \times 22^2 = 0.625 \times 484 = 302.5 \, \text{N/m}^2 = 0.3025 \, \text{kN/m}^2 \). "
                    "This pressure represents the force per unit area exerted by the wind, forming the basis for calculating wind loads."
                )
            }

            # Step 3: Reference Height (z)
            z = h_e + h_r
            step3 = {
                'title': 'Step 3: Reference Height',
                'formula': r'z = h_e + h_r',
                'explanation': (
                    "The height to the roof ridge, used for wind calculations."
                ),
                'calculation': f'{h_e} + {h_r}',
                'result': f'{z:.2f} \, \text{'m'}',
                'constants': {
                    'h_e': 'Height to eaves (m).',
                    'h_r': 'Height from eaves to ridge (m).'
                },
                'detailed_explanation': (
                    "The reference height \( z \) is the total height from the ground to the roof ridge, combining the height to the eaves (\( h_e \)) and the additional height to the ridge (\( h_r \)). "
                    "For the example building, \( h_e = 6.80 \, \text{m} \) and \( h_r = 2.95 \, \text{m} \), so \( z = 6.80 + 2.95 = 9.75 \, \text{m} \). "
                    "This height is used to evaluate wind effects at the structure’s highest point, where wind speeds are typically higher due to reduced ground friction."
                )
            }

            # Step 4: Roughness Length (z_0)
            terrain_z0 = {
                '0': {'value': 0.003, 'description': 'Sea or coastal area exposed to sea winds'},
                'I': {'value': 0.01, 'description': 'Lakes or flat terrain with negligible vegetation'},
                'II': {'value': 0.05, 'description': 'Open terrain with scattered obstacles'},
                'III': {'value': 0.3, 'description': 'Suburban or industrial areas with low-rise buildings'},
                'IV': {'value': 3.0, 'description': 'Urban areas with high-rise buildings or dense obstacles'}
            }
            z_0 = terrain_z0[terrain_category]['value']
            step4 = {
                'title': 'Step 4: Roughness Length',
                'formula': '',
                'explanation': (
                    "Determined by terrain type, affecting wind turbulence."
                ),
                'calculation': f'Selected for terrain category {terrain_category}',
                'result': f'{z_0:.3f} \, \text{'m'}',
                'constants': {
                    'z_0': 'Roughness length (m), varies by terrain type.'
                },
                'detailed_explanation': (
                    "The roughness length \( z_0 \) quantifies the terrain’s effect on wind flow, representing the height at which wind speed theoretically becomes zero due to surface friction. "
                    "For terrain category III (suburban, as in Adama), \( z_0 = 0.3 \, \text{m} \). This parameter influences turbulence and wind speed profiles, with rougher terrains causing greater wind variability."
                )
            }

            # Step 5: Turbulence Intensity (I_v(z))
            if z > z_0:
                ln_z_z0 = math.log(z / z_0)
                I_v = 1 / ln_z_z0
                step5 = {
                    'title': 'Step 5: Turbulence Intensity',
                    'formula': r'I_v(z) = \frac{1}{\ln(z / z_0)}',
                    'explanation': (
                        "Measures wind turbulence at the reference height."
                    ),
                    'calculation': f'1 / \ln({z:.2f} / {z_0:.3f}) = 1 / {ln_z_z0:.2f}',
                    'result': f'{I_v:.3f}',
                    'constants': {
                        'z': 'Reference height (m).',
                        'z_0': 'Roughness length (m).'
                    },
                    'detailed_explanation': (
                        "Turbulence intensity \( I_v(z) \) measures the variability in wind speed due to terrain roughness at height \( z \), reflecting the gustiness of the wind. "
                        "The document uses a simplified formula, differing from the standard ES EN 1991-1-4 formula \( I_v(z) = \frac{k_I}{\ln(z / z_0) + c_0} \), where \( k_I = 1.0 \) and \( c_0 = 1.0 \). "
                        "For \( z = 9.75 \, \text{m} \) and \( z_0 = 0.3 \, \text{m} \), \( \ln(9.75 / 0.3) \approx 3.48 \), so \( I_v(z) = 1 / 3.48 \approx 0.287 \). "
                        "This value is critical for calculating peak wind pressures, as it amplifies the dynamic effects of wind gusts."
                    )
                }
            else:
                I_v = 0
                step5 = {
                    'title': 'Step 5: Turbulence Intensity',
                    'formula': '',
                    'explanation': (
                        "Cannot calculate if \( z \leq z_0 \)."
                    ),
                    'calculation': '',
                    'result': 'N/A',
                    'constants': {},
                    'detailed_explanation': (
                        "Turbulence intensity cannot be calculated if the reference height \( z \) is less than or equal to the roughness length \( z_0 \), as the logarithm becomes undefined or negative. "
                        "In such cases, wind load calculations may require alternative methods or assumptions."
                    )
                }

            # Step 6: Roughness Factor (c_r(z))
            k_r = 0.2154
            if z > z_0:
                c_r = k_r * ln_z_z0
                step6 = {
                    'title': 'Step 6: Roughness Factor',
                    'formula': r'c_r(z) = k_r \times \ln\left(\frac{z}{z_0}\right)',
                    'explanation': (
                        "Adjusts wind speed based on terrain roughness."
                    ),
                    'calculation': f'{k_r} \times \ln({z:.2f} / {z_0:.3f}) = {k_r} \times {ln_z_z0:.2f}',
                    'result': f'{c_r:.3f}',
                    'constants': {
                        'k_r': 'Terrain roughness constant, 0.2154.'
                    },
                    'detailed_explanation': (
                        "The roughness factor \( c_r(z) \) adjusts the wind speed based on the terrain’s roughness and the height above ground, derived from boundary layer theory. "
                        "The constant \( k_r = 0.2154 \) is calculated as \( k_r = 0.19 \times (z_0 / z_{0,II})^{0.07} \), where \( z_{0,II} = 0.05 \, \text{m} \). "
                        "For \( z_0 = 0.3 \, \text{m} \), \( k_r = 0.19 \times (0.3 / 0.05)^{0.07} \approx 0.2154 \). "
                        "For \( z = 9.75 \, \text{m} \), \( \ln(9.75 / 0.3) \approx 3.48 \), so \( c_r(z) = 0.2154 \times 3.48 \approx 0.75 \)."
                    )
                }
            else:
                c_r = 0
                step6 = {
                    'title': 'Step 6: Roughness Factor',
                    'formula': '',
                    'explanation': (
                        "Cannot calculate if \( z \leq z_0 \)."
                    ),
                    'calculation': '',
                    'result': 'N/A',
                    'constants': {},
                    'detailed_explanation': (
                        "The roughness factor cannot be calculated if the reference height \( z \) is less than or equal to the roughness length \( z_0 \), as the logarithm becomes undefined or negative."
                    )
                }

            # Step 7: Mean Wind Velocity (V_m(z))
            c_0 = 1.0  # Orography factor for flat terrain
            V_m = c_r * c_0 * V_b
            step7 = {
                'title': 'Step 7: Mean Wind Velocity',
                'formula': r'V_m(z) = c_r(z) \times c_0(z) \times V_b',
                'explanation': (
                    "Wind speed at height \( z \), adjusted for terrain effects."
                ),
                'calculation': f'{c_r:.3f} \times {c_0} \times {V_b:.2f}',
                'result': f'{V_m:.2f} \, \text{'m/s'}',
                'constants': {
                    'c_0(z)': 'Orography factor, 1.0 for flat terrain.'
                },
                'detailed_explanation': (
                    "The mean wind velocity \( V_m(z) \) is the average wind speed at height \( z \), adjusted for terrain roughness (\( c_r(z) \)) and orography (\( c_0(z) \)). "
                    "For flat terrain, \( c_0(z) = 1.0 \). For \( c_r(z) = 0.75 \), \( V_b = 22 \, \text{m/s} \), the calculation is \( V_m(z) = 0.75 \times 1.0 \times 22 = 16.5 \, \text{m/s} \). "
                    "This velocity is used to calculate the peak velocity pressure."
                )
            }

            # Step 8: Peak Velocity Pressure (q_p(z))
            q_p = (1 + 7 * I_v) * 0.5 * rho * V_m**2 / 1000  # Convert Pa to kN/m²
            step8 = {
                'title': 'Step 8: Peak Velocity Pressure',
                'formula': r'q_p(z) = [1 + 7 \times I_v(z)] \times \frac{1}{2} \rho V_m^2(z)',
                'explanation': (
                    "The peak velocity pressure \( q_p(z) \) is the maximum dynamic pressure exerted by the wind, incorporating turbulence effects through the factor \( 1 + 7 \times I_v(z) \). "
                    "It combines the mean wind velocity’s pressure with gust effects, critical for determining the wind loads on the roof. "
                    "The factor of 7 is a standard multiplier in EN 1991-1-4 to account for peak gusts, ensuring conservative load estimates."
                ),
                'calculation': f'[1 + 7 \times {I_v:.3f}] \times 0.5 \times {rho} \times {V_m:.2f}^2 / 1000',
                'result': f'{q_p:.4f} \, \text{'kN/m'}^2',
                'constants': {
                    '7': 'Turbulence multiplier, standard per EN 1991-1-4.'
                },
                'detailed_explanation': (
                    "The peak velocity pressure \( q_p(z) \) is calculated using the formula: \( q_p(z) = [1 + 7 \times I_v(z)] \times \frac{1}{2} \rho V_m^2(z) \), where: \n"
                    "- \( I_v(z) = 0.287 \) (turbulence intensity), \n"
                    "- \( \rho = 1.25 \, \text{kg/m}^3 \) (air density), \n"
                    "- \( V_m = 16.5 \, \text{m/s} \) (mean wind velocity). \n"
                    "First, calculate the turbulence factor: \( 1 + 7 \times 0.287 = 1 + 2.009 = 3.009 \). \n"
                    "Then, calculate the dynamic pressure: \( \frac{1}{2} \times 1.25 \times 16.5^2 = 0.625 \times 272.25 = 170.15625 \, \text{N/m}^2 \). \n"
                    "Finally, \( q_p(z) = 3.009 \times 170.15625 = 512.3 \, \text{N/m}^2 = 0.5123 \, \text{kN/m}^2 \). \n"
                    "This value represents the maximum pressure the wind can exert, accounting for gusts, and is used to calculate wind loads on the roof."
                )
            }

            # Step 9: External Pressure Coefficients (C_pe)
            zones = [
                {'name': 'F', 'width': 1.95, 'height': 4.875, 'area': 9.50, 'C_pe_suction': -0.5223, 'C_pe_pressure': 0.5},
                {'name': 'G', 'width': 1.95, 'height': 0.25, 'area': 0.4875, 'C_pe_suction': -1.5, 'C_pe_pressure': 0.7},
                {'name': 'H', 'width': 3.05, 'height': 31.2, 'area': 128.4, 'C_pe_suction': -0.2, 'C_pe_pressure': None},
                {'name': 'I', 'width': 3.05, 'height': 31.2, 'area': 128.4, 'C_pe_suction': -0.4, 'C_pe_pressure': None},
                {'name': 'J', 'width': 1.95, 'height': 4.22, 'area': 8.19, 'C_pe_suction': -0.743, 'C_pe_pressure': None},
                {'name': 'K', 'width': 1.95, 'height': 31.2, 'area': 60.84, 'C_pe_suction': -0.5, 'C_pe_pressure': None},
                {'name': 'L', 'width': 1.95, 'height': 4.22, 'area': 8.19, 'C_pe_suction': -1.452, 'C_pe_pressure': None},
                {'name': 'M', 'width': 8.05, 'height': 1.59, 'area': 7.66, 'C_pe_suction': -0.846, 'C_pe_pressure': None},
            ]
            step9 = {
                'title': 'Step 9: External Pressure Coefficients',
                'formula': '',
                'explanation': (
                    "External pressure coefficients \( C_{pe} \) define the pressure distribution on the roof’s surface, varying by zone, wind direction (\( \theta = 0^\circ \)), and loaded area. "
                    "Zones F and G experience both positive pressure (wind pushing on the surface) and suction (wind pulling away), while zones H to M experience only suction. "
                    "These coefficients are derived from ES EN 1991-1-4:2015 section 7.2.5 and the example in 'Wind load on Hipped roof.pdf'."
                ),
                'calculation': 'Values predefined per zone based on the standard and document.',
                'result': '',
                'constants': {},
                'detailed_explanation': (
                    "The external pressure coefficients \( C_{pe} \) are determined for each roof zone based on the building’s geometry, wind direction, and loaded area. "
                    "For the hipped roof with a pitch angle \( \alpha_0 \approx 30^\circ \), the coefficients are provided in Table 7.5 of ES EN 1991-1-4:2015. "
                    "The zones are defined as follows: \n"
                    "- Zone F: Edge zone on the windward side. \n"
                    "- Zone G: Central zone on the windward side. \n"
                    "- Zone H: Windward slope. \n"
                    "- Zone I: Leeward slope. \n"
                    "- Zone J: Edge zone on the leeward side. \n"
                    "- Zone K: Central zone on the leeward side. \n"
                    "- Zone L: Ridge zone. \n"
                    "- Zone M: Eaves zone. \n"
                    "For each zone, the coefficients for suction (\( C_{pe}(-ve) \)) and pressure (\( C_{pe}(+ve) \)) are listed in the table above, where applicable."
                )
            }

            # Step 10: Net Wind Pressure (W_net)
            C_s_C_d = 1.0  # Structural factor for buildings < 15m
            C_pi_pressure = 0.2  # Internal pressure coefficient for pressure case
            C_pi_suction = -0.3  # Internal pressure coefficient for suction case
            W_net_results = []
            for zone in zones:
                # Suction case: C_pe_suction (negative) with C_pi_pressure (positive)
                W_net_suction = C_s_C_d * q_p * (zone['C_pe_suction'] + C_pi_pressure)
                W_net_results.append({
                    'zone': zone['name'],
                    'type': 'suction',
                    'C_pe': zone['C_pe_suction'],
                    'C_pi': C_pi_pressure,
                    'W_net': W_net_suction
                })
                # Pressure case if C_pe_pressure exists: C_pe_pressure (positive) with C_pi_suction (negative)
                if zone['C_pe_pressure'] is not None:
                    W_net_pressure = C_s_C_d * q_p * (zone['C_pe_pressure'] + C_pi_suction)
                    W_net_results.append({
                        'zone': zone['name'],
                        'type': 'pressure',
                        'C_pe': zone['C_pe_pressure'],
                        'C_pi': C_pi_suction,
                        'W_net': W_net_pressure
                    })

            step10 = {
                'title': 'Step 10: Net Wind Pressure',
                'formula': r'W_{net} = C_s C_d \times q_p(z) \times [C_{pe} + C_{pi}]',
                'explanation': (
                    "The net wind pressure \( W_{net} \) combines external and internal pressures, adjusted by the peak velocity pressure and structural factor."
                ),
                'calculation': 'Calculated for each zone with respective \( C_{pe} \) and \( C_{pi} \).',
                'result': '',
                'constants': {
                    'C_s C_d': 'Structural factor, 1.0 for buildings < 15m.',
                    'C_{pi}': '+0.2 for suction case, -0.3 for pressure case.'
                },
                'detailed_explanation': (
                    "The net wind pressure \( W_{net} \) is calculated using the formula: \( W_{net} = C_s C_d \times q_p(z) \times [C_{pe} + C_{pi}] \), where: \n"
                    "- \( C_s C_d = 1.0 \) (structural factor for buildings with height < 15m), \n"
                    "- \( q_p(z) = 0.5123 \, \text{kN/m}^2 \) (peak velocity pressure), \n"
                    "- \( C_{pe} \) is the external pressure coefficient, \n"
                    "- \( C_{pi} \) is the internal pressure coefficient. \n"
                    "For buildings without dominant openings, \( C_{pi} = +0.2 \) (internal pressure) for suction cases and \( C_{pi} = -0.3 \) (internal suction) for pressure cases. \n"
                    "For each zone, the net pressure is calculated for both suction and pressure scenarios (where applicable), providing the design wind loads for structural analysis. \n"
                    "For example, for zone G: \n"
                    "- Suction case: \( W_{net} = 1.0 \times 0.5123 \times [-1.5 + 0.2] = 0.5123 \times (-1.3) = -0.666 \, \text{kN/m}^2 \), \n"
                    "- Pressure case: \( W_{net} = 1.0 \times 0.5123 \times [0.7 + (-0.3)] = 0.5123 \times 0.4 = 0.205 \, \text{kN/m}^2 \). \n"
                    "The maximum positive and negative net pressures are used for design purposes."
                )
            }

            # Calculate maximum positive and minimum negative net pressures
            max_positive_W_net = max([w['W_net'] for w in W_net_results if w['W_net'] > 0], default=0)
            min_negative_W_net = min([w['W_net'] for w in W_net_results if w['W_net'] < 0], default=0)

            # Prepare context for template
            context = {
                'form': form,
                'steps': [step1, step2, step3, step4, step5, step6, step7, step8, step9, step10],
                'zones': zones,
                'W_net_results': W_net_results,
                'max_positive_W_net': max_positive_W_net,
                'min_negative_W_net': min_negative_W_net,
            }

            return render(request, 'wind_load_result.html', context)
        else:
            # Handle invalid form by re-rendering with errors
            return render(request, 'wind_load_form.html', {'form': form})
    else:
        # Handle GET request by showing an empty form
        form = WindLoadInputForm()
        return render(request, 'wind_load_form.html', {'form': form})