from django import forms
from .models import WindLoadCalculation

class WindLoadCalculationForm(forms.ModelForm):
    class Meta:
        model = WindLoadCalculation
        fields = [
            'calculation_name',
            'vb0',
            'c_direction',
            'c_season',
            'rho',
            'terrain_category',
            'ridge_height',
            'building_length',
            'building_width',
            'pitch_angle',
            'site_altitude',
            'upwind_slope',
            'horizontal_distance',
            'effective_height',
            'upwind_slope_length',
            'windward_openings_area',
            'leeward_openings_area',
            'parallel_openings_area',
            'structural_factor',
            'purlin_spacing',
            'truss_spacing',
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
            'ridge_height': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter ridge height (m)'
                }
            ),
            'building_length': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '0',
                    'placeholder': 'Enter building length (m)'
                }
            ),
            'building_width': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '0',
                    'placeholder': 'Enter building width (m)'
                }
            ),
            'pitch_angle': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '-75',
                    'max': '75',
                    'placeholder': 'Enter pitch angle (degrees)'
                }
            ),
            'site_altitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '0',
                    'placeholder': 'Enter site altitude (m)'
                }
            ),
            'upwind_slope': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter upwind slope'
                }
            ),
            'horizontal_distance': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'placeholder': 'Enter horizontal distance from crest (m)'
                }
            ),
            'effective_height': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '0',
                    'placeholder': 'Enter effective height of crest (m)'
                }
            ),
            'upwind_slope_length': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '0',
                    'placeholder': 'Enter upwind slope length (m)'
                }
            ),
            'windward_openings_area': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter windward openings area (m²)'
                }
            ),
            'leeward_openings_area': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter leeward openings area (m²)'
                }
            ),
            'parallel_openings_area': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter parallel openings area (m²)'
                }
            ),
            'structural_factor': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter structural factor'
                }
            ),
            'purlin_spacing': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '0',
                    'placeholder': 'Enter purlin spacing (m)'
                }
            ),
            'truss_spacing': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'min': '0',
                    'placeholder': 'Enter truss spacing (m)'
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
            'ridge_height': 'Ridge Height (h, m)',
            'building_length': 'Building Length (L, m)',
            'building_width': 'Building Width (b, m)',
            'pitch_angle': 'Pitch Angle (α, degrees)',
            'site_altitude': 'Site Altitude (m)',
            'upwind_slope': 'Upwind Slope (φ)',
            'horizontal_distance': 'Horizontal Distance from Crest (m)',
            'effective_height': 'Effective Height of Crest (m)',
            'upwind_slope_length': 'Upwind Slope Length (m)',
            'windward_openings_area': 'Windward Openings Area (m²)',
            'leeward_openings_area': 'Leeward Openings Area (m²)',
            'parallel_openings_area': 'Parallel Openings Area (m²)',
            'structural_factor': 'Structural Factor (c_s c_d)',
            'purlin_spacing': 'Purlin Spacing (m)',
            'truss_spacing': 'Truss Spacing (m)',
            'notes': 'Additional Notes'
        }
        help_texts = {
            'calculation_name': 'Give this calculation a descriptive name for future reference',
            'vb0': 'The 10-minute mean wind speed at 10 m above ground',
            'c_direction': 'Factor accounting for wind direction effects (typically 1.0)',
            'c_season': 'Factor accounting for seasonal wind variations (typically 1.0)',
            'rho': 'Density of air at the site (typically 1.25 kg/m³)',
            'terrain_category': 'Describes the surrounding environment\'s roughness',
            'ridge_height': 'Height from ground to the roof\'s ridge',
            'building_length': 'Length of the building parallel to the ridge',
            'building_width': 'Width of the building perpendicular to the ridge',
            'pitch_angle': 'Angle of the roof slope relative to horizontal',
            'site_altitude': 'Elevation of the site above sea level',
            'upwind_slope': 'Slope of the terrain upwind of the building',
            'horizontal_distance': 'Distance from building to crest of upwind terrain',
            'effective_height': 'Height of upwind terrain crest relative to site',
            'upwind_slope_length': 'Length of the upwind terrain slope',
            'windward_openings_area': 'Total area of openings on windward face',
            'leeward_openings_area': 'Total area of openings on leeward face',
            'parallel_openings_area': 'Total area of openings on parallel faces',
            'structural_factor': 'Factor accounting for building\'s dynamic response',
            'purlin_spacing': 'Distance between purlins supporting the roof',
            'truss_spacing': 'Distance between trusses supporting the roof',
            'notes': 'Add any additional information about this calculation'
        }

    def clean(self):
        cleaned_data = super().clean()
        ridge_height = cleaned_data.get('ridge_height')
        building_width = cleaned_data.get('building_width')

        # Validate building proportions
        if ridge_height is not None and building_width is not None:
            if ridge_height > building_width:
                raise forms.ValidationError(
                    "The ridge height cannot be greater than the building width."
                )

        return cleaned_data