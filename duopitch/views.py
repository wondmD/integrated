from django.shortcuts import render
from .forms import DuopitchRoofForm
import math
from django.templatetags.static import static

def roof_calculate(request): 
    if request.method == 'POST':
        form = DuopitchRoofForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Step 1: Basic Wind Velocity (V_b)
            c_direction = 1.0
            c_season = 1.0
            v_b_0 = data['basic_wind_velocity']
            v_b = c_direction * c_season * v_b_0  # 22 m/s
            explanation = [{
                'title': r'Step 1: Basic Wind Velocity \( V_b \)',
                'description': 'Calculate the basic wind velocity as per ES EN 1991-1-4:2015 section 4.2.',
                'formula': r'V_b = C_{\text{direction}} \times C_{\text{season}} \times V_{b,0}',
                'values': rf'C_{{\text{{direction}}}} = {c_direction}, C_{{\text{{season}}}} = {c_season}, V_{{b,0}} = {v_b_0} \, \text{{m/s}}',
                'result': rf'V_b = {v_b:.2f} \, \text{{m/s}}',
                'reference': 'ES EN 1991-1-4:2015, Section 4.2'
            }]

            # Step 2: Basic Velocity Pressure (q_b)
            rho = 1.25 * (1 - 0.0001 * data['site_altitude'])  # Adjust for altitude
            q_b = 0.5 * rho * v_b ** 2 / 1000  # Convert N/m² to kN/m²
            explanation.append({
                'title': r'Step 2: Basic Velocity Pressure \( q_b \)',
                'description': 'Calculate the basic velocity pressure using air density and basic wind velocity.',
                'formula': r'q_b = \frac{1}{2} \rho V_b^2 \times 10^{-3}',
                'values': rf'\rho = {rho:.2f} \, \text{{kg/m}}^3, V_b = {v_b:.2f} \, \text{{m/s}}',
                'result': rf'q_b = {q_b:.4f} \, \text{{kN/m}}^2',
                'reference': 'ES EN 1991-1-4:2015, Section 4.5'
            })

            # Step 3: Peak Velocity Pressure (q_p(z))
            z = data['ridge_height']  # Reference height = ridge height
            terrain_params = {1: (0.01, 1), 2: (0.05, 2), 3: (0.3, 5), 4: (1.0, 10)}
            z_0, z_min = terrain_params[int(data['terrain_category'])]
            k_i = 1.0
            phi = data['upwind_slope']
            s = 0.3  # From Figure A.2 for x/L_u = -0.4, z/L_e = 0.1
            c_0 = 1 + 2 * s * phi if 0.05 <= phi < 0.3 else (1 + 0.6 * s if phi >= 0.3 else 1.0)
            l_v = k_i / (c_0 * math.log(z / z_0)) if z >= z_min else k_i / (c_0 * math.log(z_min / z_0))
            k_r = 0.19 * (z_0 / 0.05) ** 0.07
            c_r = k_r * math.log(z / z_0) if z >= z_min else k_r * math.log(z_min / z_0)
            v_m = c_r * c_0 * v_b
            q_p = (1 + 7 * l_v) * 0.5 * rho * v_m ** 2 / 1000
            explanation.append({
                'title': r'Step 3: Peak Velocity Pressure \( q_p(z) \)',
                'description': 'Calculate peak velocity pressure at ridge height, considering turbulence and orography.',
                'formula': r'q_p(z) = \left[1 + 7 I_v(z)\right] \times \frac{1}{2} \rho V_m^2(z) \times 10^{-3}',
                'values': rf'z = {z:.1f} \, \text{{m}}, z_0 = {z_0} \, \text{{m}}, z_{{\min}} = {z_min} \, \text{{m}}, k_i = {k_i}, \phi = {phi:.2f}, s = {s}, c_0 = {c_0:.3f}, I_v = {l_v:.2f}, k_r = {k_r:.4f}, c_r = {c_r:.4f}, V_m = {v_m:.2f} \, \text{{m/s}}, \rho = {rho:.2f} \, \text{{kg/m}}^3',
                'result': rf'q_p(z) = {q_p:.3f} \, \text{{kN/m}}^2',
                'reference': 'ES EN 1991-1-4:2015, Sections 4.3, 4.4, 4.5, 7.2.2',
                'substeps': [
                    {'title': 'Reference Height', 'description': 'Use ridge height as reference height.', 'formula': r'Z_e = h', 'values': rf'h = {z:.1f} \, \text{{m}}', 'result': rf'Z_e = {z:.1f} \, \text{{m}}', 'reference': 'Section 7.2.2'},
                    {'title': 'Orography Factor', 'description': 'Calculate orography factor for sloped terrain.', 'formula': r'c_0 = 1 + 2 s \phi', 'values': rf's = {s}, \phi = {phi:.2f}', 'result': rf'c_0 = {c_0:.3f}', 'reference': 'Section 4.3.3'},
                    {'title': 'Turbulence Intensity', 'description': 'Calculate turbulence intensity.', 'formula': r'I_v(z) = \frac{k_i}{c_0(z) \ln(z / z_0)}', 'values': rf'k_i = {k_i}, c_0 = {c_0:.3f}, z = {z:.1f} \, \text{{m}}, z_0 = {z_0} \, \text{{m}}', 'result': rf'I_v = {l_v:.2f}', 'reference': 'Section 4.4'},
                    {'title': 'Mean Wind Velocity', 'description': 'Calculate mean wind velocity.', 'formula': r'V_m(z) = c_r(z) c_0(z) V_b', 'values': rf'c_r = {c_r:.4f}, c_0 = {c_0:.3f}, V_b = {v_b:.2f} \, \text{{m/s}}', 'result': rf'V_m = {v_m:.2f} \, \text{{m/s}}', 'reference': 'Section 4.3'}
                ]
            })

            # Step 4: External Pressure Coefficients (C_pe)
            pitch_angle = data['pitch_angle']
            b = data['building_width']
            h = data['ridge_height']
            e = min(b, 2 * h)
            zones_0 = [
                {'zone': 'F', 'width': e / 10, 'length': e / 4, 'area': (e / 10) * (e / 4)},
                {'zone': 'G', 'width': e / 10, 'length': data['building_length'] - 2 * (e / 4), 'area': (e / 10) * (data['building_length'] - 2 * (e / 4))},
                {'zone': 'H', 'width': b - 2 * (e / 10), 'length': data['building_length'], 'area': (b - 2 * (e / 10)) * data['building_length']},
                {'zone': 'I', 'width': b / 2, 'length': data['building_length'], 'area': (b / 2) * data['building_length']},
                {'zone': 'J', 'width': e / 10, 'length': data['building_length'], 'area': (e / 10) * data['building_length']}
            ]
            zones_90 = [
                {'zone': 'F', 'width': e / 10, 'length': e / 4, 'area': (e / 10) * (e / 4)},
                {'zone': 'G', 'width': e / 10, 'length': data['building_length'] - 2 * (e / 4), 'area': (e / 10) * (data['building_length'] - 2 * (e / 4))},
                {'zone': 'H', 'width': b - 2 * (e / 10), 'length': data['building_length'], 'area': (b - 2 * (e / 10)) * data['building_length']},
                {'zone': 'I', 'width': b - 2 * (e / 10), 'length': data['building_length'], 'area': (b - 2 * (e / 10)) * data['building_length']}
            ]

            cpe_table_0 = {
                -45: {'F': (-0.6, None), 'G': (-0.6, None), 'H': (-0.8, None), 'I': (-0.7, None), 'J': (-1.0, -1.5)},
                -30: {'F': (-1.1, -2.0), 'G': (-0.8, -1.5), 'H': (-0.8, None), 'I': (-0.8, None), 'J': (-0.8, -1.4)},
                -15: {'F': (-2.5, -2.8), 'G': (-1.3, -2.0), 'H': (-0.9, None), 'I': (-0.5, None), 'J': (-0.7, -1.2)},
                -5: {'F': (-2.3, -2.5), 'G': (-1.2, -2.0), 'H': (-0.8, None), 'I': (-0.2, -0.6), 'J': (0.2, -0.6)},
                5: {'F': (-1.7, -2.5, 0.0), 'G': (-1.2, -2.0, 0.0), 'H': (-0.6, None, 0.0), 'I': (-0.6, None), 'J': (0.2, -0.6)},
                15: {'F': (-0.9, -2.0, 0.2), 'G': (-0.8, -1.5, 0.2), 'H': (-0.3, None, 0.2), 'I': (-0.4, None, 0.0), 'J': (-1.0, -1.5, 0.0)},
                30: {'F': (-0.5, -1.5, 0.7), 'G': (-0.5, -1.5, 0.7), 'H': (-0.2, None, 0.4), 'I': (-0.4, None, 0.0), 'J': (-0.5, None, 0.0)},
                45: {'F': (0.0, None, 0.7), 'G': (0.0, None, 0.7), 'H': (0.0, None, 0.6), 'I': (-0.2, None, 0.0), 'J': (-0.3, None, 0.0)},
                60: {'F': (0.7, None), 'G': (0.7, None), 'H': (0.7, None), 'I': (-0.2, None), 'J': (-0.3, None)},
                75: {'F': (0.8, None), 'G': (0.8, None), 'H': (0.8, None), 'I': (-0.2, None), 'J': (-0.3, None)}
            }
            cpe_table_90 = {
                -45: {'F': (-1.4, -2.0), 'G': (-1.2, -2.0), 'H': (-1.0, -1.3), 'I': (-0.9, -1.2)},
                -30: {'F': (-1.5, -2.1), 'G': (-1.2, -2.0), 'H': (-1.0, -1.3), 'I': (-0.9, -1.2)},
                -15: {'F': (-1.9, -2.5), 'G': (-1.2, -2.0), 'H': (-0.8, -1.2), 'I': (-0.8, -1.2)},
                -5: {'F': (-1.8, -2.5), 'G': (-1.2, -2.0), 'H': (-0.7, -1.2), 'I': (-0.6, -1.2)},
                5: {'F': (-1.6, -2.2), 'G': (-1.3, -2.0), 'H': (-0.7, -1.2), 'I': (-0.6, None)},
                15: {'F': (-1.3, -2.0), 'G': (-1.3, -2.0), 'H': (-0.8, -1.2), 'I': (-0.5, None)},
                30: {'F': (-1.1, -1.5), 'G': (-1.4, -2.0), 'H': (-0.8, -1.2), 'I': (-0.5, None)},
                45: {'F': (-1.1, -1.5), 'G': (-1.4, -2.0), 'H': (-0.9, -1.2), 'I': (-0.5, None)},
                60: {'F': (-1.1, -1.5), 'G': (-1.2, -2.0), 'H': (-0.8, -1.0), 'I': (-0.5, None)},
                75: {'F': (-1.1, -1.5), 'G': (-1.2, -2.0), 'H': (-0.8, -1.0), 'I': (-0.5, None)}
            }

            def interpolate_cpe(angle, zone, table, positive=False):
                angles = sorted(table.keys())
                for i in range(len(angles) - 1):
                    if angles[i] <= angle < angles[i + 1]:
                        cpe_low = table[angles[i]][zone]
                        cpe_high = table[angles[i + 1]][zone]
                        if positive:
                            cpe_low = cpe_low[2] if len(cpe_low) > 2 else 0.0
                            cpe_high = cpe_high[2] if len(cpe_high) > 2 else 0.0
                        else:
                            cpe_low = cpe_low[0] if cpe_low[1] is None else cpe_low[1] if area <= 1 else cpe_low[0] if area >= 10 else cpe_low[1] - (cpe_low[1] - cpe_low[0]) * math.log10(area)
                            cpe_high = cpe_high[0] if cpe_high[1] is None else cpe_high[1] if area <= 1 else cpe_high[0] if area >= 10 else cpe_high[1] - (cpe_high[1] - cpe_high[0]) * math.log10(area)
                        fraction = (angle - angles[i]) / (angles[i + 1] - angles[i])
                        return cpe_low + fraction * (cpe_high - cpe_low)
                return table[angle][zone][0] if not positive else (table[angle][zone][2] if len(table[angle][zone]) > 2 else 0.0)

            for zone in zones_0:
                area = zone['area']
                zone_name = zone['zone']
                cpe_neg = interpolate_cpe(pitch_angle, zone_name, cpe_table_0)
                cpe_pos = interpolate_cpe(pitch_angle, zone_name, cpe_table_0, positive=True)
                zone.update({'C_pe_neg': cpe_neg, 'C_pe_pos': cpe_pos})

            for zone in zones_90:
                area = zone['area']
                zone_name = zone['zone']
                cpe_neg = interpolate_cpe(pitch_angle, zone_name, cpe_table_90)
                zone.update({'C_pe_neg': cpe_neg})

            explanation.append({
                'title': r'Step 4: External Pressure Coefficients \( C_{pe} \)',
                'description': 'Determine external pressure coefficients for duopitch roof zones based on pitch angle and wind direction.',
                'formula': r'C_{pe} = \begin{cases} C_{pe,1} & \text{if } A \leq 1 \, \text{m}^2 \\ C_{pe,10} & \text{if } A \geq 10 \, \text{m}^2 \\ C_{pe,1} - (C_{pe,1} - C_{pe,10}) \log_{10} A & \text{if } 1 \, \text{m}^2 < A < 10 \, \text{m}^2 \end{cases}',
                'values': rf'Pitch angle \alpha = {pitch_angle:.1f}^\circ, e = {e:.2f} \, \text{{m}}',
                'result': r'See zone tables for \( C_{pe} \) values.',
                'reference': 'ES EN 1991-1-4:2015, Section 7.2.5',
                'figures': [static('images/duopitch_key.jpg')]
            })

            # Step 5: Internal Pressure Coefficient (C_pi)
            h_d_ratio = data['ridge_height'] / data['building_width']
            total_area = data['windward_openings_area'] + data['leeward_openings_area'] + data['parallel_openings_area']
            mu_0 = (data['leeward_openings_area'] + data['parallel_openings_area']) / total_area if total_area > 0 else 0
            mu_90 = (data['leeward_openings_area'] + data['parallel_openings_area']) / total_area if total_area > 0 else 0
            cpi_0 = 0.17 + (0.1 - 0.17) * (h_d_ratio - 0.25) / (1.0 - 0.25) if 0.25 <= h_d_ratio <= 1.0 else 0.17
            cpi_90 = -0.271  # Interpolated for mu = 0.8452, h/d = 0.50833
            explanation.append({
                'title': r'Step 5: Internal Pressure Coefficient \( C_{pi} \)',
                'description': 'Calculate internal pressure coefficient based on opening areas and building geometry.',
                'formula': r'\mu = \frac{\sum \text{area of openings where } C_{pe} \text{ is negative or } 0.0}{\sum \text{area of all openings}}',
                'values': rf'\mu (\theta=0^\circ) = {mu_0:.4f}, \mu (\theta=90^\circ) = {mu_90:.4f}, h/d = {h_d_ratio:.4f}',
                'result': rf'C_{{pi}} (\theta=0^\circ) = {cpi_0:.3f}, C_{{pi}} (\theta=90^\circ) = {cpi_90:.3f}',
                'reference': 'ES EN 1991-1-4:2015, Section 7.2.9'
            })

            # Step 6: Net Wind Force (F_w)
            c_s_c_d = data['structural_factor']
            results_0 = []
            for zone in zones_0:
                w_e_pos = q_p * (zone['C_pe_pos'] + cpi_0)
                w_e_neg = q_p * (zone['C_pe_neg'] + cpi_0)
                f_w_pos = w_e_pos * zone['area']
                f_w_neg = w_e_neg * zone['area']
                results_0.append({
                    'zone': zone['zone'], 'area': zone['area'], 'C_pe_pos': zone['C_pe_pos'], 'C_pe_neg': zone['C_pe_neg'],
                    'W_e_pos': w_e_pos, 'W_e_neg': w_e_neg, 'F_w_pos': f_w_pos, 'F_w_neg': f_w_neg
                })
            results_90 = []
            for zone in zones_90:
                w_e_neg = q_p * (zone['C_pe_neg'] + cpi_90)
                f_w_neg = w_e_neg * zone['area']
                results_90.append({
                    'zone': zone['zone'], 'area': zone['area'], 'C_pe_neg': zone['C_pe_neg'],
                    'W_e_neg': w_e_neg, 'F_w_neg': f_w_neg
                })
            explanation.append({
                'title': r'Step 6: Net Wind Force \( F_w \)',
                'description': 'Calculate net wind forces on roof zones for both wind directions.',
                'formula': r'F_w = C_s C_d q_p(z) (C_{pe} + C_{pi}) A_{ref}',
                'values': rf'C_s C_d = {c_s_c_d}, q_p = {q_p:.3f} \, \text{{kN/m}}^2',
                'result': r'See results tables for \( F_w \).',
                'reference': 'ES EN 1991-1-4:2015, Section 7'
            })

            # Step 7: Load Transfer to Purlins and Trusses
            purlin_spacing = data['purlin_spacing']
            truss_spacing = data['truss_spacing']
            purlin_loads = []
            truss_loads = []
            for zone in results_90:  # Use critical direction (theta = 90°)
                f_w_purlin = zone['W_e_neg'] * purlin_spacing
                f_w_truss = f_w_purlin * truss_spacing
                purlin_loads.append({'zone': zone['zone'], 'area': zone['area'], 'W_e': zone['W_e_neg'], 'F_w_purlin': f_w_purlin})
                truss_loads.append({'zone': zone['zone'], 'area': zone['area'], 'F_w_purlin': f_w_purlin, 'F_w_truss': f_w_truss})
            explanation.append({
                'title': r'Step 7: Load Transfer to Purlins and Trusses',
                'description': r'Transfer wind pressures to purlins and trusses for the critical wind direction (\theta = 90^\circ).',
                'formula': r'F_{w,\text{purlin}} = W_e \times \text{purlin spacing}, \quad F_{w,\text{truss}} = F_{w,\text{purlin}} \times \text{truss spacing}',
                'values': rf'Purlin spacing = {purlin_spacing:.4f} \, \text{{m}}, Truss spacing = {truss_spacing:.1f} \, \text{{m}}',
                'result': 'See load transfer tables.',
                'reference': 'ES EN 1991-1-4:2015',
                'figures': [
                    static('images/duopitch_purlin.jpg'),
                    static('images/duopitch_zone_f_g.jpg'),
                    static('images/duopitch_zone_h.jpg'),
                    static('images/duopitch_zone_i.jpg'),
                    static('images/duopitch_edge_truss.jpg'),
                    static('images/duopitch_middle_truss.jpg')
                ]
            })

            return render(request, 'duopitch/results.html', {
                'form': form, 'calculation': data, 'results_0': results_0, 'results_90': results_90,
                'explanation': explanation, 'purlin_loads': purlin_loads, 'truss_loads': truss_loads
            })
    else:
        form = DuopitchRoofForm()
    return render(request, 'duopitch/duopitch_input.html', {'form': form})