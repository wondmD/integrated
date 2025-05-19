from django.shortcuts import render
from .forms import MonopitchRoofForm
import math
from django.templatetags.static import static

def monopitch_calculate(request):
    if request.method == 'POST':
        form = MonopitchRoofForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            explanation = []

            # Step 1: Basic Wind Velocity (V_b)
            c_direction = 1.0
            c_season = 1.0
            v_b_0 = data['basic_wind_velocity']
            v_b = c_direction * c_season * v_b_0
            explanation.append({
                'title': 'Step 1: Basic Wind Velocity V_b',
                'description': 'The basic wind velocity (V_b) is the fundamental wind speed used for calculating wind loads on the monopitch roof, as defined in ES EN 1991-1-4:2015 Section 4.2. It accounts for directional and seasonal effects, though these are assumed constant (C_direction = 1.0, C_season = 1.0) for simplicity in this calculation. The reference wind velocity (V_b,0) is provided based on regional wind maps or user input.',
                'formula': '\\( V_b = C_{\\text{direction}} \\times C_{\\text{season}} \\times V_{b,0} \\)',
                'values': {
                    'c_direction': c_direction,
                    'c_season': c_season,
                    'v_b_0': v_b_0
                },
                'values_latex': '\\( C_{\\text{direction}} = %.1f, C_{\\text{season}} = %.1f, V_{b,0} = %.1f \\text{ m/s} \\)' % (c_direction, c_season, v_b_0),
                'result': v_b,
                'result_latex': '\\( V_b = %.2f \\text{ m/s} \\)' % v_b,
                'reference': 'ES EN 1991-1-4:2015, Section 4.2'
            })

            # Step 2: Basic Velocity Pressure (q_b)
            rho = 1.25 * (1 - 0.0001 * data['site_altitude'])
            q_b = 0.5 * rho * v_b ** 2 / 1000  # kN/m²
            explanation.append({
                'title': 'Step 2: Basic Velocity Pressure q_b',
                'description': 'The basic velocity pressure (q_b) represents the dynamic pressure exerted by the wind, calculated using air density (rho) and the square of the basic wind velocity (V_b), as per ES EN 1991-1-4:2015 Section 4.5. Air density is adjusted for site altitude, decreasing by 0.01% per meter above sea level. The result is converted to kN/m² for structural calculations.',
                'formula': '\\( q_b = \\frac{1}{2} \\rho V_b^2 \\times 10^{-3} \\)',
                'values': {
                    'rho': rho,
                    'v_b': v_b
                },
                'values_latex': '\\( \\rho = %.2f \\text{ kg/m}^3, V_b = %.2f \\text{ m/s} \\)' % (rho, v_b),
                'result': q_b,
                'result_latex': '\\( q_b = %.4f \\text{ kN/m}^2 \\)' % q_b,
                'reference': 'ES EN 1991-1-4:2015, Section 4.5'
            })

            # Step 3: Peak Velocity Pressure (q_p(z))
            z = data['ridge_height']  # Reference height
            terrain_params = {1: (0.01, 1), 2: (0.05, 2), 3: (0.3, 5), 4: (1.0, 10)}
            z_0, z_min = terrain_params[int(data['terrain_category'])]
            k_i = 1.0
            phi = data['upwind_slope']
            s = 0.3  # Simplified from document
            c_0 = 1 + 2 * s * phi if 0.05 <= phi < 0.3 else (1 + 0.6 * s if phi >= 0.3 else 1.0)
            l_v = k_i / (c_0 * math.log(z / z_0)) if z >= z_min else k_i / (c_0 * math.log(z_min / z_0))
            k_r = 0.19 * (z_0 / 0.05) ** 0.07
            c_r = k_r * math.log(z / z_0) if z >= z_min else k_r * math.log(z_min / z_0)
            v_m = c_r * c_0 * v_b
            q_p = (1 + 7 * l_v) * 0.5 * rho * v_m ** 2 / 1000
            explanation.append({
                'title': 'Step 3: Peak Velocity Pressure q_p(z)',
                'description': 'The peak velocity pressure (q_p(z)) accounts for wind effects at the reference height (z, typically the ridge height), incorporating terrain roughness, orography, and turbulence, as per ES EN 1991-1-4:2015 Sections 4.3, 4.4, and 4.5. Terrain category determines roughness length (z_0) and minimum height (z_min). The orography factor (c_0) adjusts for upwind slope, and turbulence intensity (I_v) amplifies the pressure. The mean wind velocity (V_m) is adjusted for terrain and height.',
                'formula': '\\( q_p(z) = \\left[1 + 7 I_v(z)\\right] \\times \\frac{1}{2} \\rho V_m^2(z) \\times 10^{-3} \\)',
                'values': {
                    'z': z,
                    'z_0': z_0,
                    'z_min': z_min,
                    'k_i': k_i,
                    'phi': phi,
                    's': s,
                    'c_0': c_0,
                    'l_v': l_v,
                    'k_r': k_r,
                    'c_r': c_r,
                    'v_m': v_m,
                    'rho': rho
                },
                'values_latex': '\\( z = %.1f \\text{ m}, z_0 = %.2f \\text{ m}, z_{\\text{min}} = %.1f \\text{ m}, k_i = %.1f, \\phi = %.2f, s = %.1f, c_0 = %.3f, I_v = %.2f, k_r = %.4f, c_r = %.4f, V_m = %.2f \\text{ m/s}, \\rho = %.2f \\text{ kg/m}^3 \\)' % (z, z_0, z_min, k_i, phi, s, c_0, l_v, k_r, c_r, v_m, rho),
                'result': q_p,
                'result_latex': '\\( q_p(z) = %.3f \\text{ kN/m}^2 \\)' % q_p,
                'reference': 'ES EN 1991-1-4:2015, Sections 4.3, 4.4, 4.5, 7.2.2',
                'substeps': [
                    {
                        'title': 'Reference Height',
                        'description': 'The reference height (z_e) is taken as the ridge height (h) of the monopitch roof, as specified in ES EN 1991-1-4:2015 Section 7.2.2, to evaluate wind effects at the highest point of the structure.',
                        'formula': '\\( z_e = h \\)',
                        'values': {'h': z},
                        'values_latex': '\\( h = %.1f \\text{ m} \\)' % z,
                        'result': z,
                        'result_latex': '\\( z_e = %.1f \\text{ m} \\)' % z,
                        'reference': 'Section 7.2.2'
                    },
                    {
                        'title': 'Orography Factor',
                        'description': 'The orography factor (c_0) accounts for increased wind speed due to upwind terrain slope (phi), as per ES EN 1991-1-4:2015 Section 4.3.3. A simplified factor (s = 0.3) is used for slopes between 0.05 and 0.3.',
                        'formula': '\\( c_0 = 1 + 2 s \\phi \\)',
                        'values': {'s': s, 'phi': phi},
                        'values_latex': '\\( s = %.1f, \\phi = %.2f \\)' % (s, phi),
                        'result': c_0,
                        'result_latex': '\\( c_0 = %.3f \\)' % c_0,
                        'reference': 'Section 4.3.3'
                    },
                    {
                        'title': 'Turbulence Intensity',
                        'description': 'Turbulence intensity (I_v) quantifies wind fluctuations at height z, calculated using the turbulence factor (k_i), orography factor (c_0), and terrain roughness (z_0), as per ES EN 1991-1-4:2015 Section 4.4.',
                        'formula': '\\( I_v(z) = \\frac{k_i}{c_0(z) \\ln(z / z_0)} \\)',
                        'values': {'k_i': k_i, 'c_0': c_0, 'z': z, 'z_0': z_0},
                        'values_latex': '\\( k_i = %.1f, c_0 = %.3f, z = %.1f \\text{ m}, z_0 = %.2f \\text{ m} \\)' % (k_i, c_0, z, z_0),
                        'result': l_v,
                        'result_latex': '\\( I_v = %.2f \\)' % l_v,
                        'reference': 'Section 4.4'
                    },
                    {
                        'title': 'Mean Wind Velocity',
                        'description': 'The mean wind velocity (V_m) at height z is adjusted for terrain roughness (c_r), orography (c_0), and basic wind velocity (V_b), as per ES EN 1991-1-4:2015 Section 4.3.',
                        'formula': '\\( V_m(z) = c_r(z) c_0(z) V_b \\)',
                        'values': {'c_r': c_r, 'c_0': c_0, 'v_b': v_b},
                        'values_latex': '\\( c_r = %.4f, c_0 = %.3f, V_b = %.2f \\text{ m/s} \\)' % (c_r, c_0, v_b),
                        'result': v_m,
                        'result_latex': '\\( V_m = %.2f \\text{ m/s} \\)' % v_m,
                        'reference': 'Section 4.3'
                    }
                ]
            })

            # Step 4: External Pressure Coefficients (C_pe) for Monopitch Roof
            pitch_angle = data['pitch_angle']
            b = data['building_width']
            h = data['ridge_height']
            e = min(b, 2 * h)
            zones = [
                {'zone': 'F', 'width': e / 10, 'length': e / 4, 'area': (e / 10) * (e / 4)},
                {'zone': 'G', 'width': e / 10, 'length': b - 2 * (e / 4), 'area': (e / 10) * (b - 2 * (e / 4))},
                {'zone': 'H', 'width': b - 2 * (e / 10), 'length': b, 'area': (b - 2 * (e / 10)) * b}
            ]

            cpe_table = {
                5: {'F': (-1.7, -2.5, 0.0), 'G': (-1.2, -2.0, 0.0), 'H': (-0.6, -2.0, 0.0)},
                15: {'F': (-0.9, -2.0, 0.2), 'G': (-0.8, -1.5, 0.0), 'H': (-0.3, -1.5, 0.0)},
                30: {'F': (-0.5, -1.5, 0.7), 'G': (-0.5, -1.5, 0.4), 'H': (-0.2, -1.5, 0.4)},
                45: {'F': (0.0, None, 0.7), 'G': (0.0, None, 0.7), 'H': (0.0, None, 0.6)},
                60: {'F': (0.7, None), 'G': (0.7, None), 'H': (0.7, None)},
                75: {'F': (0.8, None), 'G': (0.8, None), 'H': (0.8, None)}
            }

            def interpolate_cpe(angle, zone, positive=False):
                angles = sorted(cpe_table.keys())
                for i in range(len(angles) - 1):
                    if angles[i] <= angle < angles[i + 1]:
                        cpe_low = cpe_table[angles[i]][zone]
                        cpe_high = cpe_table[angles[i + 1]][zone]
                        if positive:
                            cpe_low = cpe_low[2] if len(cpe_low) > 2 else 0.0
                            cpe_high = cpe_high[2] if len(cpe_high) > 2 else 0.0
                        else:
                            cpe_low = cpe_low[1] if cpe_low[1] is not None else cpe_low[0]
                            cpe_high = cpe_high[1] if cpe_high[1] is not None else cpe_high[0]
                        fraction = (angle - angles[i]) / (angles[i + 1] - angles[i])
                        return cpe_low + fraction * (cpe_high - cpe_low)
                return cpe_table[angle][zone][0] if not positive else cpe_table[angle][zone][2] if len(cpe_table[angle][zone]) > 2 else 0.0

            for zone in zones:
                area = zone['area']
                zone_name = zone['zone']
                cpe_neg = interpolate_cpe(pitch_angle, zone_name)
                cpe_pos = interpolate_cpe(pitch_angle, zone_name, positive=True)
                zone.update({'C_pe_neg': cpe_neg, 'C_pe_pos': cpe_pos})

            explanation.append({
                'title': 'Step 4: External Pressure Coefficients C_pe',
                'description': 'External pressure coefficients (C_pe) define the wind pressure distribution across the monopitch roof’s zones (F, G, H), as per ES EN 1991-1-4:2015 Section 7.2.4. These coefficients vary with pitch angle and zone area, using tables for C_pe,1 (small areas, ≤1 m²) and C_pe,10 (large areas, ≥10 m²). Interpolation is applied for intermediate areas or angles. Zone dimensions are derived from the building width (b) and ridge height (h).',
                'formula': '\\( C_{pe} = \\begin{cases} C_{pe,1} & \\text{if } A \\leq 1 \\text{ m}^2 \\\\ C_{pe,10} & \\text{if } A \\geq 10 \\text{ m}^2 \\\\ \\text{Interpolate} & \\text{if } 1 \\text{ m}^2 < A < 10 \\text{ m}^2 \\end{cases} \\)',
                'values': {
                    'pitch_angle': pitch_angle,
                    'e': e
                },
                'values_latex': '\\( \\alpha = %.1f \\text{°}, e = %.2f \\text{ m} \\)' % (pitch_angle, e),
                'result': 'See zone table for C_pe values.',
                'result_latex': 'See zone table for C_pe values.',
                'reference': 'ES EN 1991-1-4:2015, Section 7.2.4',
                'figures': [static('images/monopitch_zones.jpg')]
            })

            # Step 5: Internal Pressure Coefficient (C_pi)
            h_d_ratio = data['ridge_height'] / data['building_width']
            total_area = data['windward_openings_area'] + data['leeward_openings_area'] + data['parallel_openings_area']
            mu = (data['leeward_openings_area'] + data['parallel_openings_area']) / total_area if total_area > 0 else 0
            c_pi = 0.17 + (0.1 - 0.17) * (h_d_ratio - 0.25) / (1.0 - 0.25) if 0.25 <= h_d_ratio <= 1.0 else 0.17
            explanation.append({
                'title': 'Step 5: Internal Pressure Coefficient C_pi',
                'description': 'The internal pressure coefficient (C_pi) accounts for wind pressure inside the building due to openings, as per ES EN 1991-1-4:2015 Section 7.2.9. It depends on the ratio of opening areas (mu) and the height-to-width ratio (h/d). The coefficient is interpolated between 0.17 (for h/d ≤ 0.25) and 0.1 (for h/d ≥ 1.0) to reflect internal pressure variations.',
                'formula': '\\( \\mu = \\frac{\\sum \\text{area of openings where } C_{pe} \\text{ is negative or } 0.0}{\\sum \\text{area of all openings}} \\)',
                'values': {
                    'mu': mu,
                    'h_d_ratio': h_d_ratio
                },
                'values_latex': '\\( \\mu = %.4f, \\text{h/d} = %.4f \\)' % (mu, h_d_ratio),
                'result': c_pi,
                'result_latex': '\\( C_{pi} = %.3f \\)' % c_pi,
                'reference': 'ES EN 1991-1-4:2015, Section 7.2.9'
            })

            # Step 6: Net Wind Pressure (w)
            c_s_c_d = data['structural_factor']
            results = []
            for zone in zones:
                w_e_pos = q_p * (zone['C_pe_pos'] + c_pi)
                w_e_neg = q_p * (zone['C_pe_neg'] + c_pi)
                results.append({
                    'zone': zone['zone'], 'area': zone['area'],
                    'C_pe_pos': zone['C_pe_pos'], 'C_pe_neg': zone['C_pe_neg'],
                    'w_e_pos': w_e_pos, 'w_e_neg': w_e_neg
                })
            explanation.append({
                'title': 'Step 6: Net Wind Pressure w',
                'description': 'The net wind pressure (w_e) on each roof zone combines external (C_pe) and internal (C_pi) pressure coefficients with the peak velocity pressure (q_p), as per ES EN 1991-1-4:2015 Section 5.2. The structural factor (C_s C_d) accounts for dynamic response, assumed as 1.0 unless specified. Positive and negative pressures are calculated for wind direction theta = 0°.',
                'formula': '\\( w_e = q_p(z) (C_{pe} + C_{pi}) \\)',
                'values': {
                    'c_s_c_d': c_s_c_d,
                    'q_p': q_p,
                    'c_pi': c_pi
                },
                'values_latex': '\\( C_s C_d = %.1f, q_p = %.3f \\text{ kN/m}^2, C_{pi} = %.3f \\)' % (c_s_c_d, q_p, c_pi),
                'result': 'See results table for w_e values.',
                'result_latex': 'See results table for w_e values.',
                'reference': 'ES EN 1991-1-4:2015, Section 5.2'
            })

            # Step 7: Load Transfer to Purlins and Trusses
            purlin_spacing = data['purlin_spacing']
            truss_spacing = data['truss_spacing']
            print(f"Debug: Purlin spacing = {purlin_spacing}, Truss spacing = {truss_spacing}")  # Debug
            purlin_loads = []
            truss_loads = []
            for zone in results:
                f_w_purlin = zone['w_e_neg'] * purlin_spacing
                f_w_truss = f_w_purlin * truss_spacing
                purlin_loads.append({
                    'zone': zone['zone'], 'area': zone['area'],
                    'w_e': zone['w_e_neg'], 'f_w_purlin': f_w_purlin
                })
                truss_loads.append({
                    'zone': zone['zone'], 'area': zone['area'],
                    'f_w_purlin': f_w_purlin, 'f_w_truss': f_w_truss
                })
            explanation.append({
                'title': 'Step 7: Load Transfer to Purlins and Trusses',
                'description': 'Wind pressures are transferred to structural elements (purlins and trusses) to determine design loads, as per ES EN 1991-1-4:2015. The net wind pressure (w_e, negative for uplift) is multiplied by purlin spacing to calculate the load per unit length on purlins (F_w,purlin). This load is then multiplied by truss spacing to find the point load on trusses (F_w,truss). These loads are critical for designing the roof’s structural members.',
                'formula': '\\( F_{w,\\text{purlin}} = w_e \\times \\text{purlin spacing}, \\quad F_{w,\\text{truss}} = F_{w,\\text{purlin}} \\times \\text{truss spacing} \\)',
                'values': {
                    'purlin_spacing': purlin_spacing,
                    'truss_spacing': truss_spacing
                },
                'values_latex': '\\( \\text{purlin spacing} = %.2f \\text{ m}, \\text{truss spacing} = %.2f \\text{ m} \\)' % (purlin_spacing, truss_spacing),
                'result': 'See load transfer tables.',
                'result_latex': 'See load transfer tables.',
                'reference': 'ES EN 1991-1-4:2015',
                'figures': [static('images/monopitch_purlin.jpg')]
            })

            return render(request, 'monopitch/results.html', {
                'form': form, 'calculation': data, 'results': results,
                'explanation': explanation, 'purlin_loads': purlin_loads, 'truss_loads': truss_loads
            })
    else:
        form = MonopitchRoofForm()
    return render(request, 'monopitch/monopitch_input.html', {'form': form})