from django.shortcuts import render
from .forms import WindPressureForm
import math

def calculate(request):
    if request.method == 'POST':
        form = WindPressureForm(request.POST)
        if form.is_valid():
            # Extract input data
            data = form.cleaned_data
            h = data['height']
            b = data['in_wind_depth']
            d = data['width']
            h_o = data['site_altitude']
            T = int(data['terrain_category'])
            phi = data['upwind_slope']
            s = data['orographic_factor']
            C_sC_d = data['structural_factor']
            n_1 = data['windward_openings']
            n_2 = data['leeward_openings']
            n_3 = data['parallel_openings']
            A_w = data['windward_area'] * 1e-6  # Convert mm² to m²
            A_l = data['leeward_area'] * 1e-6
            A_p = data['parallel_area'] * 1e-6
            C_pi = data['internal_pressure_coeff']
            V_b0 = data['basic_wind_velocity']

            # Initialize explanation list
            explanation = []

            # Step 1: Air density (ρ) based on altitude
            h_o_total = h_o + h
            explanation.append({
                'title': 'Step 1: Calculate Air Density (\\(\\rho\\))',
                'description': 'Air density (\\(\\rho\\)) depends on the total altitude (site altitude + building height). It affects how much force the wind exerts. We use a table from Eurocode to find \\(\\rho\\), interpolating between known values if needed.',
                'formula': '\\rho = \\text{Interpolated based on } h_{o,total} = h_o + h',
                'values': f'Total altitude (\\(h_{{o,total}}\\)) = Site altitude (\\(h_o = {h_o:.2f}\\,\\text{{m}}\\)) + Building height (\\(h = {h:.2f}\\,\\text{{m}}\\)) = {h_o_total:.2f}\\,\\text{{m}}',
                'reference': 'ES EN 1991-1-4:2015 Section 4.2, Table in Standards Modal'
            })

            if h_o_total == 0:
                rho = 1.2
            elif h_o_total == 500:
                rho = 1.12
            elif 0 < h_o_total < 500:
                rho = 1.2 + (1.12 - 1.2) * (h_o_total / 500)
            elif h_o_total == 1000:
                rho = 1.06
            elif 500 < h_o_total < 1000:
                rho = 1.12 + (1.06 - 1.12) * ((h_o_total - 500) / 500)
            elif h_o_total == 1500:
                rho = 1.00
            elif 1000 < h_o_total < 1500:
                rho = 1.06 + (1.00 - 1.06) * ((h_o_total - 1000) / 500)
            elif h_o_total == 2000:
                rho = 0.94
            elif 1500 < h_o_total < 2000:
                rho = 1.00 + (0.94 - 1.00) * ((h_o_total - 1500) / 500)
            else:
                rho = 0.94

            explanation[-1]['result'] = f'\\(\\rho = {rho:.2f}\\,\\text{{kg/m}}^3\\)'

            # Step 2: Basic wind velocity
            C_dir = 1.0
            C_seasonal = 1.0
            V_b = C_dir * C_seasonal * V_b0
            explanation.append({
                'title': 'Step 2: Calculate Basic Wind Velocity (\\(V_b\\))',
                'description': 'The basic wind velocity (\\(V_b\\)) is the starting point for wind speed calculations. It’s adjusted by directional (\\(C_{dir}\\)) and seasonal (\\(C_{seasonal}\\)) factors, which we assume as 1.0 for simplicity.',
                'formula': 'V_b = C_{dir} \\times C_{seasonal} \\times V_{b,0}',
                'values': f'\\(C_{{dir}} = {C_dir:.2f}\\), \\(C_{{seasonal}} = {C_seasonal:.2f}\\), \\(V_{{b,0}} = {V_b0:.2f}\\,\\text{{m/s}}\\)',
                'result': f'\\(V_b = {C_dir:.2f} \\times {C_seasonal:.2f} \\times {V_b0:.2f} = {V_b:.2f}\\,\\text{{m/s}}\\)',
                'reference': 'ES EN 1991-1-4:2015 Section 4.2'
            })

            q_b = 0.5 * rho * V_b ** 2 * 1e-3
            explanation.append({
                'title': 'Step 3: Calculate Basic Velocity Pressure (\\(q_b\\))',
                'description': 'The basic velocity pressure (\\(q_b\\)) converts wind speed into pressure, accounting for air density. It’s measured in kN/m².',
                'formula': 'q_b = \\frac{1}{2} \\rho V_b^2 \\times 10^{-3}',
                'values': f'\\(\\rho = {rho:.2f}\\,\\text{{kg/m}}^3\\), \\(V_b = {V_b:.2f}\\,\\text{{m/s}}\\)',
                'result': f'\\(q_b = \\frac{{1}}{{2}} \\times {rho:.2f} \\times {V_b:.2f}^2 \\times 10^{{-3}} = {q_b:.3f}\\,\\text{{kN/m}}^2\\)',
                'reference': 'ES EN 1991-1-4:2015 Section 4.5'
            })

            # Step 4: Terrain parameters
            Z_o_II = 0.05
            terrain_data = {
                1: {'Z_o': 0.01, 'Z_min': 1, 'K_r': 0.17},
                2: {'Z_o': 0.05, 'Z_min': 2, 'K_r': 0.19},
                3: {'Z_o': 0.3, 'Z_min': 3, 'K_r': 0.22},
                4: {'Z_o': 1.0, 'Z_min': 10, 'K_r': 0.24}
            }
            Z_o = terrain_data[T]['Z_o']
            Z_min = terrain_data[T]['Z_min']
            K_r = 0.19 * (Z_o / Z_o_II) ** 0.07

            explanation.append({
                'title': 'Step 4: Calculate Terrain Parameters',
                'description': 'The terrain affects how rough or smooth the wind flow is. We use the terrain category to find roughness length (\\(Z_o\\)), minimum height (\\(Z_{min}\\)), and terrain factor (\\(k_r\\)).',
                'formula': 'k_r = 0.19 \\times \\left( \\frac{Z_o}{Z_{o,II}} \\right)^{0.07}, \\quad Z_{o,II} = 0.05\\,\\text{m}',
                'values': f'Terrain Category = {T}, \\(Z_o = {Z_o:.2f}\\,\\text{{m}}\\), \\(Z_{{min}} = {Z_min:.2f}\\,\\text{{m}}\\), \\(Z_{{o,II}} = {Z_o_II:.2f}\\,\\text{{m}}\\)',
                'result': f'\\(k_r = 0.19 \\times \\left( \\frac{{{Z_o:.2f}}}{{0.05}} \\right)^{{0.07}} = {K_r:.3f}\\)',
                'reference': 'ES EN 1991-1-4:2015 Table 4.1'
            })

            # Step 5: Reference height (Z_e)
            z_e_parts = []
            if h <= b:
                z_e_parts = [{'part': 'Single', 'Z_e': h, 'height': h}]
                explanation.append({
                    'title': 'Step 5: Determine Reference Height (\\(Z_e\\))',
                    'description': 'The reference height (\\(Z_e\\)) is where we measure wind effects. For buildings where height (\\(h\\)) is less than or equal to in-wind depth (\\(b\\)), \\(Z_e = h\\) for all zones. For internal pressure, \\(Z_i = Z_e\\).',
                    'formula': 'Z_e = h \\quad \\text{if } h \\leq b, \\quad Z_i = Z_e',
                    'values': f'\\(h = {h:.2f}\\,\\text{{m}}\\), \\(b = {b:.2f}\\,\\text{{m}}\\)',
                    'result': f'\\(Z_e = {h:.2f}\\,\\text{{m}}\\), \\(Z_i = {h:.2f}\\,\\text{{m}}\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 7.2.2'
                })
            elif b < h < 2 * b:
                z_e_parts = [
                    {'part': 'Lower (Zone D)', 'Z_e': b, 'height': b},
                    {'part': 'Upper (Zone D)', 'Z_e': h, 'height': h - b}
                ]
                explanation.append({
                    'title': 'Step 5: Determine Reference Height (\\(Z_e\\))',
                    'description': 'For buildings where \\(b < h < 2b\\), Zone D (windward) is split into two parts: a lower part with height \\(b\\) (\\(Z_{e1} = b\\)) and an upper part with height \\(h - b\\) (\\(Z_{e2} = h\\)). For Zones A, B, C, E, and internal pressure, \\(Z_e = h\\) and \\(Z_i = h\\).',
                    'formula': 'Z_{e1} = b, \\quad Z_{e2} = h \\quad \\text{for Zone D}, \\quad Z_e = h \\quad \\text{for A, B, C, E}, \\quad Z_i = h',
                    'values': f'\\(h = {h:.2f}\\,\\text{{m}}\\), \\(b = {b:.2f}\\,\\text{{m}}\\), \\(2b = {2*b:.2f}\\,\\text{{m}}\\)',
                    'result': f'Zone D Lower: \\(Z_{{e1}} = {b:.2f}\\,\\text{{m}}\\), Zone D Upper: \\(Z_{{e2}} = {h:.2f}\\,\\text{{m}}\\), Zones A, B, C, E: \\(Z_e = {h:.2f}\\,\\text{{m}}\\), \\(Z_i = {h:.2f}\\,\\text{{m}}\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 7.2.2, Figure 7.5'
                })
            else:  # h >= 2b
                z_e_parts = [{'part': 'Single', 'Z_e': h, 'height': h}]
                explanation.append({
                    'title': 'Step 5: Determine Reference Height (\\(Z_e\\))',
                    'description': 'For buildings where height (\\(h\\)) is greater than or equal to twice the in-wind depth (\\(2b\\)), \\(Z_e = h\\) for all zones. For internal pressure, \\(Z_i = Z_e\\).',
                    'formula': 'Z_e = h \\quad \\text{if } h \\geq 2b, \\quad Z_i = Z_e',
                    'values': f'\\(h = {h:.2f}\\,\\text{{m}}\\), \\(b = {b:.2f}\\,\\text{{m}}\\), \\(2b = {2*b:.2f}\\,\\text{{m}}\\)',
                    'result': f'\\(Z_e = {h:.2f}\\,\\text{{m}}\\), \\(Z_i = {h:.2f}\\,\\text{{m}}\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 7.2.2'
                })

            # Step 6: Roughness and exposure factors
            roughness_explanations = []
            C_e_z_values = []
            for part in z_e_parts:
                Z_e = part['Z_e']
                C_r = K_r * math.log(Z_e / Z_o) if Z_e >= Z_min else K_r * math.log(Z_min / Z_o)
                roughness_explanations.append({
                    'title': f'Step 6: Calculate Roughness Factor (\\(C_r\\)) for {part["part"]}',
                    'description': f'The roughness factor (\\(C_r\\)) adjusts wind speed based on terrain roughness and reference height (\\(Z_e\\)) for {part["part"]}. We use \\(Z_{{min}}\\) if \\(Z_e\\) is too low.',
                    'formula': 'C_r = k_r \\times \\ln\\left( \\frac{Z_e}{Z_o} \\right) \\quad \\text{if } Z_e \\geq Z_{min}, \\quad \\text{else } k_r \\times \\ln\\left( \\frac{Z_{min}}{Z_o} \\right)',
                    'values': f'\\(k_r = {K_r:.3f}\\), \\(Z_e = {Z_e:.2f}\\,\\text{{m}}\\), \\(Z_o = {Z_o:.2f}\\,\\text{{m}}\\), \\(Z_{{min}} = {Z_min:.2f}\\,\\text{{m}}\\)',
                    'result': f'\\(C_r = {K_r:.3f} \\times \\ln\\left( \\frac{{{Z_e if Z_e >= Z_min else Z_min:.2f}}}{{{Z_o:.2f}}} \\right) = {C_r:.3f}\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 4.3.2'
                })

                if phi < 0.05:
                    C_o = 1
                elif 0.05 <= phi < 0.3:
                    C_o = 1 + 2 * s * phi
                else:
                    C_o = 1 + 0.6 * s

                roughness_explanations.append({
                    'title': f'Step 7: Calculate Orographic Factor (\\(C_o\\)) for {part["part"]}',
                    'description': f'The orographic factor (\\(C_o\\)) accounts for wind speed changes due to hills or cliffs for {part["part"]}. It depends on the upwind slope (\\(\\phi\\)) and orographic factor (\\(s\\)).',
                    'formula': 'C_o = 1 \\quad \\text{if } \\phi < 0.05, \\quad 1 + 2 \\times s \\times \\phi \\quad \\text{if } 0.05 \\leq \\phi < 0.3, \\quad \\text{else } 1 + 0.6 \\times s',
                    'values': f'\\(\\phi = {phi:.2f}\\), \\(s = {s:.2f}\\)',
                    'result': f'\\(C_o = {C_o:.3f}\\)',
                    'reference': 'ES EN 1991-1-4:2015 Annex A'
                })

                C_e_z = C_o ** 2 * C_r ** 2 * (1 + (7 * K_r) / (C_o * C_r))
                C_e_z_values.append({'part': part['part'], 'C_e_z': C_e_z, 'height': part['height']})
                roughness_explanations.append({
                    'title': f'Step 8: Calculate Exposure Factor (\\(C_e(z)\\)) for {part["part"]}',
                    'description': f'The exposure factor (\\(C_e(z)\\)) combines terrain and orographic effects to adjust wind pressure for height and location for {part["part"]}.',
                    'formula': 'C_e(z) = C_o^2 \\times C_r^2 \\times \\left( 1 + \\frac{7 \\times k_r}{C_o \\times C_r} \\right)',
                    'values': f'\\(C_o = {C_o:.3f}\\), \\(C_r = {C_r:.3f}\\), \\(k_r = {K_r:.3f}\\)',
                    'result': f'\\(C_e(z) = {C_o:.3f}^2 \\times {C_r:.3f}^2 \\times \\left( 1 + \\frac{{7 \\times {K_r:.3f}}}{{{C_o:.3f} \\times {C_r:.3f}}} \\right) = {C_e_z:.3f}\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 4.3.1'
                })

            explanation.extend(roughness_explanations)

            # Step 9: Peak velocity pressure
            peak_pressure_explanations = []
            q_p_values = []
            for ce_z in C_e_z_values:
                q_p = q_b * ce_z['C_e_z']
                q_p_values.append({'part': ce_z['part'], 'q_p': q_p, 'height': ce_z['height']})
                peak_pressure_explanations.append({
                    'title': f'Step 9: Calculate Peak Velocity Pressure (\\(q_p\\)) for {ce_z["part"]}',
                    'description': f'The peak velocity pressure (\\(q_p\\)) is the maximum pressure the wind can exert for {ce_z["part"]}, combining basic pressure and exposure effects.',
                    'formula': 'q_p = q_b \\times C_e(z)',
                    'values': f'\\(q_b = {q_b:.3f}\\,\\text{{kN/m}}^2\\), \\(C_e(z) = {ce_z["C_e_z"]:.3f}\\)',
                    'result': f'\\(q_p = {q_b:.3f} \\times {ce_z["C_e_z"]:.3f} = {q_p:.3f}\\,\\text{{kN/m}}^2\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 4.5'
                })

            explanation.extend(peak_pressure_explanations)

            # Step 10: Building parameters
            e = min(b, 2 * h)
            h_d_ratio = h / d
            explanation.append({
                'title': 'Step 10: Calculate Building Parameters',
                'description': 'We calculate the eccentricity (\\(e\\)) and height-to-depth ratio (\\(h/d\\)) to determine how wind affects different parts of the building.',
                'formula': 'e = \\min(b, 2 \\times h), \\quad h/d = \\frac{h}{d}',
                'values': f'\\(b = {b:.2f}\\,\\text{{m}}\\), \\(h = {h:.2f}\\,\\text{{m}}\\), \\(d = {d:.2f}\\,\\text{{m}}\\)',
                'result': f'\\(e = \\min({b:.2f}, 2 \\times {h:.2f}) = {e:.2f}\\,\\text{{m}}\\), \\(h/d = \\frac{{{h:.2f}}}{{{d:.2f}}} = {h_d_ratio:.2f}\\)',
                'reference': 'ES EN 1991-1-4:2015 Section 7.2.2'
            })

            cpe_data = {
                5: {
                    'A': {'C_pe_10': -1.2, 'C_pe_1': -1.4},
                    'B': {'C_pe_10': -0.8, 'C_pe_1': -1.1},
                    'C': {'C_pe_10': -0.5, 'C_pe_1': -0.5},
                    'D': {'C_pe_10': 0.8, 'C_pe_1': 1.0},
                    'E': {'C_pe_10': -0.7, 'C_pe_1': -0.7}
                },
                2: {
                    'A': {'C_pe_10': -1.2, 'C_pe_1': -1.4},
                    'B': {'C_pe_10': -0.8, 'C_pe_1': -1.1},
                    'C': {'C_pe_10': -0.5, 'C_pe_1': -0.5},
                    'D': {'C_pe_10': 0.8, 'C_pe_1': 1.0},
                    'E': {'C_pe_10': -0.5, 'C_pe_1': -0.5}
                },
                0.25: {
                    'A': {'C_pe_10': -1.2, 'C_pe_1': -1.4},
                    'B': {'C_pe_10': -0.8, 'C_pe_1': -1.1},
                    'C': {'C_pe_10': -0.5, 'C_pe_1': -0.5},
                    'D': {'C_pe_10': 0.7, 'C_pe_1': 1.0},
                    'E': {'C_pe_10': -0.3, 'C_pe_1': -0.3}
                }
            }

            if h_d_ratio > 2 and h_d_ratio < 5:
                h_d_key = 5
            elif h_d_ratio > 0.25 and h_d_ratio < 2:
                h_d_key = 2
            elif h_d_ratio <= 0.25:
                h_d_key = 0.25
            else:
                h_d_key = 5

            explanation.append({
                'title': 'Step 11: Select h/d Ratio for \\(C_{pe}\\)',
                'description': 'The \\(h/d\\) ratio determines which external pressure coefficients (\\(C_{pe}\\)) to use for each building zone (A, B, C, D, E). We select the closest \\(h/d\\) value from the Eurocode table.',
                'formula': 'h/d \\text{ key} = 5 \\quad \\text{if } h/d > 2, \\quad 2 \\quad \\text{if } 0.25 < h/d \\leq 2, \\quad 0.25 \\quad \\text{if } h/d \\leq 0.25',
                'values': f'\\(h/d = {h_d_ratio:.2f}\\)',
                'result': f'\\(h/d \\text{{ key}} = {h_d_key}\\)',
                'reference': 'ES EN 1991-1-4:2015 Table 7.1'
            })

            # Calculate areas
            A_area = (e / 5) * h
            B_area = (4 / 5 * e) * h
            C_area = (d - e) * h
            D_area_lower = b * b if b < h < 2 * b else b * h
            D_area_upper = b * (h - b) if b < h < 2 * b else 0
            E_area = b * h
            areas = [A_area, B_area, C_area, D_area_lower, D_area_upper, E_area]
            zones = ['A', 'B', 'C', 'D (Lower)', 'D (Upper)', 'E']

            explanation.append({
                'title': 'Step 12: Calculate Zone Areas',
                'description': 'Each building zone (A, B, C, D, E) has a specific area where wind pressure is applied. For Zone D, if \\(b < h < 2b\\), we split into lower (height = \\(b\\)) and upper (height = \\(h - b\\)) parts.',
                'formula': 'A_{area} = \\frac{e}{5} \\times h, \\quad B_{area} = \\frac{4}{5} \\times e \\times h, \\quad C_{area} = (d - e) \\times h, \\quad D_{area,lower} = b \\times b \\text{ or } b \\times h, \\quad D_{area,upper} = b \\times (h - b), \\quad E_{area} = b \\times h',
                'values': f'\\(e = {e:.2f}\\,\\text{{m}}\\), \\(h = {h:.2f}\\,\\text{{m}}\\), \\(d = {d:.2f}\\,\\text{{m}}\\), \\(b = {b:.2f}\\,\\text{{m}}\\)',
                'result': f'\\(A_{{area}} = {A_area:.2f}\\,\\text{{m}}^2\\), \\(B_{{area}} = {B_area:.2f}\\,\\text{{m}}^2\\), \\(C_{{area}} = {C_area:.2f}\\,\\text{{m}}^2\\), \\(D_{{area,lower}} = {D_area_lower:.2f}\\,\\text{{m}}^2\\), \\(D_{{area,upper}} = {D_area_upper:.2f}\\,\\text{{m}}^2\\), \\(E_{{area}} = {E_area:.2f}\\,\\text{{m}}^2\\)',
                'reference': 'ES EN 1991-1-4:2015 Figure 7.5'
            })

            results = []
            zone_explanations = []
            for i, (zone, area) in enumerate(zip(zones, areas)):
                if area == 0:  # Skip D (Upper) if not applicable
                    continue

                cpe_10 = cpe_data[h_d_key][zone[0]]['C_pe_10'] if zone.startswith('D') else cpe_data[h_d_key][zone]['C_pe_10']
                cpe_1 = cpe_data[h_d_key][zone[0]]['C_pe_1'] if zone.startswith('D') else cpe_data[h_d_key][zone]['C_pe_1']
                if area <= 1:
                    C_pe = cpe_1
                elif area >= 10:
                    C_pe = cpe_10
                else:
                    C_pe = cpe_1 - (cpe_1 - cpe_10) * math.log10(area)

                if zone == 'D (Lower)' and h_d_key == 0.25 and 0.25 < h_d_ratio < 2:
                    cpe_10 = 0.7 + (0.8 - 0.7) * ((h_d_ratio - 0.25) / (2 - 0.25))
                    C_pe = cpe_1 if area <= 1 else (cpe_10 if area >= 10 else cpe_1 - (cpe_1 - cpe_10) * math.log10(area))
                elif zone == 'D (Upper)' and h_d_key == 0.25 and 0.25 < h_d_ratio < 2:
                    cpe_10 = 0.7 + (0.8 - 0.7) * ((h_d_ratio - 0.25) / (2 - 0.25))
                    C_pe = cpe_1 if area <= 1 else (cpe_10 if area >= 10 else cpe_1 - (cpe_1 - cpe_10) * math.log10(area))
                elif zone == 'E' and h_d_key == 5 and 2 < h_d_ratio < 5:
                    cpe_val = -0.5 + (-0.7 - (-0.5)) * ((h_d_ratio - 2) / (5 - 2))
                    C_pe = cpe_val if area <= 1 or area >= 10 else cpe_1 - (cpe_1 - cpe_10) * math.log10(area)
                elif zone == 'E' and h_d_key == 2 and 0.25 < h_d_ratio < 2:
                    cpe_val = -0.3 + (-0.5 - (-0.3)) * ((h_d_ratio - 0.25) / (2 - 0.25))
                    C_pe = cpe_val if area <= 1 or area >= 10 else cpe_1 - (cpe_1 - cpe_10) * math.log10(area)

                zone_explanations.append({
                    'title': f'Step 13: Calculate \\(C_{{pe}}\\) for Zone {zone}',
                    'description': f'The external pressure coefficient (\\(C_{{pe}}\\)) for Zone {zone} depends on the zone’s area and the \\(h/d\\) ratio. We interpolate between \\(C_{{pe,10}}\\) (for areas \\(\\geq 10\\,\\text{{m}}^2\\)) and \\(C_{{pe,1}}\\) (for areas \\(\\leq 1\\,\\text{{m}}^2\\)).',
                    'formula': 'C_{pe} = C_{pe,1} \\quad \\text{if } \\text{area} \\leq 1\\,\\text{m}^2, \\quad C_{pe,10} \\quad \\text{if } \\text{area} \\geq 10\\,\\text{m}^2, \\quad \\text{else } C_{pe,1} - (C_{pe,1} - C_{pe,10}) \\times \\log_{10}(\\text{area})',
                    'values': f'Area = {area:.2f}\\,\\text{{m}}^2, \\(C_{{pe,10}} = {cpe_10:.2f}\\), \\(C_{{pe,1}} = {cpe_1:.2f}\\)',
                    'result': f'\\(C_{{pe}} = {C_pe:.2f}\\)',
                    'reference': 'ES EN 1991-1-4:2015 Table 7.1'
                })

                q_p = q_p_values[0]['q_p'] if zone != 'D (Upper)' else q_p_values[1]['q_p']
                W_e = q_p * C_pe
                zone_explanations[-1]['substeps'] = [{
                    'title': f'Calculate External Pressure (\\(W_e\\)) for Zone {zone}',
                    'description': f'The external pressure (\\(W_e\\)) for Zone {zone} is the peak velocity pressure times the external pressure coefficient.',
                    'formula': 'W_e = q_p \\times C_{pe}',
                    'values': f'\\(q_p = {q_p:.3f}\\,\\text{{kN/m}}^2\\), \\(C_{{pe}} = {C_pe:.2f}\\)',
                    'result': f'\\(W_e = {q_p:.3f} \\times {C_pe:.2f} = {W_e:.3f}\\,\\text{{kN/m}}^2\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 7.2'
                }]

                W_i = q_p * C_pi
                zone_explanations[-1]['substeps'].append({
                    'title': f'Calculate Internal Pressure (\\(W_i\\)) for Zone {zone}',
                    'description': f'The internal pressure (\\(W_i\\)) is the same for all zones and depends on the internal pressure coefficient (\\(C_{{pi}}\\)) and peak velocity pressure.',
                    'formula': 'W_i = q_p \\times C_{pi}',
                    'values': f'\\(q_p = {q_p:.3f}\\,\\text{{kN/m}}^2\\), \\(C_{{pi}} = {C_pi:.2f}\\)',
                    'result': f'\\(W_i = {q_p:.3f} \\times {C_pi:.2f} = {W_i:.3f}\\,\\text{{kN/m}}^2\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 7.2.9'
                })

                W_net = W_e - W_i
                zone_explanations[-1]['substeps'].append({
                    'title': f'Calculate Net Pressure (\\(W_{{net}}\\)) for Zone {zone}',
                    'description': f'The net pressure (\\(W_{{net}}\\)) is the difference between external and internal pressures, showing the effective wind load on Zone {zone}.',
                    'formula': 'W_{net} = W_e - W_i',
                    'values': f'\\(W_e = {W_e:.3f}\\,\\text{{kN/m}}^2\\), \\(W_i = {W_i:.3f}\\,\\text{{kN/m}}^2\\)',
                    'result': f'\\(W_{{net}} = {W_e:.3f} - {W_i:.3f} = {W_net:.3f}\\,\\text{{kN/m}}^2\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 7.2'
                })

                F_w = C_sC_d * W_net * area
                zone_explanations[-1]['substeps'].append({
                    'title': f'Calculate Wind Force (\\(F_w\\)) for Zone {zone}',
                    'description': f'The wind force (\\(F_w\\)) on Zone {zone} is the net pressure times the zone’s area, adjusted by the structural factor (\\(C_s C_d\\)).',
                    'formula': 'F_w = C_s C_d \\times W_{net} \\times \\text{Area}',
                    'values': f'\\(C_s C_d = {C_sC_d:.2f}\\), \\(W_{{net}} = {W_net:.3f}\\,\\text{{kN/m}}^2\\), Area = {area:.2f}\\,\\text{{m}}^2',
                    'result': f'\\(F_w = {C_sC_d:.2f} \\times {W_net:.3f} \\times {area:.2f} = {F_w:.3f}\\,\\text{{kN}}\\)',
                    'reference': 'ES EN 1991-1-4:2015 Section 7.2'
                })

                results.append({
                    'zone': zone,
                    'area': area,
                    'C_pe': C_pe,
                    'W_e': W_e,
                    'W_i': W_i,
                    'W_net': W_net,
                    'F_w': F_w
                })

            explanation.extend(zone_explanations)

            # Render results
            return render(request, 'calculator/results.html', {
                'form': form,
                'calculation': data,
                'results': results,
                'h_d_ratio': h_d_ratio,
                'explanation': explanation
            })
    else:
        initial_data = {
            'height': 19.871,
            'in_wind_depth': 30.6,
            'width': 19.26,
            'site_altitude': 0,
            'terrain_category': 3,
            'upwind_slope': 0,
            'orographic_factor': 0,
            'structural_factor': 1,
            'windward_openings': 24,
            'leeward_openings': 1,
            'parallel_openings': 5,
            'windward_area': 1.7514,
            'leeward_area': 37.43,
            'parallel_area': 1.7514,
            'internal_pressure_coeff': 0.35,
            'basic_wind_velocity': 22
        }
        form = WindPressureForm(initial=initial_data)

    return render(request, 'calculator/input_form.html', {'form': form})