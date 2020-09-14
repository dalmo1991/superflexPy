"""
Copyright 2020 Marco Dal Molin et al.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file is part of the SuperflexPy modelling framework. For details about it,
visit the page https://superflexpy.readthedocs.io

CODED BY: Marco Dal Molin
DESIGNED BY: Marco Dal Molin, Fabrizio Fenicia

This file implements the model M4 presented in Kavetsi and Fenicia, 2011.

Reference
---------

Kavetski, D., and F. Fenicia (2011), Elements of a flexible approach
for conceptual hydrological modeling: 2. Application and experimental insights,
Water Resour. Res., 47, W11511, doi:10.1029/2011WR010748
"""

from superflexpy.implementation.computation.pegasus_root_finding import PegasusPython
from superflexpy.implementation.computation.implicit_euler import ImplicitEulerPython
from superflexpy.implementation.elements.hbv import UnsaturatedReservoir, FastReservoir
from superflexpy.framework.unit import Unit

root_finder = PegasusPython()
numeric_approximator = ImplicitEulerPython(root_finder=root_finder)

ur = UnsaturatedReservoir(
    parameters={'Smax': 50.0, 'Ce': 1.0, 'm': 0.01, 'beta': 2.0},
    states={'S0': 25.0},
    approximation=numeric_approximator,
    id='UR'
)

fr = FastReservoir(
    parameters={'k': 0.1, 'alpha': 1.0},
    states={'S0': 10.0},
    approximation=numeric_approximator,
    id='FR'
)

model = Unit(
    layers=[
        [ur],
        [fr]
    ],
    id='M4'
)
