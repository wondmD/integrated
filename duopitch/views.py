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

def wind_load_calculate(request):
    if request.method == 'POST':
        form = WindLoadCalculationForm(request.POST)
        if form.is_valid():
            calculation = form.save()
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
    else:
        form = WindLoadCalculationForm()
    
    return render(request, 'duopitch/duopitch_input.html', {'form': form})

def generate_pdf(request, context, section='all'):
    """Generate PDF for the specified section of the results."""
    template = 'duopitch/results.html'
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output:
        # Render the template with the context
        html_string = render_to_string(template, context)
        
        # Create PDF using WeasyPrint
        HTML(string=html_string).write_pdf(output.name)
        
        # Read the PDF file
        with open(output.name, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            
            # Set the filename based on the section
            filename = f'wind_load_results_{section}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
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