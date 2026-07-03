import pathlib
import sys

REPO_FOLDER = pathlib.Path(__file__).absolute().parents[2]
sys.path.insert(0, str(REPO_FOLDER))
from superflexpy.framework.network import Network
from superflexpy.framework.node import Node
from superflexpy.framework.unit import Unit
from superflexpy.implementation.elements.structure_elements import (
    Junction,
    Splitter,
    Transparent,
)
from superflexpy.implementation.elements.thur_model_hess import (
    HalfTriangularLag,
    PowerReservoir,
    SnowReservoir,
    UnsaturatedReservoir,
)
from superflexpy.implementation.numerical_approximators.implicit_euler import (
    ImplicitEulerPython,
)
from superflexpy.implementation.root_finders.pegasus import PegasusPython

solver = PegasusPython()
approximator = ImplicitEulerPython(root_finder=solver)

# Fluxes in the order P, T, PET
upper_splitter = Splitter(
    direction=[
        [0, 1, None],  # P and T go to the snow reservoir
        [2, None, None],  # PET goes to the transparent element
    ],
    weight=[[1.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
    id="upper-splitter",
)

snow = SnowReservoir(
    parameters={"t0": 0.0, "k": 0.01, "m": 2.0}, states={"S0": 0.0}, approximation=approximator, id="snow"
)

upper_transparent = Transparent(id="upper-transparent")

upper_junction = Junction(direction=[[0, None], [None, 0]], id="upper-junction")

unsaturated = UnsaturatedReservoir(
    parameters={"Smax": 50.0, "Ce": 1.0, "m": 0.01, "beta": 2.0},
    states={"S0": 10.0},
    approximation=approximator,
    id="unsaturated",
)

lower_splitter = Splitter(
    direction=[[0], [0]],
    weight=[[0.3], [0.7]],  # Portion to slow reservoir  # Portion to fast reservoir
    id="lower-splitter",
)

lag_fun = HalfTriangularLag(parameters={"lag-time": 2.0}, states={"lag": None}, id="lag-fun")

fast = PowerReservoir(parameters={"k": 0.01, "alpha": 3.0}, states={"S0": 0.0}, approximation=approximator, id="fast")

slow = PowerReservoir(parameters={"k": 1e-4, "alpha": 1.0}, states={"S0": 0.0}, approximation=approximator, id="slow")

lower_transparent = Transparent(id="lower-transparent")

lower_junction = Junction(direction=[[0, 0]], id="lower-junction")

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
    id="consolidated",
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
    id="unconsolidated",
)

andelfingen = Node(units=[consolidated, unconsolidated], weights=[0.24, 0.76], area=403.3, id="andelfingen")

appenzell = Node(units=[consolidated, unconsolidated], weights=[0.92, 0.08], area=74.4, id="appenzell")

frauenfeld = Node(units=[consolidated, unconsolidated], weights=[0.49, 0.51], area=134.4, id="frauenfeld")

halden = Node(units=[consolidated, unconsolidated], weights=[0.34, 0.66], area=314.3, id="halden")

herisau = Node(units=[consolidated, unconsolidated], weights=[0.88, 0.12], area=16.7, id="herisau")

jonschwil = Node(units=[consolidated, unconsolidated], weights=[0.9, 0.1], area=401.6, id="jonschwil")

mogelsberg = Node(units=[consolidated, unconsolidated], weights=[0.92, 0.08], area=88.1, id="mogelsberg")

mosnang = Node(units=[consolidated], weights=[1.0], area=3.1, id="mosnang")

stgallen = Node(units=[consolidated, unconsolidated], weights=[0.87, 0.13], area=186.6, id="stgallen")

waengi = Node(units=[consolidated, unconsolidated], weights=[0.63, 0.37], area=78.9, id="waengi")

thur_catchment = Network(
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
        "andelfingen": None,
        "appenzell": "stgallen",
        "frauenfeld": "andelfingen",
        "halden": "andelfingen",
        "herisau": "halden",
        "jonschwil": "halden",
        "mogelsberg": "jonschwil",
        "mosnang": "jonschwil",
        "stgallen": "halden",
        "waengi": "frauenfeld",
    },
)

thur_catchment.set_timestep(1.0)

catchments = [
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
]

catchments_names = [
    "andelfingen",
    "appenzell",
    "frauenfeld",
    "halden",
    "herisau",
    "jonschwil",
    "mogelsberg",
    "mosnang",
    "stgallen",
    "waengi",
]

df = {}

for cat, cat_name in zip(catchments, catchments_names):
    cat.set_input(
        [
            df["P_{}".format(cat_name)].values,
            df["T_{}".format(cat_name)].values,
            df["PET_{}".format(cat_name)].values,
        ]
    )

thur_catchment.set_timestep(1.0)

output = thur_catchment.get_output()
