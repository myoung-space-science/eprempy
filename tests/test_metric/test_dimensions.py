from eprempy import metric


def test_dimension_quantities():
    """Look up quantities in a given metric system for a dimension."""
    cases = {
        'L': {
            'mks': {'length'},
            'cgs': {'capacitance', 'length'},
        },
        'L / T': {
            'mks': {'velocity', 'speed'},
            'cgs': {'conductance', 'velocity', 'speed'},
        },
        'M * L / T^2': {
            'mks': {'force'},
            'cgs': {'force'},
        },
        'M * L^2 / T^2': {
            'mks': {'energy', 'work'},
            'cgs': {'energy', 'work'},
        },
    }
    for string, systems in cases.items():
        dimension = metric.dimension(string)
        for system, quantities in systems.items():
            assert dimension.quantities(system) == quantities


