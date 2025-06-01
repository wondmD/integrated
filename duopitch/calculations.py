import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

@dataclass
class ZoneResult:
    zone: str
    width: float
    length: float
    area: float
    C_pe_pos: float
    C_pe_neg: float
    C_pe: float
    w_e: float

@dataclass
class PurlinLoad:
    zone: str
    area: float
    W_e: float
    F_w_purlin: float

@dataclass
class TrussLoad:
    zone: str
    area: float
    F_w_purlin: float
    F_w_truss: float

def calculate_wind_loads(calculation) -> Tuple[List[ZoneResult], List[ZoneResult], List[PurlinLoad], List[TrussLoad], List[Dict[str, Any]]]:
    """
    Calculate wind loads for a duopitch roof.
    Returns results for θ=0° and θ=90°, purlin loads, truss loads, and calculation explanation.
    """
    explanation = []
    
    # Step 1: Basic Wind Velocity (V_b)
    v_b = calculation.c_direction * calculation.c_season * calculation.vb0
    explanation.append({
        'title': 'Basic Wind Velocity V_b',
        'description': 'The basic wind velocity (V_b) is the fundamental wind speed used for calculating wind loads on the duopitch roof, as defined in EN 1991-1-4 Section 4.2.',
        'formula': r'\( V_b = C_{\text{direction}} \times C_{\text{season}} \times V_{b,0} \)',
        'values_latex': f'\( C_{{\\text{{direction}}}} = {calculation.c_direction:.1f}, C_{{\\text{{season}}}} = {calculation.c_season:.1f}, V_{{b,0}} = {calculation.vb0:.1f} \\text{{ m/s}} \)',
        'result_latex': f'\( V_b = {v_b:.2f} \\text{{ m/s}} \)',
        'reference': 'EN 1991-1-4:2005, Section 4.2'
    })

    # Step 2: Basic Velocity Pressure (q_b)
    q_b = 0.5 * calculation.rho * v_b ** 2 / 1000  # kN/m²
    explanation.append({
        'title': 'Basic Velocity Pressure q_b',
        'description': 'The basic velocity pressure (q_b) represents the dynamic pressure exerted by the wind, calculated using air density (ρ) and the square of the basic wind velocity (V_b).',
        'formula': r'\( q_b = \frac{1}{2} \rho V_b^2 \times 10^{-3} \)',
        'values_latex': f'\( \\rho = {calculation.rho:.2f} \\text{{ kg/m}}^3, V_b = {v_b:.2f} \\text{{ m/s}} \)',
        'result_latex': f'\( q_b = {q_b:.4f} \\text{{ kN/m}}^2 \)',
        'reference': 'EN 1991-1-4:2005, Section 4.5'
    })

    # Step 3: Peak Velocity Pressure (q_p(z))
    z = calculation.ridge_height  # Reference height
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
        'title': 'Peak Velocity Pressure q_p(z)',
        'description': 'The peak velocity pressure (q_p(z)) accounts for wind effects at the reference height, incorporating terrain roughness and turbulence.',
        'formula': r'\( q_p(z) = \left[1 + 7 I_v(z)\right] \times \frac{1}{2} \rho V_m^2(z) \times 10^{-3} \)',
        'values_latex': f'\( z = {z:.1f} \\text{{ m}}, z_0 = {z_0:.3f} \\text{{ m}}, z_{{\\text{{min}}}} = {z_min:.1f} \\text{{ m}}, k_i = {k_i:.1f}, k_r = {k_r:.4f}, c_r = {c_r:.4f}, V_m = {v_m:.2f} \\text{{ m/s}}, \\rho = {calculation.rho:.2f} \\text{{ kg/m}}^3 \)',
        'result_latex': f'\( q_p(z) = {q_p:.3f} \\text{{ kN/m}}^2 \)',
        'reference': 'EN 1991-1-4:2005, Sections 4.3, 4.4, 4.5'
    })

    # Step 4: External Pressure Coefficients (C_pe)
    h = calculation.ridge_height
    b = calculation.building_width
    e = min(b, 2 * h)
    
    # Define zones for θ = 0°
    zones_0 = [
        {'zone': 'F', 'width': e / 10, 'length': e / 4},
        {'zone': 'G', 'width': e / 10, 'length': b - 2 * (e / 4)},
        {'zone': 'H', 'width': b - 2 * (e / 10), 'length': b},
        {'zone': 'I', 'width': e / 10, 'length': e / 4},
        {'zone': 'J', 'width': b - 2 * (e / 10), 'length': b}
    ]

    # Calculate C_pe values for each zone
    for zone in zones_0:
        area = zone['width'] * zone['length']
        if area <= 1:
            cpe_pos = 0.8  # C_pe,1 for small areas
            cpe_neg = -2.0
        elif area >= 10:
            cpe_pos = 0.7  # C_pe,10 for large areas
            cpe_neg = -1.5
        else:
            # Linear interpolation
            cpe_pos = 0.8 + (area - 1) * (-0.1) / 9
            cpe_neg = -2.0 + (area - 1) * 0.5 / 9
        zone['C_pe_pos'] = cpe_pos
        zone['C_pe_neg'] = cpe_neg

    explanation.append({
        'title': 'External Pressure Coefficients C_pe',
        'description': 'External pressure coefficients (C_pe) define the wind pressure distribution across the duopitch roof zones.',
        'formula': r'\( C_{pe} = \begin{cases} C_{pe,1} & \text{if } A \leq 1 \text{ m}^2 \\ C_{pe,10} & \text{if } A \geq 10 \text{ m}^2 \\ \text{Interpolate} & \text{if } 1 \text{ m}^2 < A < 10 \text{ m}^2 \end{cases} \)',
        'values_latex': f'\( e = {e:.2f} \\text{{ m}} \)',
        'result_latex': 'See zone table for C_pe values.',
        'reference': 'EN 1991-1-4:2005, Section 7.2.5'
    })

    # Step 5: Internal Pressure Coefficient (C_pi)
    c_pi = -0.3  # Conservative value for internal pressure
    explanation.append({
        'title': 'Internal Pressure Coefficient C_pi',
        'description': 'The internal pressure coefficient (C_pi) accounts for wind pressure inside the building.',
        'formula': r'\( C_{pi} = -0.3 \)',
        'values_latex': '',
        'result_latex': f'\( C_{{pi}} = {c_pi:.1f} \)',
        'reference': 'EN 1991-1-4:2005, Section 7.2.9'
    })

    # Step 6: Net Wind Pressure (w)
    results_0 = []
    for zone in zones_0:
        area = zone['width'] * zone['length']
        # Use the more critical (larger magnitude) of positive and negative pressures
        c_pe = max(abs(zone['C_pe_pos']), abs(zone['C_pe_neg']))
        if zone['C_pe_neg'] < -zone['C_pe_pos']:
            c_pe = -c_pe
        w_e = q_p * (c_pe + c_pi)
        
        results_0.append(ZoneResult(
            zone=zone['zone'],
            width=zone['width'],
            length=zone['length'],
            area=area,
            C_pe_pos=zone['C_pe_pos'],
            C_pe_neg=zone['C_pe_neg'],
            C_pe=c_pe,
            w_e=w_e
        ))

    # For θ = 90°, we use the same zones but with different coefficients
    zones_90 = zones_0.copy()
    for zone in zones_90:
        area = zone['width'] * zone['length']
        if area <= 1:
            cpe_pos = 0.7
            cpe_neg = -1.8
        elif area >= 10:
            cpe_pos = 0.6
            cpe_neg = -1.3
        else:
            cpe_pos = 0.7 + (area - 1) * (-0.1) / 9
            cpe_neg = -1.8 + (area - 1) * 0.5 / 9
        zone['C_pe_pos'] = cpe_pos
        zone['C_pe_neg'] = cpe_neg

    results_90 = []
    for zone in zones_90:
        area = zone['width'] * zone['length']
        c_pe = max(abs(zone['C_pe_pos']), abs(zone['C_pe_neg']))
        if zone['C_pe_neg'] < -zone['C_pe_pos']:
            c_pe = -c_pe
        w_e = q_p * (c_pe + c_pi)
        
        results_90.append(ZoneResult(
            zone=zone['zone'],
            width=zone['width'],
            length=zone['length'],
            area=area,
            C_pe_pos=zone['C_pe_pos'],
            C_pe_neg=zone['C_pe_neg'],
            C_pe=c_pe,
            w_e=w_e
        ))

    explanation.append({
        'title': 'Net Wind Pressure w',
        'description': 'The net wind pressure (w_e) on each roof zone combines external and internal pressure coefficients with the peak velocity pressure.',
        'formula': r'\( w_e = q_p(z) (C_{pe} + C_{pi}) \)',
        'values_latex': f'\( q_p = {q_p:.3f} \\text{{ kN/m}}^2, C_{{pi}} = {c_pi:.1f} \)',
        'result_latex': 'See results table for w_e values.',
        'reference': 'EN 1991-1-4:2005, Section 5.2'
    })

    # Calculate purlin loads (using θ = 90° results as they are typically more critical)
    purlin_loads = []
    for result in results_90:
        F_w_purlin = result.w_e * result.width  # kN/m
        purlin_loads.append(PurlinLoad(
            zone=result.zone,
            area=result.area,
            W_e=result.w_e,
            F_w_purlin=F_w_purlin
        ))

    # Calculate truss loads
    truss_loads = []
    for purlin_load in purlin_loads:
        F_w_truss = purlin_load.F_w_purlin * calculation.building_length  # kN
        truss_loads.append(TrussLoad(
            zone=purlin_load.zone,
            area=purlin_load.area,
            F_w_purlin=purlin_load.F_w_purlin,
            F_w_truss=F_w_truss
        ))

    return results_0, results_90, purlin_loads, truss_loads, explanation 