from django.test import TestCase
from .services import WindLoadCalculator
from django.core.exceptions import ValidationError

class WindLoadCalculatorTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'height': 19.871,
            'in_wind_depth': 30.6,
            'width': 19.26,
            'site_altitude': 0,
            'terrain_category': 3,
            'upwind_slope': 0,
            'orographic_factor': 0,
            'structural_factor': 1,
            'windward_openings': 24,
            'leeward_openings': 1,
            'parallel_openings': 5,
            'windward_area': 1.7514,
            'leeward_area': 37.43,
            'parallel_area': 1.7514,
            'internal_pressure_coeff': 0.35,
            'basic_wind_velocity': 22
        }
        
    def test_validation(self):
        """Test input validation."""
        # Test missing field
        invalid_data = self.valid_data.copy()
        del invalid_data['height']
        with self.assertRaises(ValidationError):
            WindLoadCalculator(invalid_data)
            
        # Test negative height
        invalid_data = self.valid_data.copy()
        invalid_data['height'] = -1
        with self.assertRaises(ValidationError):
            WindLoadCalculator(invalid_data)
            
        # Test invalid terrain category
        invalid_data = self.valid_data.copy()
        invalid_data['terrain_category'] = 5
        with self.assertRaises(ValidationError):
            WindLoadCalculator(invalid_data)
            
    def test_air_density_calculation(self):
        """Test air density calculation."""
        calculator = WindLoadCalculator(self.valid_data)
        rho = calculator.calculate_air_density()
        self.assertAlmostEqual(rho, 1.2, places=2)
        
        # Test at different altitudes
        data = self.valid_data.copy()
        data['site_altitude'] = 500
        calculator = WindLoadCalculator(data)
        rho = calculator.calculate_air_density()
        self.assertAlmostEqual(rho, 1.12, places=2)
        
    def test_basic_wind_velocity_calculation(self):
        """Test basic wind velocity calculation."""
        calculator = WindLoadCalculator(self.valid_data)
        V_b = calculator.calculate_basic_wind_velocity()
        self.assertEqual(V_b, 22.0)  # C_dir and C_seasonal are 1.0
        
    def test_terrain_parameters_calculation(self):
        """Test terrain parameters calculation."""
        calculator = WindLoadCalculator(self.valid_data)
        Z_o, Z_min, K_r = calculator.calculate_terrain_parameters()
        self.assertEqual(Z_o, 0.3)  # For terrain category 3
        self.assertEqual(Z_min, 3)  # For terrain category 3
        self.assertAlmostEqual(K_r, 0.22, places=2)
        
    def test_reference_height_calculation(self):
        """Test reference height calculation."""
        calculator = WindLoadCalculator(self.valid_data)
        z_e_parts = calculator.calculate_reference_height()
        self.assertEqual(len(z_e_parts), 1)  # Single part since h > 2b
        self.assertEqual(z_e_parts[0]['Z_e'], self.valid_data['height'])
        
        # Test case where b < h < 2b
        data = self.valid_data.copy()
        data['height'] = 40
        data['in_wind_depth'] = 30.6
        calculator = WindLoadCalculator(data)
        z_e_parts = calculator.calculate_reference_height()
        self.assertEqual(len(z_e_parts), 2)  # Two parts for Zone D
        
    def test_exposure_factor_calculation(self):
        """Test exposure factor calculation."""
        calculator = WindLoadCalculator(self.valid_data)
        Z_o, Z_min, K_r = calculator.calculate_terrain_parameters()
        C_e_z = calculator.calculate_exposure_factor(
            self.valid_data['height'],
            Z_o,
            Z_min,
            K_r
        )
        self.assertGreater(C_e_z, 0)  # Should be positive
        
    def test_zone_areas_calculation(self):
        """Test zone areas calculation."""
        calculator = WindLoadCalculator(self.valid_data)
        zones = calculator.calculate_zone_areas()
        self.assertEqual(len(zones), 6)  # A, B, C, D (Lower), D (Upper), E
        
        # Check that areas are positive
        for zone in zones:
            self.assertGreaterEqual(zone['area'], 0)
            
    def test_pressure_coefficients_calculation(self):
        """Test pressure coefficients calculation."""
        calculator = WindLoadCalculator(self.valid_data)
        h_d_ratio = self.valid_data['height'] / self.valid_data['width']
        zone = {'zone': 'A', 'area': 10}
        C_pe = calculator.calculate_pressure_coefficients(h_d_ratio, zone)
        self.assertAlmostEqual(C_pe, -1.2, places=2)  # C_pe_10 for zone A
        
    def test_full_calculation(self):
        """Test full calculation process."""
        calculator = WindLoadCalculator(self.valid_data)
        results = calculator.calculate()
        
        # Check that we have results for all zones
        self.assertGreater(len(results), 0)
        
        # Check that each result has all required fields
        for result in results:
            self.assertIn('zone', result)
            self.assertIn('area', result)
            self.assertIn('C_pe', result)
            self.assertIn('W_e', result)
            self.assertIn('W_i', result)
            self.assertIn('W_net', result)
            self.assertIn('F_w', result)
            
            # Check that values are reasonable
            self.assertGreaterEqual(result['area'], 0)
            self.assertGreaterEqual(result['W_net'], -10)  # Net pressure shouldn't be too negative
            self.assertLessEqual(result['W_net'], 10)  # Net pressure shouldn't be too positive
