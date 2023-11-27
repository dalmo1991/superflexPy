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
"""

import sys
import unittest
from os.path import abspath, dirname, join

import numpy as np
import pandas as pd

# Package path is 2 levels above this file
package_path = join(abspath(dirname(__file__)), "..", "..")
sys.path.insert(0, package_path)

from superflexpy.framework.network import Network
from superflexpy.framework.node import Node
from superflexpy.framework.unit import Unit
from superflexpy.implementation.elements.hbv import PowerReservoir, UnsaturatedReservoir
from superflexpy.implementation.elements.structure_elements import Junction, Splitter
from superflexpy.implementation.numerical_approximators.implicit_euler import (
    ImplicitEulerNumba,
    ImplicitEulerPython,
)
from superflexpy.implementation.root_finders.pegasus import PegasusNumba, PegasusPython


class TestStructureElements(unittest.TestCase):
    """
    This class tests the functionality of Splitter and Junction.
    We compare the results with superflex in two scenarios:
    - start and stop to check that it saves the intermediate states
    - 2 rounds to check that it re-sets the states to the initial value
    """

    def _init_model(self, solver):
        if solver == "numba":
            solver = PegasusNumba()
            num_app = ImplicitEulerNumba(root_finder=solver)
        elif solver == "python":
            solver = PegasusPython()
            num_app = ImplicitEulerPython(root_finder=solver)

        # Define HRU 1 (40%)
        fr = PowerReservoir(parameters={"k": 0.01, "alpha": 2.5}, states={"S0": 0.0}, approximation=num_app, id="FR")

        h1 = Unit(layers=[[fr]], id="H1")

        # Define HRU 2 (60%)
        fr = PowerReservoir(parameters={"k": 0.01, "alpha": 2.5}, states={"S0": 0.0}, approximation=num_app, id="FR")

        sr = PowerReservoir(parameters={"k": 1e-4, "alpha": 1.0}, states={"S0": 0.0}, approximation=num_app, id="SR")

        ur = UnsaturatedReservoir(
            parameters={
                "Smax": 50.0,
                "Ce": 1.5,
                "m": 0.01,
                "beta": 1.5,
            },
            states={"S0": 0.2 * 50.0, "PET": None},
            approximation=num_app,
            id="UR",
        )

        s = Splitter(weight=[[0.3], [0.7]], direction=[[0], [0]], id="S")

        j = Junction(direction=[[0, 0]], id="J")

        h2 = Unit(layers=[[ur], [s], [fr, sr], [j]], id="H2")

        # Define the catchment
        cat1 = Node(units=[h1, h2], weights=[0.25, 0.75], area=10.0, id="Cat1")
        cat2 = Node(units=[h1, h2], weights=[0.4, 0.6], area=20.0, id="Cat2")
        cat3 = Node(units=[h1, h2], weights=[0.8, 0.2], area=30.0, id="Cat3")

        # Define the network
        net = Network(
            nodes=[cat1, cat2, cat3],
            topology={
                "Cat1": "Cat3",
                "Cat2": "Cat3",
                "Cat3": None,
            },
        )
        net.set_timestep(1.0)
        self._cat1 = cat1
        self._cat2 = cat2
        self._cat3 = cat3
        self._model = net

    def _read_inputs(self):
        data = pd.read_csv(
            "{}/test/reference_results/06_3Cats_2HRUs/input.dat".format(package_path),
            header=6,
            sep="\s+|,\s+|,",
            engine="python",
        )
        self._precipitation_c1 = data.iloc[:, 5].values
        self._precipitation_c2 = data.iloc[:, 6].values
        self._precipitation_c3 = data.iloc[:, 7].values
        self._pet_c1 = data.iloc[:, 8].values
        self._pet_c2 = data.iloc[:, 9].values
        self._pet_c3 = data.iloc[:, 10].values

    def _read_outputs(self):
        self._superflex_output = pd.read_csv(
            "{}/test/reference_results/06_3Cats_2HRUs/Results.csv".format(package_path)
        )

    def _test_start_stop(self, solver):
        self._init_model(solver=solver)
        self._read_outputs()
        self._read_inputs()

        # First half of time series
        self._cat1.set_input([self._precipitation_c1[:5], self._pet_c1[:5]])
        self._cat2.set_input([self._precipitation_c2[:5], self._pet_c2[:5]])
        self._cat3.set_input([self._precipitation_c3[:5], self._pet_c3[:5]])

        out = self._model.get_output()

        # Catchment_1
        cat_1_out_h1 = self._model.call_internal(id="Cat1_H1", method="get_output", solve=False)
        cat_1_s_fr_h1 = self._model.get_internal(id="Cat1_H1_FR", attribute="state_array")[:, 0]
        cat_1_out_h2 = self._model.call_internal(id="Cat1_H2", method="get_output", solve=False)
        cat_1_aet_h2 = self._model.call_internal(id="Cat1_H2_UR", method="get_AET")
        cat_1_s_ur_h2 = self._model.get_internal(id="Cat1_H2_UR", attribute="state_array")[:, 0]
        cat_1_s_fr_h2 = self._model.get_internal(id="Cat1_H2_FR", attribute="state_array")[:, 0]
        cat_1_s_sr_h2 = self._model.get_internal(id="Cat1_H2_SR", attribute="state_array")[:, 0]

        # Catchment_2
        cat_2_out_h1 = self._model.call_internal(id="Cat2_H1", method="get_output", solve=False)
        cat_2_s_fr_h1 = self._model.get_internal(id="Cat2_H1_FR", attribute="state_array")[:, 0]
        cat_2_out_h2 = self._model.call_internal(id="Cat2_H2", method="get_output", solve=False)
        cat_2_aet_h2 = self._model.call_internal(id="Cat2_H2_UR", method="get_AET")
        cat_2_s_ur_h2 = self._model.get_internal(id="Cat2_H2_UR", attribute="state_array")[:, 0]
        cat_2_s_fr_h2 = self._model.get_internal(id="Cat2_H2_FR", attribute="state_array")[:, 0]
        cat_2_s_sr_h2 = self._model.get_internal(id="Cat2_H2_SR", attribute="state_array")[:, 0]

        # Catchment_3
        cat_3_out_h1 = self._model.call_internal(id="Cat3_H1", method="get_output", solve=False)
        cat_3_s_fr_h1 = self._model.get_internal(id="Cat3_H1_FR", attribute="state_array")[:, 0]
        cat_3_out_h2 = self._model.call_internal(id="Cat3_H2", method="get_output", solve=False)
        cat_3_aet_h2 = self._model.call_internal(id="Cat3_H2_UR", method="get_AET")
        cat_3_s_ur_h2 = self._model.get_internal(id="Cat3_H2_UR", attribute="state_array")[:, 0]
        cat_3_s_fr_h2 = self._model.get_internal(id="Cat3_H2_FR", attribute="state_array")[:, 0]
        cat_3_s_sr_h2 = self._model.get_internal(id="Cat3_H2_SR", attribute="state_array")[:, 0]

        msg = "Fail in the second round"

        self.assertTrue(np.allclose(out["Cat1"], self._superflex_output.iloc[:5, 0]), msg=msg)
        self.assertTrue(np.allclose(out["Cat2"], self._superflex_output.iloc[:5, 1]), msg=msg)
        self.assertTrue(np.allclose(out["Cat3"], self._superflex_output.iloc[:5, 2]), msg=msg)
        self.assertTrue(np.allclose(cat_1_out_h1, self._superflex_output.iloc[:5, 3]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_fr_h1, self._superflex_output.iloc[:5, 4]), msg=msg)
        self.assertTrue(np.allclose(cat_2_out_h1, self._superflex_output.iloc[:5, 5]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_fr_h1, self._superflex_output.iloc[:5, 6]), msg=msg)
        self.assertTrue(np.allclose(cat_3_out_h1, self._superflex_output.iloc[:5, 7]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_fr_h1, self._superflex_output.iloc[:5, 8]), msg=msg)
        self.assertTrue(np.allclose(cat_1_out_h2, self._superflex_output.iloc[:5, 9]), msg=msg)
        self.assertTrue(np.allclose(cat_1_aet_h2, self._superflex_output.iloc[:5, 10]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_ur_h2, self._superflex_output.iloc[:5, 11]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_fr_h2, self._superflex_output.iloc[:5, 12]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_sr_h2, self._superflex_output.iloc[:5, 13]), msg=msg)
        self.assertTrue(np.allclose(cat_2_out_h2, self._superflex_output.iloc[:5, 14]), msg=msg)
        self.assertTrue(np.allclose(cat_2_aet_h2, self._superflex_output.iloc[:5, 15]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_ur_h2, self._superflex_output.iloc[:5, 16]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_fr_h2, self._superflex_output.iloc[:5, 17]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_sr_h2, self._superflex_output.iloc[:5, 18]), msg=msg)
        self.assertTrue(np.allclose(cat_3_out_h2, self._superflex_output.iloc[:5, 19]), msg=msg)
        self.assertTrue(np.allclose(cat_3_aet_h2, self._superflex_output.iloc[:5, 20]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_ur_h2, self._superflex_output.iloc[:5, 21]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_fr_h2, self._superflex_output.iloc[:5, 22]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_sr_h2, self._superflex_output.iloc[:5, 23]), msg=msg)

        # Second half of time series
        self._model.set_states({"Cat1_H2_UR_PET": self._pet_c1[5:]})
        self._model.set_states({"Cat2_H2_UR_PET": self._pet_c2[5:]})
        self._model.set_states({"Cat3_H2_UR_PET": self._pet_c3[5:]})
        self._cat1.set_input([self._precipitation_c1[5:], self._pet_c1[5:]])
        self._cat2.set_input([self._precipitation_c2[5:], self._pet_c2[5:]])
        self._cat3.set_input([self._precipitation_c3[5:], self._pet_c3[5:]])
        out = self._model.get_output()

        # Catchment_1
        cat_1_out_h1 = self._model.call_internal(id="Cat1_H1", method="get_output", solve=False)
        cat_1_s_fr_h1 = self._model.get_internal(id="Cat1_H1_FR", attribute="state_array")[:, 0]
        cat_1_out_h2 = self._model.call_internal(id="Cat1_H2", method="get_output", solve=False)
        cat_1_aet_h2 = self._model.call_internal(id="Cat1_H2_UR", method="get_AET")
        cat_1_s_ur_h2 = self._model.get_internal(id="Cat1_H2_UR", attribute="state_array")[:, 0]
        cat_1_s_fr_h2 = self._model.get_internal(id="Cat1_H2_FR", attribute="state_array")[:, 0]
        cat_1_s_sr_h2 = self._model.get_internal(id="Cat1_H2_SR", attribute="state_array")[:, 0]

        # Catchment_2
        cat_2_out_h1 = self._model.call_internal(id="Cat2_H1", method="get_output", solve=False)
        cat_2_s_fr_h1 = self._model.get_internal(id="Cat2_H1_FR", attribute="state_array")[:, 0]
        cat_2_out_h2 = self._model.call_internal(id="Cat2_H2", method="get_output", solve=False)
        cat_2_aet_h2 = self._model.call_internal(id="Cat2_H2_UR", method="get_AET")
        cat_2_s_ur_h2 = self._model.get_internal(id="Cat2_H2_UR", attribute="state_array")[:, 0]
        cat_2_s_fr_h2 = self._model.get_internal(id="Cat2_H2_FR", attribute="state_array")[:, 0]
        cat_2_s_sr_h2 = self._model.get_internal(id="Cat2_H2_SR", attribute="state_array")[:, 0]

        # Catchment_3
        cat_3_out_h1 = self._model.call_internal(id="Cat3_H1", method="get_output", solve=False)
        cat_3_s_fr_h1 = self._model.get_internal(id="Cat3_H1_FR", attribute="state_array")[:, 0]
        cat_3_out_h2 = self._model.call_internal(id="Cat3_H2", method="get_output", solve=False)
        cat_3_aet_h2 = self._model.call_internal(id="Cat3_H2_UR", method="get_AET")
        cat_3_s_ur_h2 = self._model.get_internal(id="Cat3_H2_UR", attribute="state_array")[:, 0]
        cat_3_s_fr_h2 = self._model.get_internal(id="Cat3_H2_FR", attribute="state_array")[:, 0]
        cat_3_s_sr_h2 = self._model.get_internal(id="Cat3_H2_SR", attribute="state_array")[:, 0]

        msg = "Fail in the second round"

        self.assertTrue(np.allclose(out["Cat1"], self._superflex_output.iloc[5:, 0]), msg=msg)
        self.assertTrue(np.allclose(out["Cat2"], self._superflex_output.iloc[5:, 1]), msg=msg)
        self.assertTrue(np.allclose(out["Cat3"], self._superflex_output.iloc[5:, 2]), msg=msg)
        self.assertTrue(np.allclose(cat_1_out_h1, self._superflex_output.iloc[5:, 3]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_fr_h1, self._superflex_output.iloc[5:, 4]), msg=msg)
        self.assertTrue(np.allclose(cat_2_out_h1, self._superflex_output.iloc[5:, 5]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_fr_h1, self._superflex_output.iloc[5:, 6]), msg=msg)
        self.assertTrue(np.allclose(cat_3_out_h1, self._superflex_output.iloc[5:, 7]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_fr_h1, self._superflex_output.iloc[5:, 8]), msg=msg)
        self.assertTrue(np.allclose(cat_1_out_h2, self._superflex_output.iloc[5:, 9]), msg=msg)
        self.assertTrue(np.allclose(cat_1_aet_h2, self._superflex_output.iloc[5:, 10]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_ur_h2, self._superflex_output.iloc[5:, 11]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_fr_h2, self._superflex_output.iloc[5:, 12]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_sr_h2, self._superflex_output.iloc[5:, 13]), msg=msg)
        self.assertTrue(np.allclose(cat_2_out_h2, self._superflex_output.iloc[5:, 14]), msg=msg)
        self.assertTrue(np.allclose(cat_2_aet_h2, self._superflex_output.iloc[5:, 15]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_ur_h2, self._superflex_output.iloc[5:, 16]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_fr_h2, self._superflex_output.iloc[5:, 17]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_sr_h2, self._superflex_output.iloc[5:, 18]), msg=msg)
        self.assertTrue(np.allclose(cat_3_out_h2, self._superflex_output.iloc[5:, 19]), msg=msg)
        self.assertTrue(np.allclose(cat_3_aet_h2, self._superflex_output.iloc[5:, 20]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_ur_h2, self._superflex_output.iloc[5:, 21]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_fr_h2, self._superflex_output.iloc[5:, 22]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_sr_h2, self._superflex_output.iloc[5:, 23]), msg=msg)

    def test_start_stop_python(self):
        self._test_start_stop(solver="python")

    def test_start_stop_numba(self):
        self._test_start_stop(solver="numba")

    def _test_2_rounds(self, solver):
        self._init_model(solver=solver)
        self._read_outputs()
        self._read_inputs()

        # First half of time series
        self._cat1.set_input([self._precipitation_c1[:], self._pet_c1[:]])
        self._cat2.set_input([self._precipitation_c2[:], self._pet_c2[:]])
        self._cat3.set_input([self._precipitation_c3[:], self._pet_c3[:]])
        out = self._model.get_output()

        # Catchment_1
        cat_1_out_h1 = self._model.call_internal(id="Cat1_H1", method="get_output", solve=False)
        cat_1_s_fr_h1 = self._model.get_internal(id="Cat1_H1_FR", attribute="state_array")[:, 0]
        cat_1_out_h2 = self._model.call_internal(id="Cat1_H2", method="get_output", solve=False)
        cat_1_aet_h2 = self._model.call_internal(id="Cat1_H2_UR", method="get_AET")
        cat_1_s_ur_h2 = self._model.get_internal(id="Cat1_H2_UR", attribute="state_array")[:, 0]
        cat_1_s_fr_h2 = self._model.get_internal(id="Cat1_H2_FR", attribute="state_array")[:, 0]
        cat_1_s_sr_h2 = self._model.get_internal(id="Cat1_H2_SR", attribute="state_array")[:, 0]

        # Catchment_2
        cat_2_out_h1 = self._model.call_internal(id="Cat2_H1", method="get_output", solve=False)
        cat_2_s_fr_h1 = self._model.get_internal(id="Cat2_H1_FR", attribute="state_array")[:, 0]
        cat_2_out_h2 = self._model.call_internal(id="Cat2_H2", method="get_output", solve=False)
        cat_2_aet_h2 = self._model.call_internal(id="Cat2_H2_UR", method="get_AET")
        cat_2_s_ur_h2 = self._model.get_internal(id="Cat2_H2_UR", attribute="state_array")[:, 0]
        cat_2_s_fr_h2 = self._model.get_internal(id="Cat2_H2_FR", attribute="state_array")[:, 0]
        cat_2_s_sr_h2 = self._model.get_internal(id="Cat2_H2_SR", attribute="state_array")[:, 0]

        # Catchment_3
        cat_3_out_h1 = self._model.call_internal(id="Cat3_H1", method="get_output", solve=False)
        cat_3_s_fr_h1 = self._model.get_internal(id="Cat3_H1_FR", attribute="state_array")[:, 0]
        cat_3_out_h2 = self._model.call_internal(id="Cat3_H2", method="get_output", solve=False)
        cat_3_aet_h2 = self._model.call_internal(id="Cat3_H2_UR", method="get_AET")
        cat_3_s_ur_h2 = self._model.get_internal(id="Cat3_H2_UR", attribute="state_array")[:, 0]
        cat_3_s_fr_h2 = self._model.get_internal(id="Cat3_H2_FR", attribute="state_array")[:, 0]
        cat_3_s_sr_h2 = self._model.get_internal(id="Cat3_H2_SR", attribute="state_array")[:, 0]

        msg = "Fail in the second round"

        self.assertTrue(np.allclose(out["Cat1"], self._superflex_output.iloc[:, 0]), msg=msg)
        self.assertTrue(np.allclose(out["Cat2"], self._superflex_output.iloc[:, 1]), msg=msg)
        self.assertTrue(np.allclose(out["Cat3"], self._superflex_output.iloc[:, 2]), msg=msg)
        self.assertTrue(np.allclose(cat_1_out_h1, self._superflex_output.iloc[:, 3]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_fr_h1, self._superflex_output.iloc[:, 4]), msg=msg)
        self.assertTrue(np.allclose(cat_2_out_h1, self._superflex_output.iloc[:, 5]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_fr_h1, self._superflex_output.iloc[:, 6]), msg=msg)
        self.assertTrue(np.allclose(cat_3_out_h1, self._superflex_output.iloc[:, 7]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_fr_h1, self._superflex_output.iloc[:, 8]), msg=msg)
        self.assertTrue(np.allclose(cat_1_out_h2, self._superflex_output.iloc[:, 9]), msg=msg)
        self.assertTrue(np.allclose(cat_1_aet_h2, self._superflex_output.iloc[:, 10]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_ur_h2, self._superflex_output.iloc[:, 11]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_fr_h2, self._superflex_output.iloc[:, 12]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_sr_h2, self._superflex_output.iloc[:, 13]), msg=msg)
        self.assertTrue(np.allclose(cat_2_out_h2, self._superflex_output.iloc[:, 14]), msg=msg)
        self.assertTrue(np.allclose(cat_2_aet_h2, self._superflex_output.iloc[:, 15]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_ur_h2, self._superflex_output.iloc[:, 16]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_fr_h2, self._superflex_output.iloc[:, 17]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_sr_h2, self._superflex_output.iloc[:, 18]), msg=msg)
        self.assertTrue(np.allclose(cat_3_out_h2, self._superflex_output.iloc[:, 19]), msg=msg)
        self.assertTrue(np.allclose(cat_3_aet_h2, self._superflex_output.iloc[:, 20]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_ur_h2, self._superflex_output.iloc[:, 21]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_fr_h2, self._superflex_output.iloc[:, 22]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_sr_h2, self._superflex_output.iloc[:, 23]), msg=msg)

        # Second half of time series
        self._model.reset_states()
        out = self._model.get_output()

        # Catchment_1
        cat_1_out_h1 = self._model.call_internal(id="Cat1_H1", method="get_output", solve=False)
        cat_1_s_fr_h1 = self._model.get_internal(id="Cat1_H1_FR", attribute="state_array")[:, 0]
        cat_1_out_h2 = self._model.call_internal(id="Cat1_H2", method="get_output", solve=False)
        cat_1_aet_h2 = self._model.call_internal(id="Cat1_H2_UR", method="get_AET")
        cat_1_s_ur_h2 = self._model.get_internal(id="Cat1_H2_UR", attribute="state_array")[:, 0]
        cat_1_s_fr_h2 = self._model.get_internal(id="Cat1_H2_FR", attribute="state_array")[:, 0]
        cat_1_s_sr_h2 = self._model.get_internal(id="Cat1_H2_SR", attribute="state_array")[:, 0]

        # Catchment_2
        cat_2_out_h1 = self._model.call_internal(id="Cat2_H1", method="get_output", solve=False)
        cat_2_s_fr_h1 = self._model.get_internal(id="Cat2_H1_FR", attribute="state_array")[:, 0]
        cat_2_out_h2 = self._model.call_internal(id="Cat2_H2", method="get_output", solve=False)
        cat_2_aet_h2 = self._model.call_internal(id="Cat2_H2_UR", method="get_AET")
        cat_2_s_ur_h2 = self._model.get_internal(id="Cat2_H2_UR", attribute="state_array")[:, 0]
        cat_2_s_fr_h2 = self._model.get_internal(id="Cat2_H2_FR", attribute="state_array")[:, 0]
        cat_2_s_sr_h2 = self._model.get_internal(id="Cat2_H2_SR", attribute="state_array")[:, 0]

        # Catchment_3
        cat_3_out_h1 = self._model.call_internal(id="Cat3_H1", method="get_output", solve=False)
        cat_3_s_fr_h1 = self._model.get_internal(id="Cat3_H1_FR", attribute="state_array")[:, 0]
        cat_3_out_h2 = self._model.call_internal(id="Cat3_H2", method="get_output", solve=False)
        cat_3_aet_h2 = self._model.call_internal(id="Cat3_H2_UR", method="get_AET")
        cat_3_s_ur_h2 = self._model.get_internal(id="Cat3_H2_UR", attribute="state_array")[:, 0]
        cat_3_s_fr_h2 = self._model.get_internal(id="Cat3_H2_FR", attribute="state_array")[:, 0]
        cat_3_s_sr_h2 = self._model.get_internal(id="Cat3_H2_SR", attribute="state_array")[:, 0]

        msg = "Fail in the second round"

        self.assertTrue(np.allclose(out["Cat1"], self._superflex_output.iloc[:, 0]), msg=msg)
        self.assertTrue(np.allclose(out["Cat2"], self._superflex_output.iloc[:, 1]), msg=msg)
        self.assertTrue(np.allclose(out["Cat3"], self._superflex_output.iloc[:, 2]), msg=msg)
        self.assertTrue(np.allclose(cat_1_out_h1, self._superflex_output.iloc[:, 3]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_fr_h1, self._superflex_output.iloc[:, 4]), msg=msg)
        self.assertTrue(np.allclose(cat_2_out_h1, self._superflex_output.iloc[:, 5]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_fr_h1, self._superflex_output.iloc[:, 6]), msg=msg)
        self.assertTrue(np.allclose(cat_3_out_h1, self._superflex_output.iloc[:, 7]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_fr_h1, self._superflex_output.iloc[:, 8]), msg=msg)
        self.assertTrue(np.allclose(cat_1_out_h2, self._superflex_output.iloc[:, 9]), msg=msg)
        self.assertTrue(np.allclose(cat_1_aet_h2, self._superflex_output.iloc[:, 10]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_ur_h2, self._superflex_output.iloc[:, 11]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_fr_h2, self._superflex_output.iloc[:, 12]), msg=msg)
        self.assertTrue(np.allclose(cat_1_s_sr_h2, self._superflex_output.iloc[:, 13]), msg=msg)
        self.assertTrue(np.allclose(cat_2_out_h2, self._superflex_output.iloc[:, 14]), msg=msg)
        self.assertTrue(np.allclose(cat_2_aet_h2, self._superflex_output.iloc[:, 15]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_ur_h2, self._superflex_output.iloc[:, 16]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_fr_h2, self._superflex_output.iloc[:, 17]), msg=msg)
        self.assertTrue(np.allclose(cat_2_s_sr_h2, self._superflex_output.iloc[:, 18]), msg=msg)
        self.assertTrue(np.allclose(cat_3_out_h2, self._superflex_output.iloc[:, 19]), msg=msg)
        self.assertTrue(np.allclose(cat_3_aet_h2, self._superflex_output.iloc[:, 20]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_ur_h2, self._superflex_output.iloc[:, 21]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_fr_h2, self._superflex_output.iloc[:, 22]), msg=msg)
        self.assertTrue(np.allclose(cat_3_s_sr_h2, self._superflex_output.iloc[:, 23]), msg=msg)

    def test_2_rounds_python(self):
        self._test_2_rounds(solver="python")

    def test_2_rounds_numba(self):
        self._test_2_rounds(solver="numba")


if __name__ == "__main__":
    unittest.main()
    # test = TestStructureElements()
    # test._read_inputs()
    # test.test_start_stop_python()
