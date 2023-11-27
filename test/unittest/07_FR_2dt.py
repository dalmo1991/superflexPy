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

from superflexpy.implementation.elements.hbv import PowerReservoir
from superflexpy.implementation.numerical_approximators.implicit_euler import (
    ImplicitEulerNumba,
    ImplicitEulerPython,
)
from superflexpy.implementation.root_finders.pegasus import PegasusNumba, PegasusPython


class TestFR(unittest.TestCase):
    """
    This class tests the functionality of the reservoir FR alone.
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

        fr = PowerReservoir(parameters={"k": 0.01, "alpha": 2.5}, states={"S0": 0.0}, approximation=num_app, id="FR")

        fr.set_timestep(2.0)
        self._model = fr

    def _read_inputs(self):
        data = pd.read_csv(
            "{}/test/reference_results/07_FR_2dt/input.dat".format(package_path),
            header=6,
            sep="\s+|,\s+|,",
            engine="python",
        )
        self._precipitation = data.iloc[:, 6].values
        self._pet = data.iloc[:, 7].values

    def _read_outputs(self):
        self._superflex_output = pd.read_csv("{}/test/reference_results/07_FR_2dt/Results.csv".format(package_path))

    def _test_fr_start_stop(self, solver):
        self._init_model(solver=solver)
        self._read_outputs()
        self._read_inputs()

        # First half of time series
        self._model.set_input([self._precipitation[:5]])
        out = self._model.get_output()

        msg = "Fail in the first half"

        self.assertTrue(np.allclose(out, self._superflex_output.iloc[:5, 0]), msg=msg)
        self.assertTrue(np.allclose(self._model.state_array[:, 0], self._superflex_output.iloc[:5, 1]), msg=msg)

        # Second half of time series
        self._model.set_input([self._precipitation[5:]])
        out = self._model.get_output()

        msg = "Fail in the second half"

        self.assertTrue(np.allclose(out, self._superflex_output.iloc[5:, 0]), msg=msg)
        self.assertTrue(np.allclose(self._model.state_array[:, 0], self._superflex_output.iloc[5:, 1]), msg=msg)

    def test_fr_start_stop_python(self):
        self._test_fr_start_stop(solver="python")

    def test_fr_start_stop_numba(self):
        self._test_fr_start_stop(solver="numba")

    def _test_2_rounds(self, solver):
        self._init_model(solver=solver)
        self._read_outputs()
        self._read_inputs()

        # First half of time series
        self._model.set_input([self._precipitation])
        out = self._model.get_output()

        msg = "Fail in the first round"

        self.assertTrue(np.allclose(out, self._superflex_output.iloc[:, 0]), msg=msg)
        self.assertTrue(np.allclose(self._model.state_array[:, 0], self._superflex_output.iloc[:, 1]), msg=msg)

        # Second half of time series
        self._model.reset_states()
        out = self._model.get_output()

        msg = "Fail in the second round"

        self.assertTrue(np.allclose(out, self._superflex_output.iloc[:, 0]), msg=msg)
        self.assertTrue(np.allclose(self._model.state_array[:, 0], self._superflex_output.iloc[:, 1]), msg=msg)

    def test_2_rounds_python(self):
        self._test_2_rounds(solver="python")

    def test_2_rounds_numba(self):
        self._test_2_rounds(solver="numba")


# if __name__ == "__main__":
unittest.main()
# test = TestFR()
# test.test_2_rounds_python()
