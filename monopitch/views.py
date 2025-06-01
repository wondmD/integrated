from django.shortcuts import render, redirect
from django.contrib import messages
from .models import WindLoadCalculation
from .forms import WindLoadInputForm
import math
from django.templatetags.static import static
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from latex2mathml import converter
import csv

def wind_load_calculation(request):
    if request.method == 'POST':
        form = WindLoadInputForm(request.POST)
        if form.is_valid():
            calculation = form.save()
            messages.success(request, 'Wind load calculation saved successfully!')
            return redirect('wind_load_detail', pk=calculation.pk)
    else:
        form = WindLoadInputForm()
    
    return render(request, 'monopitch/wind_load_form.html', {'form': form})

def wind_load_detail(request, pk):
    calculation = WindLoadCalculation.objects.get(pk=pk)
    explanation = []

    # Step 1: Basic Wind Velocity (V_b)
    v_b = calculation.c_direction * calculation.c_season * calculation.vb0
    explanation.append({
        'title': 'Step 1: Basic Wind Velocity V_b',
        'description': 'The basic wind velocity (V_b) is the fundamental wind speed used for calculating wind loads on the monopitch roof, as defined in ES EN 1991-1-4:2015 Section 4.2.',
        'formula': '\\( V_b = C_{\\text{direction}} \\times C_{\\text{season}} \\times V_{b,0} \\)',
        'values': {
            'c_direction': calculation.c_direction,
            'c_season': calculation.c_season,
            'v_b_0': calculation.vb0
        },
        'result': v_b,
        'reference': 'ES EN 1991-1-4:2015, Section 4.2'
    })

    # Step 2: Basic Velocity Pressure (q_b)
    q_b = 0.5 * calculation.rho * v_b ** 2 / 1000  # kN/m²
    explanation.append({
        'title': 'Step 2: Basic Velocity Pressure q_b',
        'description': 'The basic velocity pressure (q_b) represents the dynamic pressure exerted by the wind, calculated using air density (rho) and the square of the basic wind velocity (V_b).',
        'formula': '\\( q_b = \\frac{1}{2} \\rho V_b^2 \\times 10^{-3} \\)',
        'values': {
            'rho': calculation.rho,
            'v_b': v_b
        },
        'result': q_b,
        'reference': 'ES EN 1991-1-4:2015, Section 4.5'
    })

    # Step 3: Peak Velocity Pressure (q_p(z))
    z = calculation.get_total_height()  # Reference height
    terrain_params = {
        '0': (0.003, 1),
        'I': (0.01, 1),
        'II': (0.05, 2),
        'III': (0.3, 5),
        'IV': (1.0, 10)
    }
    z_0, z_min = terrain_params[calculation.terrain_category]
    k_i = 1.0
    k_r = 0.19 * (z_0 / 0.05) ** 0.07
    c_r = k_r * math.log(z / z_0) if z >= z_min else k_r * math.log(z_min / z_0)
    v_m = c_r * v_b
    l_v = k_i / math.log(z / z_0) if z >= z_min else k_i / math.log(z_min / z_0)
    q_p = (1 + 7 * l_v) * 0.5 * calculation.rho * v_m ** 2 / 1000

    explanation.append({
        'title': 'Step 3: Peak Velocity Pressure q_p(z)',
        'description': 'The peak velocity pressure (q_p(z)) accounts for wind effects at the reference height, incorporating terrain roughness and turbulence.',
        'formula': '\\( q_p(z) = \\left[1 + 7 I_v(z)\\right] \\times \\frac{1}{2} \\rho V_m^2(z) \\times 10^{-3} \\)',
        'values': {
            'z': z,
            'z_0': z_0,
            'z_min': z_min,
            'k_i': k_i,
            'k_r': k_r,
            'c_r': c_r,
            'v_m': v_m,
            'l_v': l_v,
            'rho': calculation.rho
        },
        'result': q_p,
        'reference': 'ES EN 1991-1-4:2015, Sections 4.3, 4.4, 4.5'
    })

    # Step 4: External Pressure Coefficients (C_pe)
    h = calculation.h_r
    b = 2 * calculation.h_r  # Assuming building width is twice the ridge height
    e = min(b, 2 * h)
    zones = [
        {'zone': 'F', 'width': e / 10, 'length': e / 4},
        {'zone': 'G', 'width': e / 10, 'length': b - 2 * (e / 4)},
        {'zone': 'H', 'width': b - 2 * (e / 10), 'length': b}
    ]

    # Calculate C_pe values for each zone
    for zone in zones:
        area = zone['width'] * zone['length']
        if area <= 1:
            cpe = -2.0  # C_pe,1 for small areas
        elif area >= 10:
            cpe = -1.5  # C_pe,10 for large areas
        else:
            # Linear interpolation
            cpe = -2.0 + (area - 1) * 0.5 / 9
        zone['C_pe'] = cpe

    explanation.append({
        'title': 'Step 4: External Pressure Coefficients C_pe',
        'description': 'External pressure coefficients (C_pe) define the wind pressure distribution across the monopitch roof zones.',
        'formula': '\\( C_{pe} = \\begin{cases} C_{pe,1} & \\text{if } A \\leq 1 \\text{ m}^2 \\\\ C_{pe,10} & \\text{if } A \\geq 10 \\text{ m}^2 \\\\ \\text{Interpolate} & \\text{if } 1 \\text{ m}^2 < A < 10 \\text{ m}^2 \\end{cases} \\)',
        'values': {
            'e': e,
            'zones': zones
        },
        'result': 'See zone table for C_pe values.',
        'reference': 'ES EN 1991-1-4:2015, Section 7.2.4'
    })

    # Step 5: Internal Pressure Coefficient (C_pi)
    c_pi = -0.3  # Conservative value for internal pressure
    explanation.append({
        'title': 'Step 5: Internal Pressure Coefficient C_pi',
        'description': 'The internal pressure coefficient (C_pi) accounts for wind pressure inside the building.',
        'formula': '\\( C_{pi} = -0.3 \\)',
        'values': {},
        'result': c_pi,
        'reference': 'ES EN 1991-1-4:2015, Section 7.2.9'
    })

    # Step 6: Net Wind Pressure (w)
    results = []
    for zone in zones:
        w_e = q_p * (zone['C_pe'] + c_pi)
        results.append({
            'zone': zone['zone'],
            'area': zone['width'] * zone['length'],
            'C_pe': zone['C_pe'],
            'w_e': w_e
        })

    explanation.append({
        'title': 'Step 6: Net Wind Pressure w',
        'description': 'The net wind pressure (w_e) on each roof zone combines external and internal pressure coefficients with the peak velocity pressure.',
        'formula': '\\( w_e = q_p(z) (C_{pe} + C_{pi}) \\)',
        'values': {
            'q_p': q_p,
            'c_pi': c_pi
        },
        'result': 'See results table for w_e values.',
        'reference': 'ES EN 1991-1-4:2015, Section 5.2'
    })

    context = {
        'calculation': calculation,
        'explanation': explanation,
        'results': results
    }
    return render(request, 'monopitch/wind_load_detail.html', context)

