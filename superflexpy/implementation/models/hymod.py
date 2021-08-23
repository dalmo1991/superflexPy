"""
Copyright 2020 Marco Dal Molin et al.

This file is part of SuperflexPy.

SuperflexPy is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SuperflexPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with SuperflexPy. If not, see <https://www.gnu.org/licenses/>.

This file is part of the SuperflexPy modelling framework. For details about it,
visit the page https://superflexpy.readthedocs.io

CODED BY: Marco Dal Molin
DESIGNED BY: Marco Dal Molin, Fabrizio Fenicia, Dmitri Kavetski

This file implements a version of the model Hymod
"""

from superflexpy.implementation.root_finders.pegasus import PegasusPython
from superflexpy.implementation.numerical_approximators.implicit_euler import ImplicitEulerPython
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
