"""
Copyright 2019 Marco Dal Molin et al.

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

This file contains the implementation of some elements needed to replicate the
model used in Dal Molin et al, 2020

Bibliography
------------


Dal Molin, M., Schirmer, M., Zappa, M., and Fenicia, F.: Understanding dominant
controls on streamflow spatial variability to set up a semi-distributed
hydrological model: the case study of the Thur catchment, Hydrol. Earth Syst.
Sci., 24, 1319–1345, https://doi.org/10.5194/hess-24-1319-2020, 2020.
"""


from ...framework.element import LagElement, ODEsElement
from .hbv import FastReservoir, UnsaturatedReservoir
import numba as nb
import numpy as np


class SnowReservoir(ODEsElement):

    def __init__(self, parameters, states, solver, id):
        """
        This is the initializer of the class SnowReservoir.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            - 't0' : threshold temperature separating snow from rain
            - 'k' : release rate for the melting potential
            - 'm' : smoothing factor
        states : dict
            Initial state of the element. The keys must be:
            - 'S0' : initial storage of the reservoir.
        solver : superflexpy.utils.root_finder.RootFinder
            Solver used to find the root(s) of the differential equation(s).
            Child classes may implement their own solver, therefore the tipe
            of the solver is not enforced.
        id : str
            Itentifier of the element. All the elements of the framework must
            have an id.
        """

        ODEsElement.__init__(self,
                             parameters=parameters,
                             states=states,
                             solver=solver,
                             id=id)

        if solver.architecture == 'numba':
            self._differential_equation = self._differential_equation_numba
        elif solver.architecture == 'python':
            self._differential_equation = self._differential_equation_python

    def set_input(self, input):
        """
        Set the input of the element.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List containing the input fluxes of the element. It contains 2
            flux:
            1. Precipitation
            2. Temperature
        """

        self.input = {'P': input[0],
                      'T': input[1]}

    def get_output(self, solve=True):
        """
        This method solves the differential equation governing the routing
        store.

        Returns
        -------
        list(numpy.ndarray)
            Output fluxes in the following order:
            1. Streamflow (P + melt)
        """

        # Separate rain from snow
        t0 = self._parameters[self._prefix_parameters + 't0']

        rain = np.where(self.input['T'] > t0,  # Condition
                        self.input['P'],       # True
                        0.0)                   # False

        snow = self.input['P'] - rain

        if solve:
            self._solver_states = [self._states[self._prefix_states + 'S0']]
            self._solve_differential_equation(snow=snow)

            # Update the state
            self.set_states({self._prefix_states + 'S0': self.state_array[-1, 0]})

        k = self._parameters[self._prefix_parameters + 'k']
        m = self._parameters[self._prefix_parameters + 'm']

        melt_potential = np.where(self.input['T'] > t0,
                                  k * self.input['T'],
                                  0.0)

        actual_melt = melt_potential * (1 - np.exp(-(self.state_array[:, 0] / m)))

        return [rain + actual_melt]

    @staticmethod
    def _differential_equation_python(S, S0, snow, T, t0, k, m, dt):

        if S is None:
            S = 0

        melt_potential = k * T if T > t0 else 0.0
        actual_melt = melt_potential * (1 - np.exp(-(S / m)))

        return(
            (S - S0) / dt - snow + actual_melt,
            0.0,
            S0 + snow,
        )

    @staticmethod
    @nb.jit('UniTuple(f8, 3)(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])',
            nopython=True)
    def _differential_equation_numba(S, S0, ind, snow, T, t0, k, m, dt):

        if S is None:
            S = 0

        snow = snow[ind]
        T = T[ind]
        t0 = t0[ind]
        k = k[ind]
        m = m[ind]
        dt = dt[ind]

        melt_potential = k * T if T > t0 else 0.0
        actual_melt = melt_potential * (1 - np.exp(-(S / m)))

        return(
            (S - S0) / dt - snow + actual_melt,
            0.0,
            S0 + snow,
        )


class HalfTriangularLag(LagElement):

    def __init__(self, parameters, states, id):
        """
        This is the initializer of the half triangular lag function.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            - lag_time : total length (base) of the lag function.
        states : dict
            Initial state of the element. The keys must be:
            - lag : initial state of the lag function
        id : str
            Itentifier of the element. All the elements of the framework must
            have an id.
        """

        LagElement.__init__(self, parameters, states, id)

    def _build_weight(self, lag_time):

        weight = []

        for t in lag_time:
            array_length = np.ceil(t)
            w_i = []
            for i in range(int(array_length)):
                w_i.append(self._calculate_lag_area(i + 1, t)
                           - self._calculate_lag_area(i, t))
            weight.append(np.array(w_i))

        return weight

    @staticmethod
    def _calculate_lag_area(bin, len):
        if bin <= 0:
            value = 0
        elif bin < len:
            value = (bin / len)**2
        else:
            value = 1

        return value
