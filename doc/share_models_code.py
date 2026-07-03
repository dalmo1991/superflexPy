from superflexpy.framework.unit import Unit
from superflexpy.implementation.elements.hbv import PowerReservoir, UnsaturatedReservoir
from superflexpy.implementation.numerical_approximators.implicit_euler import (
    ImplicitEulerPython,
)
from superflexpy.implementation.root_finders.pegasus import PegasusPython

root_finder = PegasusPython()
numeric_approximator = ImplicitEulerPython(root_finder=root_finder)

ur = UnsaturatedReservoir(
    parameters={"Smax": 50.0, "Ce": 1.0, "m": 0.01, "beta": 2.0},
    states={"S0": 25.0},
    approximation=numeric_approximator,
    id="UR",
)

fr = PowerReservoir(
    parameters={"k": 0.1, "alpha": 1.0}, states={"S0": 10.0}, approximation=numeric_approximator, id="FR"
)

model = Unit(layers=[[ur], [fr]], id="M4")

from superflexpy.implementation.models.m4_sf_2011 import model

model.set_input([P, E])
model.set_timestep(1.0)
model.reset_states()

output = model.get_output()

from .my_new_model import model
