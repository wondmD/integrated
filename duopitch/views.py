from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML
import tempfile
import os
from .models import WindLoadCalculation
from .forms import WindLoadCalculationForm
from .calculations import calculate_wind_loads

def wind_load_calculator(request):
    if request.method == 'POST':
        form = WindLoadCalculationForm(request.POST)
        if form.is_valid():
            # Get form data
            data = form.cleaned_data
            
            # Calculate wind loads
            results = calculate_wind_loads(
                vb0=data['vb0'],
                c_direction=data['c_direction'],
                c_season=data['c_season'],
                rho=data['rho'],
                terrain_category=data['terrain_category'],
                ridge_height=data['ridge_height'],
                building_length=data['building_length'],
                building_width=data['building_width'],
                pitch_angle=data['pitch_angle'],
                site_altitude=data['site_altitude'],
                upwind_slope=data['upwind_slope'],
                horizontal_distance=data['horizontal_distance'],
                effective_height=data['effective_height'],
                upwind_slope_length=data['upwind_slope_length'],
                windward_openings_area=data['windward_openings_area'],
                leeward_openings_area=data['leeward_openings_area'],
                parallel_openings_area=data['parallel_openings_area'],
                structural_factor=data['structural_factor'],
                purlin_spacing=data['purlin_spacing'],
                truss_spacing=data['truss_spacing']
            )
            
            # Save calculation to database
            calculation = form.save(commit=False)
            calculation.results = results
            calculation.save()
            
            # Store calculation ID in session for PDF generation
            request.session['last_calculation_id'] = calculation.id
            
            # Prepare context for template
            context = {
                'form': form,
                'results': results,
                'calculation': calculation,
                'show_results': True
            }
            
            return render(request, 'duopitch/duopitch_input.html', context)
    else:
        form = WindLoadCalculationForm()
    
    return render(request, 'duopitch/duopitch_input.html', {'form': form})

def download_pdf(request):
    calculation_id = request.session.get('last_calculation_id')
    if not calculation_id:
        messages.error(request, 'No calculation results available for download.')
        return redirect('duopitch:wind_load_calculator')
    
    try:
        calculation = WindLoadCalculation.objects.get(id=calculation_id)
    except WindLoadCalculation.DoesNotExist:
        messages.error(request, 'Calculation not found.')
        return redirect('duopitch:wind_load_calculator')
    
    # Render HTML template with calculation results
    html_string = render_to_string('duopitch/pdf_template.html', {
        'calculation': calculation,
        'results': calculation.results
    })
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="wind_load_calculation_{calculation.id}.pdf"'
    
    # Generate PDF using WeasyPrint
    HTML(string=html_string).write_pdf(response)
    
    return response

def wind_load_list(request):
    calculations = WindLoadCalculation.objects.all().order_by('-created_at')
    return render(request, 'duopitch/list.html', {'calculations': calculations})

def wind_load_detail(request, pk):
    calculation = get_object_or_404(WindLoadCalculation, pk=pk)
    results_0, results_90, purlin_loads, truss_loads, explanation = calculate_wind_loads(calculation)
    
    # Calculate max/min pressures for display
    max_positive_W_net = max((result.w_e for result in results_0), default=0)
    min_negative_W_net = min((result.w_e for result in results_0), default=0)
    
    context = {
        'calculation': calculation,
        'results_0': results_0,
        'results_90': results_90,
        'purlin_loads': purlin_loads,
        'truss_loads': truss_loads,
        'explanation': explanation,
        'max_positive_W_net': max_positive_W_net,
        'min_negative_W_net': min_negative_W_net,
    }
    
    # Handle PDF export
    if request.GET.get('format') == 'pdf':
        section = request.GET.get('section', 'all')
        return generate_pdf(request, context, section)
    
    return render(request, 'duopitch/results.html', context)

def wind_load_delete(request, pk):
    calculation = get_object_or_404(WindLoadCalculation, pk=pk)
    if request.method == 'POST':
        calculation.delete()
        messages.success(request, 'Calculation deleted successfully.')
        return redirect('duopitch:wind_load_list')
    return render(request, 'duopitch/delete.html', {'calculation': calculation})