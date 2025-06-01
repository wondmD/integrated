from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from latex2mathml import converter
import csv
import math
from .forms import WindLoadInputForm
from .models import WindLoadCalculation

def wind_load_analysis_on_hipped_roof(request):
    """
    Handle wind load analysis for a hipped roof, processing form inputs and rendering results.
    Supports HTML, PDF, and CSV outputs based on the 'format' parameter in GET requests.
    """
    if request.method == 'POST':
        form = WindLoadInputForm(request.POST)
        if form.is_valid():
            # Get form data
            vb0 = form.cleaned_data['vb0']
            c_direction = form.cleaned_data['c_direction']
            c_season = form.cleaned_data['c_season']
            rho = form.cleaned_data['rho']
            terrain_category = form.cleaned_data['terrain_category']
            h_e = form.cleaned_data['h_e']
            h_r = form.cleaned_data['h_r']

            # Save calculation to database
            calculation = form.save()
            
            # Calculate basic wind velocity
            vb = vb0 * c_direction * c_season
            
            # Calculate basic velocity pressure
            qb = 0.5 * rho * vb0**2
            
            # Calculate reference height
            h = h_e + h_r
            
            # Calculate roughness length and turbulence intensity based on terrain category
            if terrain_category == '0':
                z0 = 0.003
                turbulence_intensity = 0.17
            elif terrain_category == 'I':
                z0 = 0.01
                turbulence_intensity = 0.19
            elif terrain_category == 'II':
                z0 = 0.05
                turbulence_intensity = 0.21
            elif terrain_category == 'III':
                z0 = 0.3
                turbulence_intensity = 0.23
            elif terrain_category == 'IV':
                z0 = 1.0
                turbulence_intensity = 0.26
            
            # Calculate roughness factor
            kr = 0.19 * (z0/0.05)**0.07
            
            # Calculate mean wind velocity
            vm = vb * kr * (h/10)**0.07
            
            # Calculate peak velocity pressure
            qp = 0.5 * rho * vm**2 * (1 + 7 * turbulence_intensity)
            
            # Calculate external pressure coefficients for different zones
            zones = []
            
            # Zone A (windward)
            zone_a = {
                'name': 'A',
                'width': 2 * h,
                'height': h,
                'area': 2 * h * h,
                'c_pe_suction': 0.8,
                'c_pe_pressure': 0.8
            }
            zones.append(zone_a)
            
            # Zone B (leeward)
            zone_b = {
                'name': 'B',
                'width': 2 * h,
                'height': h,
                'area': 2 * h * h,
                'c_pe_suction': -0.5,
                'c_pe_pressure': None
            }
            zones.append(zone_b)
            
            # Zone C (side)
            zone_c = {
                'name': 'C',
                'width': h,
                'height': h,
                'area': h * h,
                'c_pe_suction': -0.7,
                'c_pe_pressure': None
            }
            zones.append(zone_c)
            
            # Calculate net wind pressures
            W_net_results = []
            c_pi = 0.2  # Internal pressure coefficient
            
            for zone in zones:
                # Suction case
                W_net_suction = qp * (zone['c_pe_suction'] - c_pi)
                W_net_results.append({
                    'zone': zone['name'],
                    'type': 'Suction',
                    'c_pe': zone['c_pe_suction'],
                    'c_pi': c_pi,
                    'w_net': W_net_suction
                })
                
                # Pressure case (if applicable)
                if zone['c_pe_pressure'] is not None:
                    W_net_pressure = qp * (zone['c_pe_pressure'] - c_pi)
                    W_net_results.append({
                        'zone': zone['name'],
                        'type': 'Pressure',
                        'c_pe': zone['c_pe_pressure'],
                        'c_pi': c_pi,
                        'w_net': W_net_pressure
                    })
            
            # Find maximum positive and negative pressures
            max_positive_W_net = max(result['w_net'] for result in W_net_results)
            min_negative_W_net = min(result['w_net'] for result in W_net_results)
            
            # Prepare calculation steps for display
            steps = [
                {
                    'title': 'Basic Wind Velocity',
                    'formula': 'V_b = V_{b0} \\cdot C_{direction} \\cdot C_{season}',
                    'inputs': {
                        'V_{b0}': f'{vb0:.2f} \\, \\text{{m/s}}',
                        'C_{direction}': f'{c_direction:.2f}',
                        'C_{season}': f'{c_season:.2f}'
                    },
                    'calculation_steps': [
                        f'V_b = {vb0:.2f} \\cdot {c_direction:.2f} \\cdot {c_season:.2f}',
                        f'V_b = {vb0:.2f} \\cdot {c_direction * c_season:.2f}',
                        f'V_b = {vb:.2f} \\, \\text{{m/s}}'
                    ],
                    'result': f'{vb:.2f} \\, \\text{{m/s}}',
                    'explanation': 'Basic wind velocity is calculated by multiplying the basic wind velocity by directional and seasonal factors.',
                    'considerations': [
                        'Basic wind velocity (V_b0) is the fundamental wind speed for the site',
                        'Directional factor (C_direction) accounts for wind direction effects',
                        'Seasonal factor (C_season) accounts for seasonal variations'
                    ]
                },
                {
                    'title': 'Basic Velocity Pressure',
                    'formula': 'q_b = \\frac{1}{2} \\cdot \\rho \\cdot V_{b0}^2',
                    'inputs': {
                        '\\rho': f'{rho:.2f} \\, \\text{{kg/m}}^3',
                        'V_{b0}': f'{vb0:.2f} \\, \\text{{m/s}}'
                    },
                    'calculation_steps': [
                        f'q_b = \\frac{{1}}{{2}} \\cdot {rho:.2f} \\cdot ({vb0:.2f})^2',
                        f'q_b = 0.5 \\cdot {rho:.2f} \\cdot {vb0**2:.2f}',
                        f'q_b = {qb:.2f} \\, \\text{{N/m}}^2'
                    ],
                    'result': f'{qb:.2f} \\, \\text{{N/m}}^2',
                    'explanation': 'Basic velocity pressure is calculated using the air density and basic wind velocity.',
                    'considerations': [
                        'Air density (ρ) is typically 1.25 kg/m³ at sea level',
                        'The square of velocity represents kinetic energy',
                        'The factor 1/2 comes from the kinetic energy equation'
                    ]
                },
                {
                    'title': 'Roughness Factor',
                    'formula': 'k_r = 0.19 \\cdot (\\frac{z_0}{0.05})^{0.07}',
                    'inputs': {
                        'z_0': f'{z0:.3f} \\, \\text{{m}}'
                    },
                    'calculation_steps': [
                        f'k_r = 0.19 \\cdot (\\frac{{{z0:.3f}}}{{0.05}})^{{0.07}}',
                        f'k_r = 0.19 \\cdot ({z0/0.05:.3f})^{{0.07}}',
                        f'k_r = 0.19 \\cdot {((z0/0.05)**0.07):.3f}',
                        f'k_r = {kr:.3f}'
                    ],
                    'result': f'{kr:.3f}',
                    'explanation': 'Roughness factor is calculated based on the terrain roughness length.',
                    'considerations': [
                        'Roughness length (z_0) varies with terrain type',
                        'The exponent 0.07 is a standard value for wind calculations',
                        'The factor 0.19 is derived from empirical data'
                    ]
                },
                {
                    'title': 'Mean Wind Velocity',
                    'formula': 'V_m = V_b \\cdot k_r \\cdot (\\frac{h}{10})^{0.07}',
                    'inputs': {
                        'V_b': f'{vb:.2f} \\, \\text{{m/s}}',
                        'k_r': f'{kr:.3f}',
                        'h': f'{h:.2f} \\, \\text{{m}}'
                    },
                    'calculation_steps': [
                        f'V_m = {vb:.2f} \\cdot {kr:.3f} \\cdot (\\frac{{{h:.2f}}}{{10}})^{{0.07}}',
                        f'V_m = {vb:.2f} \\cdot {kr:.3f} \\cdot ({h/10:.2f})^{{0.07}}',
                        f'V_m = {vb:.2f} \\cdot {kr:.3f} \\cdot {((h/10)**0.07):.3f}',
                        f'V_m = {vm:.2f} \\, \\text{{m/s}}'
                    ],
                    'result': f'{vm:.2f} \\, \\text{{m/s}}',
                    'explanation': 'Mean wind velocity is calculated using the basic wind velocity, roughness factor, and reference height.',
                    'considerations': [
                        'Height factor accounts for wind speed increase with height',
                        'Roughness factor reduces wind speed near the ground',
                        'The exponent 0.07 is standard for height correction'
                    ]
                },
                {
                    'title': 'Peak Velocity Pressure',
                    'formula': 'q_p = \\frac{1}{2} \\cdot \\rho \\cdot V_m^2 \\cdot (1 + 7 \\cdot I_v)',
                    'inputs': {
                        '\\rho': f'{rho:.2f} \\, \\text{{kg/m}}^3',
                        'V_m': f'{vm:.2f} \\, \\text{{m/s}}',
                        'I_v': f'{turbulence_intensity:.2f}'
                    },
                    'calculation_steps': [
                        f'q_p = \\frac{{1}}{{2}} \\cdot {rho:.2f} \\cdot ({vm:.2f})^2 \\cdot (1 + 7 \\cdot {turbulence_intensity:.2f})',
                        f'q_p = 0.5 \\cdot {rho:.2f} \\cdot {vm**2:.2f} \\cdot (1 + {7*turbulence_intensity:.2f})',
                        f'q_p = 0.5 \\cdot {rho:.2f} \\cdot {vm**2:.2f} \\cdot {1+7*turbulence_intensity:.2f}',
                        f'q_p = {qp:.2f} \\, \\text{{N/m}}^2'
                    ],
                    'result': f'{qp:.2f} \\, \\text{{N/m}}^2',
                    'explanation': 'Peak velocity pressure is calculated using the mean wind velocity, air density, and turbulence intensity.',
                    'considerations': [
                        'Turbulence intensity (I_v) accounts for wind gusts',
                        'The factor 7 is a standard value for gust effects',
                        'Peak pressure is higher than mean pressure due to gusts'
                    ]
                }
            ]
            
            context = {
                'form': form,
                'calculation': calculation,
                'zones': zones,
                'W_net_results': W_net_results,
                'max_positive_W_net': max_positive_W_net,
                'min_negative_W_net': min_negative_W_net,
                'steps': steps
            }

            # Check for output format (via GET parameter)
            output_format = request.GET.get('format', 'html')
            if output_format == 'pdf':
                # Convert LaTeX formulas to MathML for PDF compatibility
                for step in context['steps']:
                    if step['formula']:
                        step['formula_mathml'] = convert(step['formula'])
                # Render template to string and generate PDF
                html_string = render_to_string('wind_load_result.html', context)
                html = HTML(string=html_string)
                pdf = html.write_pdf()
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="wind_load_hipped_roof.pdf"'
                return response
            elif output_format == 'csv':
                # Generate CSV for net wind pressures
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="wind_load_hipped_roof.csv"'
                writer = csv.writer(response)
                writer.writerow(['Zone', 'Type', 'C_pe', 'C_pi', 'W_net (kN/m²)'])
                for result in W_net_results:
                    writer.writerow([result['zone'], result['type'], result['c_pe'], result['c_pi'], f'{result["w_net"]:.3f}'])
                return response
            else:
                # Render HTML result page
                return render(request, 'wind_load_result.html', context)
        else:
            # Invalid form: re-render with error messages
            return render(request, 'wind_load_form.html', {'form': form})
    else:
        # GET request: Display empty form
        form = WindLoadInputForm()
        return render(request, 'wind_load_form.html', {'form': form})

def wind_load_history(request):
    """
    Display a history of all wind load calculations.
    """
    calculations = WindLoadCalculation.objects.all().order_by('-created_at')
    return render(request, 'wind_load_history.html', {'calculations': calculations})