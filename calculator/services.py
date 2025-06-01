import math
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class WindLoadCalculator:
    def __init__(self, data):
        self.data = data
        self.validate_input()
        
    def validate_input(self):
        """Validate input data."""
        required_fields = [
            'height', 'in_wind_depth', 'width', 'site_altitude',
            'terrain_category', 'upwind_slope', 'orographic_factor',
            'structural_factor', 'windward_openings', 'leeward_openings',
            'parallel_openings', 'windward_area', 'leeward_area',
            'parallel_area', 'internal_pressure_coeff', 'basic_wind_velocity'
        ]
        
        for field in required_fields:
            if field not in self.data:
                raise ValidationError(f"Missing required field: {field}")
                
        if self.data['height'] <= 0:
            raise ValidationError("Building height must be positive")
        if self.data['in_wind_depth'] <= 0:
            raise ValidationError("In-wind depth must be positive")
        if self.data['width'] <= 0:
            raise ValidationError("Building width must be positive")
            
    def calculate_air_density(self):
        """Calculate air density based on altitude."""
        h_o_total = self.data['site_altitude'] + self.data['height']
        
        if h_o_total == 0:
            return 1.2
        elif h_o_total == 500:
            return 1.12
        elif 0 < h_o_total < 500:
            return 1.2 + (1.12 - 1.2) * (h_o_total / 500)
        elif h_o_total == 1000:
            return 1.06
        elif 500 < h_o_total < 1000:
            return 1.12 + (1.06 - 1.12) * ((h_o_total - 500) / 500)
        elif h_o_total == 1500:
            return 1.00
        elif 1000 < h_o_total < 1500:
            return 1.06 + (1.00 - 1.06) * ((h_o_total - 1000) / 500)
        elif h_o_total == 2000:
            return 0.94
        elif 1500 < h_o_total < 2000:
            return 1.00 + (0.94 - 1.00) * ((h_o_total - 1500) / 500)
        else:
            return 0.94
            
    def calculate_basic_wind_velocity(self):
        """Calculate basic wind velocity."""
        C_dir = 1.0
        C_seasonal = 1.0
        return C_dir * C_seasonal * self.data['basic_wind_velocity']
        
    def calculate_terrain_parameters(self):
        """Calculate terrain parameters."""
        Z_o_II = 0.05
        terrain_data = {
            1: {'Z_o': 0.01, 'Z_min': 1, 'K_r': 0.17},
            2: {'Z_o': 0.05, 'Z_min': 2, 'K_r': 0.19},
            3: {'Z_o': 0.3, 'Z_min': 3, 'K_r': 0.22},
            4: {'Z_o': 1.0, 'Z_min': 10, 'K_r': 0.24}
        }
        
        T = int(self.data['terrain_category'])
        if T not in terrain_data:
            raise ValidationError(f"Invalid terrain category: {T}")
            
        Z_o = terrain_data[T]['Z_o']
        Z_min = terrain_data[T]['Z_min']
        K_r = 0.19 * (Z_o / Z_o_II) ** 0.07
        
        return Z_o, Z_min, K_r
        
    def calculate_reference_height(self):
        """Calculate reference height based on building dimensions."""
        h = self.data['height']
        b = self.data['in_wind_depth']
        
        if h <= b:
            return [{'part': 'Single', 'Z_e': h, 'height': h}]
        elif b < h < 2 * b:
            return [
                {'part': 'Lower (Zone D)', 'Z_e': b, 'height': b},
                {'part': 'Upper (Zone D)', 'Z_e': h, 'height': h - b}
            ]
        else:
            return [{'part': 'Single', 'Z_e': h, 'height': h}]
            
    def calculate_exposure_factor(self, Z_e, Z_o, Z_min, K_r):
        """Calculate exposure factor for a given reference height."""
        # Calculate roughness factor
        C_r = K_r * math.log(Z_e / Z_o) if Z_e >= Z_min else K_r * math.log(Z_min / Z_o)
        
        # Calculate orographic factor
        phi = self.data['upwind_slope']
        s = self.data['orographic_factor']
        
        if phi < 0.05:
            C_o = 1
        elif 0.05 <= phi < 0.3:
            C_o = 1 + 2 * s * phi
        else:
            C_o = 1 + 0.6 * s
            
        # Calculate exposure factor
        return C_o ** 2 * C_r ** 2 * (1 + (7 * K_r) / (C_o * C_r))
        
    def calculate_peak_velocity_pressure(self, q_b, C_e_z):
        """Calculate peak velocity pressure."""
        return q_b * C_e_z
        
    def calculate_zone_areas(self):
        """Calculate areas for each zone."""
        h = self.data['height']
        b = self.data['in_wind_depth']
        d = self.data['width']
        e = min(b, 2 * h)
        
        A_area = (e / 5) * h
        B_area = (4 / 5 * e) * h
        C_area = (d - e) * h
        D_area_lower = b * b if b < h < 2 * b else b * h
        D_area_upper = b * (h - b) if b < h < 2 * b else 0
        E_area = b * h
        
        return [
            {'zone': 'A', 'area': A_area},
            {'zone': 'B', 'area': B_area},
            {'zone': 'C', 'area': C_area},
            {'zone': 'D (Lower)', 'area': D_area_lower},
            {'zone': 'D (Upper)', 'area': D_area_upper},
            {'zone': 'E', 'area': E_area}
        ]
        
    def calculate_pressure_coefficients(self, h_d_ratio, area):
        """Calculate pressure coefficients based on h/d ratio and area."""
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
            
        zone = 'D' if 'D' in area['zone'] else area['zone'][0]
        cpe_10 = cpe_data[h_d_key][zone]['C_pe_10']
        cpe_1 = cpe_data[h_d_key][zone]['C_pe_1']
        
        if area['area'] <= 1:
            return cpe_1
        elif area['area'] >= 10:
            return cpe_10
        else:
            return cpe_1 - (cpe_1 - cpe_10) * math.log10(area['area'])
            
    def calculate(self):
        """Perform all calculations and return results."""
        try:
            # Step 1: Calculate air density
            rho = self.calculate_air_density()
            
            # Step 2: Calculate basic wind velocity
            V_b = self.calculate_basic_wind_velocity()
            
            # Step 3: Calculate basic velocity pressure
            q_b = 0.5 * rho * V_b ** 2 * 1e-3
            
            # Step 4: Calculate terrain parameters
            Z_o, Z_min, K_r = self.calculate_terrain_parameters()
            
            # Step 5: Calculate reference height
            z_e_parts = self.calculate_reference_height()
            
            # Step 6: Calculate exposure factors
            C_e_z_values = []
            for part in z_e_parts:
                C_e_z = self.calculate_exposure_factor(part['Z_e'], Z_o, Z_min, K_r)
                C_e_z_values.append({
                    'part': part['part'],
                    'C_e_z': C_e_z,
                    'height': part['height']
                })
                
            # Step 7: Calculate peak velocity pressure
            q_p_values = []
            for ce_z in C_e_z_values:
                q_p = self.calculate_peak_velocity_pressure(q_b, ce_z['C_e_z'])
                q_p_values.append({
                    'part': ce_z['part'],
                    'q_p': q_p,
                    'height': ce_z['height']
                })
                
            # Step 8: Calculate building parameters
            h = self.data['height']
            b = self.data['in_wind_depth']
            d = self.data['width']
            e = min(b, 2 * h)
            h_d_ratio = h / d
            
            # Step 9: Calculate zone areas
            zones = self.calculate_zone_areas()
            
            # Step 10: Calculate results for each zone
            results = []
            for zone in zones:
                if zone['area'] == 0:  # Skip D (Upper) if not applicable
                    continue
                    
                # Calculate pressure coefficients
                C_pe = self.calculate_pressure_coefficients(h_d_ratio, zone)
                
                # Get peak velocity pressure
                q_p = q_p_values[0]['q_p'] if zone['zone'] != 'D (Upper)' else q_p_values[1]['q_p']
                
                # Calculate pressures
                W_e = q_p * C_pe
                W_i = q_p * self.data['internal_pressure_coeff']
                W_net = W_e - W_i
                
                # Calculate wind force
                F_w = self.data['structural_factor'] * W_net * zone['area']
                
                results.append({
                    'zone': zone['zone'],
                    'area': zone['area'],
                    'C_pe': C_pe,
                    'W_e': W_e,
                    'W_i': W_i,
                    'W_net': W_net,
                    'F_w': F_w
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error in wind load calculation: {str(e)}")
            raise
            
    def get_explanation(self):
        """Generate explanation for each calculation step."""
        # This method would generate detailed explanations for each step
        # Similar to the original code but organized by step
        # Implementation omitted for brevity
        return [] 