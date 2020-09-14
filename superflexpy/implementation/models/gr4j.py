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

This file implements a version of the model GR4J
"""

from superflexpy.implementation.computation.pegasus_root_finding import PegasusPython
from superflexpy.implementation.computation.implicit_euler import ImplicitEulerPython
from superflexpy.implementation.elements.gr4j import InterceptionFilter, ProductionStore, UnitHydrograph1, UnitHydrograph2, RoutingStore, FluxAggregator
from superflexpy.implementation.elements.structure_elements import Transparent, Splitter, Junction
from superflexpy.framework.unit import Unit

x1, x2, x3, x4 = (50.0, 0.1, 20.0, 3.5)

root_finder = PegasusPython()  # Use the default parameters
numerical_approximation = ImplicitEulerPython(root_finder)

interception_filter = InterceptionFilter(id='ir')

production_store = ProductionStore(parameters={'x1': x1, 'alpha': 2.0,
                                               'beta': 5.0, 'ni': 4/9},
                                   states={'S0': 10.0},
                                   approximation=numerical_approximation,
                                   id='ps')

splitter = Splitter(weight=[[0.9], [0.1]],
                    direction=[[0], [0]],
                    id='spl')

unit_hydrograph_1 = UnitHydrograph1(parameters={'lag-time': x4},
                                    states={'lag': None},
                                    id='uh1')

unit_hydrograph_2 = UnitHydrograph2(parameters={'lag-time': 2*x4},
                                    states={'lag': None},
                                    id='uh2')

routing_store = RoutingStore(parameters={'x2': x2, 'x3': x3,
                                         'gamma': 5.0, 'omega': 3.5},
                             states={'S0': 10.0},
                             approximation=numerical_approximation,
                             id='rs')

transparent = Transparent(id='tr')

junction = Junction(direction=[[0, None],   # First output
                               [1, None],   # Second output
                               [None, 0]],  # Third output
                    id='jun')

flux_aggregator = FluxAggregator(id='fa')

model = Unit(layers=[[interception_filter],
                     [production_store],
                     [splitter],
                     [unit_hydrograph_1, unit_hydrograph_2],
                     [routing_store, transparent],
                     [junction],
                     [flux_aggregator]],
             id='model')
