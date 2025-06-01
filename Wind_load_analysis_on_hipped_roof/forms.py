from django import forms
from .models import WindLoadCalculation

class WindLoadInputForm(forms.ModelForm):
    class Meta:
        model = WindLoadCalculation
        fields = [
            'calculation_name',
            'vb0',
            'c_direction',
            'c_season',
            'rho',
            'terrain_category',
            'h_e',
            'h_r',
            'notes'
        ]
        widgets = {
            'calculation_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter a name for this calculation'}
            ),
            'vb0': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '0',
                    'max': '100',
                    'placeholder': 'Enter wind velocity (m/s)'
                }
            ),
            'c_direction': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'max': '1',
                    'placeholder': 'Enter directional factor'
                }
            ),
            'c_season': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'max': '1',
                    'placeholder': 'Enter seasonal factor'
                }
            ),
            'rho': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '1.0',
                    'max': '1.5',
                    'placeholder': 'Enter air density (kg/m³)'
                }
            ),
            'terrain_category': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'h_e': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter height to eaves (m)'
                }
            ),
            'h_r': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter height to ridge (m)'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': '3',
                    'placeholder': 'Add any additional notes here'
                }
            )
        }
        labels = {
            'calculation_name': 'Calculation Name',
            'vb0': 'Fundamental Basic Wind Velocity (V_b0, m/s)',
            'c_direction': 'Directional Factor (C_direction)',
            'c_season': 'Seasonal Factor (C_season)',
            'rho': 'Air Density (ρ, kg/m³)',
            'terrain_category': 'Terrain Category',
            'h_e': 'Height to Eaves (h_e, m)',
            'h_r': 'Height from Eaves to Ridge (h_r, m)',
            'notes': 'Additional Notes'
        }
        help_texts = {
            'calculation_name': 'Give this calculation a descriptive name for future reference',
            'vb0': 'The 10-minute mean wind speed at 10 m above ground',
            'c_direction': 'Factor accounting for wind direction effects (typically 1.0)',
            'c_season': 'Factor accounting for seasonal wind variations (typically 1.0)',
            'rho': 'Density of air at the site (typically 1.25 kg/m³)',
            'terrain_category': 'Describes the surrounding environment\'s roughness',
            'h_e': 'Height from ground to the eaves of the roof',
            'h_r': 'Height from the eaves to the roof ridge',
            'notes': 'Add any additional information about this calculation'
        }

    def clean(self):
        cleaned_data = super().clean()
        h_e = cleaned_data.get('h_e')
        h_r = cleaned_data.get('h_r')

        # Validate total height
        if h_e is not None and h_r is not None:
            total_height = h_e + h_r
            if total_height > 200:  # Assuming 200m as a reasonable maximum height
                raise forms.ValidationError(
                    "The total height (eaves + ridge) cannot exceed 200 meters."
                )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Select, forms.Textarea)):
                field.widget.attrs['class'] = 'form-control'