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

This file implements the model M2 presented in Dal Molin et al., 2020

Reference
---------

Dal Molin, M., Schirmer, M., Zappa, M., and Fenicia, F.: Understanding dominant
controls on streamflow spatial variability to set up a semi-distributed
hydrological model: the case study of the Thur catchment, Hydrol. Earth Syst.
Sci., 24, 1319–1345, https://doi.org/10.5194/hess-24-1319-2020, 2020.
"""

from superflexpy.implementation.computation.pegasus_root_finding import PegasusPython
from superflexpy.implementation.computation.implicit_euler import ImplicitEulerPython
from superflexpy.implementation.elements.thur_model_hess import SnowReservoir, UnsaturatedReservoir, PowerReservoir, HalfTriangularLag
from superflexpy.implementation.elements.structure_elements import Transparent, Junction, Splitter
from superflexpy.framework.unit import Unit
from superflexpy.framework.node import Node
from superflexpy.framework.network import Network

solver = PegasusPython()
approximator = ImplicitEulerPython(root_finder=solver)

# Fluxes in the order P, T, PET
upper_splitter = Splitter(
    direction=[
        [0, 1, None],    # P and T go to the snow reservoir
        [2, None, None]  # PET goes to the transparent element
    ],
    weight=[
        [1.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ],
    id='upper-splitter'
)

snow = SnowReservoir(
    parameters={'t0': 0.0, 'k': 0.01, 'm': 2.0},
    states={'S0': 0.0},
    approximation=approximator,
    id='snow'
)

upper_transparent = Transparent(
    id='upper-transparent'
)

upper_junction = Junction(
    direction=[
        [0, None],
        [None, 0]
    ],
    id='upper-junction'
)

unsaturated = UnsaturatedReservoir(
    parameters={'Smax': 50.0, 'Ce': 1.0, 'm': 0.01, 'beta': 2.0},
    states={'S0': 10.0},
    approximation=approximator,
    id='unsaturated'
)

lower_splitter = Splitter(
    direction=[
        [0],
        [0]
    ],
    weight=[
        [0.3],   # Portion to slow reservoir
        [0.7]    # Portion to fast reservoir
    ],
    id='lower-splitter'
)

lag_fun = HalfTriangularLag(
    parameters={'lag-time': 2.0},
    states={'lag': None},
    id='lag-fun'
)

fast = PowerReservoir(
    parameters={'k': 0.01, 'alpha': 3.0},
    states={'S0': 0.0},
    approximation=approximator,
    id='fast'
)

slow = PowerReservoir(
    parameters={'k': 1e-4, 'alpha': 1.0},
    states={'S0': 0.0},
    approximation=approximator,
    id='slow'
)

lower_transparent = Transparent(
    id='lower-transparent'
)

lower_junction = Junction(
    direction=[
        [0, 0]
    ],
    id='lower-junction'
)

consolidated = Unit(
    layers=[
        [upper_splitter],
        [snow, upper_transparent],
        [upper_junction],
        [unsaturated],
        [lower_splitter],
        [slow, lag_fun],
        [lower_transparent, fast],
        [lower_junction],
    ],
    id='consolidated'
)

unconsolidated = Unit(
    layers=[
        [upper_splitter],
        [snow, upper_transparent],
        [upper_junction],
        [unsaturated],
        [lower_splitter],
        [slow, lag_fun],
        [lower_transparent, fast],
        [lower_junction],
    ],
    id='unconsolidated'
)

andelfingen = Node(
    units=[consolidated, unconsolidated],
    weights=[0.24, 0.76],
    area=403.3,
    id='andelfingen'
)

appenzell = Node(
    units=[consolidated, unconsolidated],
    weights=[0.92, 0.08],
    area=74.4,
    id='appenzell'
)

frauenfeld = Node(
    units=[consolidated, unconsolidated],
    weights=[0.49, 0.51],
    area=134.4,
    id='frauenfeld'
)

halden = Node(
    units=[consolidated, unconsolidated],
    weights=[0.34, 0.66],
    area=314.3,
    id='halden'
)

herisau = Node(
    units=[consolidated, unconsolidated],
    weights=[0.88, 0.12],
    area=16.7,
    id='herisau'
)

jonschwil = Node(
    units=[consolidated, unconsolidated],
    weights=[0.9, 0.1],
    area=401.6,
    id='jonschwil'
)

mogelsberg = Node(
    units=[consolidated, unconsolidated],
    weights=[0.92, 0.08],
    area=88.1,
    id='mogelsberg'
)

mosnang = Node(
    units=[consolidated],
    weights=[1.0],
    area=3.1,
    id='mosnang'
)

stgallen = Node(
    units=[consolidated, unconsolidated],
    weights=[0.87, 0.13],
    area=186.6,
    id='stgallen'
)

waengi = Node(
    units=[consolidated, unconsolidated],
    weights=[0.63, 0.37],
    area=78.9,
    id='waengi'
)

model = Network(
    nodes=[
        andelfingen,
        appenzell,
        frauenfeld,
        halden,
        herisau,
        jonschwil,
        mogelsberg,
        mosnang,
        stgallen,
        waengi,
    ],
    topology={
        'andelfingen': None,
        'appenzell': 'stgallen',
        'frauenfeld': 'andelfingen',
        'halden': 'andelfingen',
        'herisau': 'halden',
        'jonschwil': 'halden',
        'mogelsberg': 'jonschwil',
        'mosnang': 'jonschwil',
        'stgallen': 'halden',
        'waengi': 'frauenfeld',
    }
)
