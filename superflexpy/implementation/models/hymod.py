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

This file implements a version of the model Hymod
"""

from superflexpy.implementation.computation.pegasus_root_finding import PegasusPython
from superflexpy.implementation.computation.implicit_euler import ImplicitEulerPython
from superflexpy.implementation.elements.hymod import UpperZone, LinearReservoir
from superflexpy.implementation.elements.structure_elements import Junction, Splitter, Transparent
from superflexpy.framework.unit import Unit

root_finder = PegasusPython()  # Use the default parameters
numerical_approximation = ImplicitEulerPython(root_finder)

upper_zone = UpperZone(parameters={'Smax': 50.0, 'm': 0.01, 'beta': 2.0},
                       states={'S0': 10.0},
                       approximation=numerical_approximation,
                       id='uz')

splitter = Splitter(weight=[[0.6], [0.4]],
                    direction=[[0], [0]],
                    id='spl')

channel_routing_1 = LinearReservoir(parameters={'k': 0.1},
                                    states={'S0': 10.0},
                                    approximation=numerical_approximation,
                                    id='cr1')

channel_routing_2 = LinearReservoir(parameters={'k': 0.1},
                                    states={'S0': 10.0},
                                    approximation=numerical_approximation,
                                    id='cr2')

channel_routing_3 = LinearReservoir(parameters={'k': 0.1},
                                    states={'S0': 10.0},
                                    approximation=numerical_approximation,
                                    id='cr3')

lower_zone = LinearReservoir(parameters={'k': 0.1},
                             states={'S0': 10.0},
                             approximation=numerical_approximation,
                             id='lz')

transparent_1 = Transparent(id='tr1')

transparent_2 = Transparent(id='tr2')

junction = Junction(direction=[[0, 0]],  # First output
                    id='jun')

model = Unit(layers=[[upper_zone],
                     [splitter],
                     [channel_routing_1, lower_zone],
                     [channel_routing_2, transparent_1],
                     [channel_routing_3, transparent_2],
                     [junction]],
             id='model')
