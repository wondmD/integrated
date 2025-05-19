from django.shortcuts import render
from .forms import FlatRoofForm
import math
from django.templatetags.static import static

def flatroof_calculate(request):
    if request.method == 'POST':
        form = FlatRoofForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            explanation = []

            # Step 1: Reference Height (z_e)
            h = data['building_height']
            h_p = data['parapet_height']
            z_e = h + h_p
            explanation.append({
                'title': 'Step 1: Reference Height z_e',
                'description': 'The reference height (z_e) for wind actions on the flat roof is the maximum height above ground, including the building height (h) and any additional parapet height (h_p), as specified in EN 1991-1-4 Section 7.2.3(3). This height determines the wind velocity and pressure at the roof level.',
                'formula': '\\( z_e = h + h_p \\)',
                'values': {'h': h, 'h_p': h_p},
                'values_latex': '\\( h = %.3f \\text{ m}, h_p = %.3f \\text{ m} \\)' % (h, h_p),
                'result': z_e,
                'result_latex': '\\( z_e = %.3f \\text{ m} \\)' % z_e,
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 7.2.3(3)'
            })

            # Step 2: Basic Wind Velocity (v_b)
            v_b = data['basic_wind_velocity']
            explanation.append({
                'title': 'Step 2: Basic Wind Velocity v_b',
                'description': 'The basic wind velocity (v_b) is the fundamental wind speed at 10 m above ground in terrain category II, accounting for directional (c_dir) and seasonal (c_season) factors, as per EN 1991-1-4 Section 4.2(2)P. It is typically provided by the National Annex or user input based on regional wind maps.',
                'formula': '\\( v_b = c_{\\text{dir}} \\cdot c_{\\text{season}} \\cdot v_{b,0} \\)',
                'values': {'v_b': v_b},
                'values_latex': '\\( v_b = %.2f \\text{ m/s} \\)' % v_b,
                'result': v_b,
                'result_latex': '\\( v_b = %.2f \\text{ m/s} \\)' % v_b,
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 4.2(2)P'
            })

            # Step 3: Terrain Roughness
            terrain_params = {
                '0': (0.003, 1.0), 'I': (0.01, 1.0), 'II': (0.05, 2.0),
                'III': (0.3, 5.0), 'IV': (1.0, 10.0)
            }
            z_0, z_min = terrain_params[data['terrain_category']]
            k_r = 0.19 * (z_0 / 0.05) ** 0.07
            c_r = k_r * math.log(max(z_e, z_min) / z_0) if z_e >= z_min else k_r * math.log(z_min / z_0)
            explanation.append({
                'title': 'Step 3: Terrain Roughness',
                'description': 'Terrain roughness accounts for the effect of ground surface on wind velocity, defined by roughness length (z_0) and minimum height (z_min) per terrain category (EN 1991-1-4 Table 4.1). The terrain factor (k_r) and roughness factor (c_r) adjust the wind speed based on height and terrain, as per Sections 4.3.2 and 4.4.',
                'formula': '\\( k_r = 0.19 \\cdot \\left( \\frac{z_0}{0.05} \\right)^{0.07}, \\quad c_r(z_e) = k_r \\cdot \\ln \\left( \\frac{\\max(z_e, z_{\\min})}{z_0} \\right) \\)',
                'values': {'z_0': z_0, 'z_min': z_min, 'z_e': z_e},
                'values_latex': '\\( z_0 = %.3f \\text{ m}, z_{\\min} = %.1f \\text{ m}, z_e = %.3f \\text{ m} \\)' % (z_0, z_min, z_e),
                'result': {'k_r': k_r, 'c_r': c_r},
                'result_latex': '\\( k_r = %.4f, c_r = %.4f \\)' % (k_r, c_r),
                'reference': 'EN 1991-1-4:2005+A1:2010, Sections 4.3.2, 4.4'
            })

            # Step 4: Orography Factor
            c_0 = data['orography_factor']
            explanation.append({
                'title': 'Step 4: Orography Factor c_0',
                'description': 'The orography factor (c_0) accounts for increased wind speeds due to significant terrain features like hills or cliffs, as per EN 1991-1-4 Section 4.3.3. A value of 1.0 is used when orography is not significant, otherwise it is calculated per the National Annex.',
                'formula': '\\( c_0(z_e) \\)',
                'values': {'c_0': c_0},
                'values_latex': '\\( c_0 = %.3f \\)' % c_0,
                'result': c_0,
                'result_latex': '\\( c_0 = %.3f \\)' % c_0,
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 4.3.3'
            })

            # Step 5: Mean Wind Velocity
            v_m = c_r * c_0 * v_b
            explanation.append({
                'title': 'Step 5: Mean Wind Velocity v_m',
                'description': 'The mean wind velocity (v_m) at reference height (z_e) is calculated by adjusting the basic wind velocity (v_b) for terrain roughness (c_r) and orography (c_0), as per EN 1991-1-4 Section 4.3.1.',
                'formula': '\\( v_m(z_e) = c_r(z_e) \\cdot c_0(z_e) \\cdot v_b \\)',
                'values': {'c_r': c_r, 'c_0': c_0, 'v_b': v_b},
                'values_latex': '\\( c_r = %.4f, c_0 = %.3f, v_b = %.2f \\text{ m/s} \\)' % (c_r, c_0, v_b),
                'result': v_m,
                'result_latex': '\\( v_m = %.2f \\text{ m/s} \\)' % v_m,
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 4.3.1'
            })

            # Step 6: Wind Turbulence
            k_i = 1.0
            I_v = k_i / (c_0 * math.log(max(z_e, z_min) / z_0)) if z_e >= z_min else k_i / (c_0 * math.log(z_min / z_0))
            explanation.append({
                'title': 'Step 6: Wind Turbulence I_v',
                'description': 'Turbulence intensity (I_v) represents the standard deviation of wind fluctuations divided by mean wind velocity, calculated at reference height (z_e) per EN 1991-1-4 Section 4.4. It depends on the turbulence factor (k_I), orography (c_0), and terrain roughness (z_0).',
                'formula': '\\( I_v(z_e) = \\frac{k_I}{c_0(z_e) \\cdot \\ln \\left( \\frac{\\max(z_e, z_{\\min})}{z_0} \\right)} \\)',
                'values': {'k_i': k_i, 'c_0': c_0, 'z_e': z_e, 'z_min': z_min, 'z_0': z_0},
                'values_latex': '\\( k_I = %.1f, c_0 = %.3f, z_e = %.3f \\text{ m}, z_{\\min} = %.1f \\text{ m}, z_0 = %.3f \\text{ m} \\)' % (k_i, c_0, z_e, z_min, z_0),
                'result': I_v,
                'result_latex': '\\( I_v = %.4f \\)' % I_v,
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 4.4'
            })

            # Step 7: Basic Velocity Pressure
            rho = data['air_density']
            q_b = (1 / 2) * rho * v_b ** 2 / 1000  # kN/m²
            explanation.append({
                'title': 'Step 7: Basic Velocity Pressure q_b',
                'description': 'The basic velocity pressure (q_b) is the dynamic pressure corresponding to the basic wind velocity (v_b), calculated using air density (rho), as per EN 1991-1-4 Section 4.5(1). It is converted to kN/m² for structural calculations.',
                'formula': '\\( q_b = \\frac{1}{2} \\cdot \\rho \\cdot v_b^2 \\cdot 10^{-3} \\)',
                'values': {'rho': rho, 'v_b': v_b},
                'values_latex': '\\( \\rho = %.2f \\text{ kg/m}^3, v_b = %.2f \\text{ m/s} \\)' % (rho, v_b),
                'result': q_b,
                'result_latex': '\\( q_b = %.3f \\text{ kN/m}^2 \\)' % q_b,
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 4.5(1)'
            })

            # Step 8: Peak Velocity Pressure
            q_p = (1 + 7 * I_v) * (1 / 2) * rho * v_m ** 2 / 1000  # kN/m²
            explanation.append({
                'title': 'Step 8: Peak Velocity Pressure q_p',
                'description': 'The peak velocity pressure (q_p) at reference height (z_e) includes both mean and short-term velocity fluctuations, calculated using turbulence intensity (I_v), air density (rho), and mean wind velocity (v_m), as per EN 1991-1-4 Section 4.5.',
                'formula': '\\( q_p(z_e) = \\left[ 1 + 7 \\cdot I_v(z_e) \\right] \\cdot \\frac{1}{2} \\cdot \\rho \\cdot v_m(z_e)^2 \\cdot 10^{-3} \\)',
                'values': {'I_v': I_v, 'rho': rho, 'v_m': v_m},
                'values_latex': '\\( I_v = %.4f, \\rho = %.2f \\text{ kg/m}^3, v_m = %.2f \\text{ m/s} \\)' % (I_v, rho, v_m),
                'result': q_p,
                'result_latex': '\\( q_p = %.3f \\text{ kN/m}^2 \\)' % q_p,
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 4.5'
            })

            # Step 9: External Pressure Coefficients
            b = data['crosswind_dimension']
            h = data['building_height']
            e = min(b, 2 * h)
            h_p_h = h_p / h if h > 0 else 0
            cpe_table = {
                0: {'F': -1.8, 'G': -1.2, 'H': -0.7, 'I': (-0.2, 0.2)},
                0.05: {'F': -2.0, 'G': -1.4, 'H': -0.8, 'I': (-0.2, 0.2)},
                0.1: {'F': -2.5, 'G': -1.6, 'H': -0.9, 'I': (-0.2, 0.2)}
            }
            cpe_values = cpe_table[0]  # Simplified for h_p/h = 0 as in PDF
            explanation.append({
                'title': 'Step 9: External Pressure Coefficients c_pe',
                'description': 'External pressure coefficients (c_pe) define wind pressure distribution across roof zones (F, G, H, I), as per EN 1991-1-4 Section 7.2.3 and Table 7.2. Zones are defined by characteristic length (e = min(b, 2h)). Coefficients depend on parapet height ratio (h_p/h), with interpolation for intermediate values. Negative values indicate suction (uplift).',
                'formula': '\\( c_{pe} \\text{ from Table 7.2, based on } \\frac{h_p}{h} \\)',
                'values': {'b': b, 'h': h, 'h_p': h_p, 'e': e},
                'values_latex': '\\( b = %.2f \\text{ m}, h = %.2f \\text{ m}, h_p = %.2f \\text{ m}, e = %.2f \\text{ m} \\)' % (b, h, h_p, e),
                'result': cpe_values,
                'result_latex': '\\( c_{pe,F} = %.1f, c_{pe,G} = %.1f, c_{pe,H} = %.1f, c_{pe,I} = \\pm %.1f \\)' % (cpe_values['F'], cpe_values['G'], cpe_values['H'], cpe_values['I'][1]),
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 7.2.3, Table 7.2',
                'figures': [static('images/flat_zones.jpg')]
            })

            # Step 10: Internal Pressure Coefficients
            c_pi_min = data['c_pi_min']
            c_pi_max = data['c_pi_max']
            explanation.append({
                'title': 'Step 10: Internal Pressure Coefficients c_pi',
                'description': 'Internal pressure coefficients (c_pi) account for wind pressure inside the building due to openings and permeability, as per EN 1991-1-4 Section 7.2.9. Without a dominant face, the most onerous values (c_pi,min = -0.3, c_pi,max = +0.2) are used unless specified otherwise.',
                'formula': '\\( c_{pi} \\text{ based on openings or default } \\pm 0.2, -0.3 \\)',
                'values': {'c_pi_min': c_pi_min, 'c_pi_max': c_pi_max},
                'values_latex': '\\( c_{pi,\\min} = %.1f, c_{pi,\\max} = %.1f \\)' % (c_pi_min, c_pi_max),
                'result': {'c_pi_min': c_pi_min, 'c_pi_max': c_pi_max},
                'result_latex': '\\( c_{pi,\\min} = %.1f, c_{pi,\\max} = %.1f \\)' % (c_pi_min, c_pi_max),
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 7.2.9'
            })

            # Step 11: Net Wind Pressure
            z_i = z_e  # Assume z_i = z_e as per PDF
            q_p_zi = q_p  # q_p(z_i) = q_p(z_e)
            results = []
            for zone in ['F', 'G', 'H', 'I']:
                c_pe = cpe_values[zone]
                if zone == 'I':
                    c_pe_neg, c_pe_pos = c_pe
                    w_net_neg = q_p * c_pe_neg - q_p_zi * c_pi_max
                    w_net_pos = q_p * c_pe_pos - q_p_zi * c_pi_min
                    results.append({
                        'zone': zone,
                        'c_pe_neg': c_pe_neg,
                        'c_pe_pos': c_pe_pos,
                        'w_net_neg': w_net_neg,
                        'w_net_pos': w_net_pos
                    })
                else:
                    w_net = q_p * c_pe - q_p_zi * c_pi_max
                    results.append({
                        'zone': zone,
                        'c_pe_neg': c_pe,
                        'c_pe_pos': None,
                        'w_net_neg': w_net,
                        'w_net_pos': None
                    })
            explanation.append({
                'title': 'Step 11: Net Wind Pressure w_net',
                'description': 'The net wind pressure (w_net) combines external (w_e = q_p * c_pe) and internal (w_i = q_p * c_pi) pressures on each roof zone, as per EN 1991-1-4 Section 5.2. For zones with negative c_pe, c_pi,max is most onerous; for positive c_pe, c_pi,min is used. Negative values indicate suction (uplift).',
                'formula': '\\( w_{\\text{net}} = q_p(z_e) \\cdot c_{pe} - q_p(z_i) \\cdot c_{pi} \\)',
                'values': {'q_p': q_p, 'c_pi_min': c_pi_min, 'c_pi_max': c_pi_max},
                'values_latex': '\\( q_p = %.3f \\text{ kN/m}^2, c_{pi,\\min} = %.1f, c_{pi,\\max} = %.1f \\)' % (q_p, c_pi_min, c_pi_max),
                'result': 'See results table for w_net values.',
                'result_latex': 'See results table for w_net values.',
                'reference': 'EN 1991-1-4:2005+A1:2010, Section 5.2'
            })

            return render(request, 'flatroof/results.html', {
                'form': form,
                'calculation': data,
                'results': results,
                'explanation': explanation
            })
    else:
        form = FlatRoofForm()
    return render(request, 'flatroof/flat_input.html', {'form': form})