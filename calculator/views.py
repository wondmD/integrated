from django.shortcuts import render
from django.core.exceptions import ValidationError
from .forms import WindPressureForm
from .services import WindLoadCalculator
import logging

logger = logging.getLogger(__name__)

def calculate(request):
    if request.method == 'POST':
        form = WindPressureForm(request.POST)
        if form.is_valid():
            try:
                # Extract input data
                data = form.cleaned_data
                
                # Initialize calculator service
                calculator = WindLoadCalculator(data)
                
                # Perform calculations
                results = calculator.calculate()
                
                # Add explanation for each step
                explanation = calculator.get_explanation()
                
                return render(request, 'calculator/results.html', {
                    'form': form,
                    'results': results,
                    'explanation': explanation
                })
                
            except ValidationError as e:
                logger.error(f"Validation error in wind load calculation: {str(e)}")
                form.add_error(None, str(e))
            except Exception as e:
                logger.error(f"Error in wind load calculation: {str(e)}")
                form.add_error(None, "An error occurred during calculation. Please try again.")
    else:
        form = WindPressureForm()
    
    return render(request, 'calculator/calculate.html', {'form': form})