def wind_load_list(request):
    calculations = WindLoadCalculation.objects.all().order_by('-created_at')
    return render(request, 'monopitch/wind_load_list.html', {'calculations': calculations})

def wind_load_analysis_on_monopitch_roof(request):
    """
    Handle wind load analysis for a monopitch roof, processing form inputs and rendering results.
    Supports HTML, PDF, and CSV outputs based on the 'format' parameter in GET requests.
    """
    if request.method == 'POST':
        form = WindLoadInputForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            explanation = []

            # Step 1: Basic Wind Velocity (V_b)
            c_direction = data.get('c_direction', 1.0)
            c_season = data.get('c_season', 1.0)
            v_b_0 = data['vb0']
            v_b = c_direction * c_season * v_b_0
            explanation.append({
                'title': 'Step 1: Basic Wind Velocity V_b',
                'description': 'The basic wind velocity (V_b) is the fundamental wind speed used for calculating wind loads on the monopitch roof, as defined in ES EN 1991-1-4:2015 Section 4.2.',
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
            rho = data.get('rho', 1.25)  # Use provided rho or default to 1.25
            q_b = 0.5 * rho * v_b ** 2 / 1000  # kN/m²
            explanation.append({
                'title': 'Step 2: Basic Velocity Pressure q_b',
                'description': 'The basic velocity pressure (q_b) represents the dynamic pressure exerted by the wind, calculated using air density (rho) and the square of the basic wind velocity (V_b).',
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
            z = data['h_r']  # Reference height
            terrain_params = {'0': (0.003, 1), 'I': (0.01, 1), 'II': (0.05, 2), 'III': (0.3, 5), 'IV': (1.0, 10)}
            z_0, z_min = terrain_params[data['terrain_category']]
            k_i = 1.0
            k_r = 0.19 * (z_0 / 0.05) ** 0.07
            c_r = k_r * math.log(z / z_0) if z >= z_min else k_r * math.log(z_min / z_0)
            v_m = c_r * v_b
            l_v = k_i / math.log(z / z_0) if z >= z_min else k_i / math.log(z_min / z_0)
            q_p = (1 + 7 * l_v) * 0.5 * rho * v_m ** 2 / 1000

            explanation.append({
                'title': 'Step 3: Peak Velocity Pressure q_p(z)',
                'description': 'The peak velocity pressure (q_p(z)) accounts for wind effects at the reference height, incorporating terrain roughness and turbulence.',
                'formula': '\\( q_p(z) = \\left[1 + 7 I_v(z)\\right] \\times \\frac{1}{2} \\rho V_m^2(z) \\times 10^{-3} \\)',
                'values': {
                    'z': z,
                    'z_0': z_0,
                    'z_min': z_min,
                    'k_i': k_i,
                    'k_r': k_r,
                    'c_r': c_r,
                    'v_m': v_m,
                    'l_v': l_v,
                    'rho': rho
                },
                'values_latex': '\\( z = %.1f \\text{ m}, z_0 = %.2f \\text{ m}, z_{\\text{min}} = %.1f \\text{ m}, k_i = %.1f, k_r = %.4f, c_r = %.4f, V_m = %.2f \\text{ m/s}, \\rho = %.2f \\text{ kg/m}^3 \\)' % (z, z_0, z_min, k_i, k_r, c_r, v_m, rho),
                'result': q_p,
                'result_latex': '\\( q_p(z) = %.3f \\text{ kN/m}^2 \\)' % q_p,
                'reference': 'ES EN 1991-1-4:2015, Sections 4.3, 4.4, 4.5'
            })

            # Step 4: External Pressure Coefficients (C_pe)
            h = data['h_r']
            b = 2 * data['h_r']  # Assuming building width is twice the ridge height
            e = min(b, 2 * h)
            zones = [
                {'zone': 'F', 'width': e / 10, 'length': e / 4},
                {'zone': 'G', 'width': e / 10, 'length': b - 2 * (e / 4)},
                {'zone': 'H', 'width': b - 2 * (e / 10), 'length': b}
            ]

            # Calculate C_pe values for each zone
            for zone in zones:
                area = zone['width'] * zone['length']
                if area <= 1:
                    cpe = -2.0  # C_pe,1 for small areas
                elif area >= 10:
                    cpe = -1.5  # C_pe,10 for large areas
                else:
                    # Linear interpolation
                    cpe = -2.0 + (area - 1) * 0.5 / 9
                zone['C_pe'] = cpe

            explanation.append({
                'title': 'Step 4: External Pressure Coefficients C_pe',
                'description': 'External pressure coefficients (C_pe) define the wind pressure distribution across the monopitch roof zones.',
                'formula': '\\( C_{pe} = \\begin{cases} C_{pe,1} & \\text{if } A \\leq 1 \\text{ m}^2 \\\\ C_{pe,10} & \\text{if } A \\geq 10 \\text{ m}^2 \\\\ \\text{Interpolate} & \\text{if } 1 \\text{ m}^2 < A < 10 \\text{ m}^2 \\end{cases} \\)',
                'values': {
                    'e': e,
                    'zones': zones
                },
                'result': 'See zone table for C_pe values.',
                'reference': 'ES EN 1991-1-4:2015, Section 7.2.4'
            })

            # Step 5: Internal Pressure Coefficient (C_pi)
            c_pi = -0.3  # Conservative value for internal pressure
            explanation.append({
                'title': 'Step 5: Internal Pressure Coefficient C_pi',
                'description': 'The internal pressure coefficient (C_pi) accounts for wind pressure inside the building.',
                'formula': '\\( C_{pi} = -0.3 \\)',
                'values': {},
                'result': c_pi,
                'reference': 'ES EN 1991-1-4:2015, Section 7.2.9'
            })

            # Step 6: Net Wind Pressure (w)
            results = []
            for zone in zones:
                w_e = q_p * (zone['C_pe'] + c_pi)
                results.append({
                    'zone': zone['zone'],
                    'area': zone['width'] * zone['length'],
                    'C_pe': zone['C_pe'],
                    'w_e': w_e
                })

            explanation.append({
                'title': 'Step 6: Net Wind Pressure w',
                'description': 'The net wind pressure (w_e) on each roof zone combines external and internal pressure coefficients with the peak velocity pressure.',
                'formula': '\\( w_e = q_p(z) (C_{pe} + C_{pi}) \\)',
                'values': {
                    'q_p': q_p,
                    'c_pi': c_pi
                },
                'result': 'See results table for w_e values.',
                'reference': 'ES EN 1991-1-4:2015, Section 5.2'
            })

            # Save calculation to database
            calculation = form.save()

            context = {
                'form': form,
                'calculation': calculation,
                'results': results,
                'explanation': explanation,
                'max_positive_W_net': max(result['w_e'] for result in results),
                'min_negative_W_net': min(result['w_e'] for result in results)
            }

            # Check for output format (via GET parameter)
            output_format = request.GET.get('format', 'html')
            if output_format == 'pdf':
                # Convert LaTeX formulas to MathML for PDF compatibility
                for step in context['explanation']:
                    if step['formula']:
                        step['formula_mathml'] = converter.convert(step['formula'])
                # Render template to string and generate PDF
                html_string = render_to_string('monopitch/results.html', context)
                html = HTML(string=html_string)
                pdf = html.write_pdf()
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="wind_load_monopitch_roof.pdf"'
                return response
            elif output_format == 'csv':
                # Generate CSV for net wind pressures
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="wind_load_monopitch_roof.csv"'
                writer = csv.writer(response)
                writer.writerow(['Zone', 'Area (m²)', 'C_pe', 'W_net (kN/m²)'])
                for result in results:
                    writer.writerow([result['zone'], f'{result["area"]:.2f}', f'{result["C_pe"]:.3f}', f'{result["w_e"]:.3f}'])
                return response
            else:
                # Render HTML result page
                return render(request, 'monopitch/results.html', context)
        else:
            # Invalid form: re-render with error messages
            return render(request, 'monopitch/monopitch_input.html', {'form': form})
    else:
        # GET request: Display empty form
        form = WindLoadInputForm()
        return render(request, 'monopitch/monopitch_input.html', {'form': form})