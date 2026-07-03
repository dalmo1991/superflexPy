import numpy as np
import spotpy

from superflexpy.framework.unit import Unit
from superflexpy.implementation.elements.hbv import PowerReservoir
from superflexpy.implementation.numerical_approximators.implicit_euler import (
    ImplicitEulerPython,
)
from superflexpy.implementation.root_finders.pegasus import PegasusPython

root_finder = PegasusPython()
num_app = ImplicitEulerPython(root_finder=root_finder)

reservoir_1 = PowerReservoir(parameters={"k": 0.1, "alpha": 2.0}, states={"S0": 10.0}, approximation=num_app, id="FR1")
reservoir_2 = PowerReservoir(parameters={"k": 0.5, "alpha": 1.0}, states={"S0": 10.0}, approximation=num_app, id="FR2")

hyd_mod = Unit(layers=[[reservoir_1], [reservoir_2]], id="model")


class spotpy_model(object):
    def __init__(self, model, inputs, dt, observations, parameters, parameter_names, output_index):
        self._model = model
        self._model.set_input(inputs)
        self._model.set_timestep(dt)

        self._parameters = parameters
        self._parameter_names = parameter_names
        self._observarions = observations
        self._output_index = output_index

    def parameters(self):
        return spotpy.parameter.generate(self._parameters)

    def simulation(self, parameters):
        named_parameters = {}
        for p_name, p in zip(self._parameter_names, parameters):
            named_parameters[p_name] = p

        self._model.set_parameters(named_parameters)
        self._model.reset_states()
        output = self._model.get_output()

        return output[self._output_index]

    def evaluation(self):
        return self._observarions

    def objectivefunction(self, simulation, evaluation):
        obj_fun = spotpy.objectivefunctions.nashsutcliffe(evaluation=evaluation, simulation=simulation)

        return obj_fun


P = np.array([0.1, 0.0, 1.5])
Q_obs = np.array([5.0, 3.2, 4.5])


spotpy_hyd_mod = spotpy_model(
    model=hyd_mod,
    inputs=[P],
    dt=1.0,
    observations=Q_obs,
    parameters=[
        spotpy.parameter.Uniform("model_FR1_k", 1e-4, 1e-1),
        spotpy.parameter.Uniform("model_FR2_k", 1e-3, 1.0),
    ],
    parameter_names=["model_FR1_k", "model_FR2_k"],
    output_index=0,
)


sampler = spotpy.algorithms.sceua(spotpy_hyd_mod, dbname="calibration", dbformat="csv")
sampler.sample(repetitions=5000)
