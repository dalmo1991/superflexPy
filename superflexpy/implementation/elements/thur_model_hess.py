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
from .hbv import PowerReservoir, UnsaturatedReservoir
import numba as nb
import numpy as np


class SnowReservoir(ODEsElement):

    def __init__(self, parameters, states, approximation, id):
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
                             approximation=approximation,
                             id=id)

        self._fluxes_python = [self._flux_function_python]
        if approximation.architecture == 'numba':
            self._fluxes = [self._flux_function_numba]
        elif approximation.architecture == 'python':
            self._fluxes = [self._flux_function_numba]

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

        fluxes = self._num_app.get_fluxes(fluxes=self._fluxes_python,
                                          S=self.state_array,
                                          S0=self._solver_states,
                                          snow=snow,
                                          dt=self._dt,
                                          **self.input,
                                          **{k[len(self._prefix_parameters):]: self._parameters[k] for k in self._parameters},
                                          )

        actual_melt = - fluxes[0][1]

        return [rain + actual_melt]

    @staticmethod
    def _flux_function_python(S, S0, ind, snow, T, t0, k, m, dt):

        if S is None:
            S = 0

        if ind is None:
            melt_potential = np.where(T > t0, k * T, 0.0)
            actual_melt = melt_potential * (1 - np.exp(-(S / m)))

            return(
                [
                    snow,
                    - actual_melt,
                ],
                0.0,
                S0 + snow * dt,
            )

        else:
            melt_potential = k[ind] * T[ind] if T[ind] > t0[ind] else 0.0
            actual_melt = melt_potential * (1 - np.exp(-(S / m[ind])))

            return(
                [
                    snow[ind],
                    - actual_melt,
                ],
                0.0,
                S0 + snow[ind] * dt[ind],
            )

    @staticmethod
    @nb.jit('Tuple((UniTuple(f8, 2), f8, f8))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])',
            nopython=True)
    def _flux_function_numba(S, S0, ind, snow, T, t0, k, m, dt):

        if S is None:
            S = 0

        melt_potential = k[ind] * T[ind] if T[ind] > t0[ind] else 0.0
        actual_melt = melt_potential * (1 - np.exp(-(S / m[ind])))

        return(
            (
                snow[ind],
                - actual_melt,
            ),
            0.0,
            S0 + snow[ind] * dt[ind],
        )


class HalfTriangularLag(LagElement):

    def __init__(self, parameters, states, id):
        """
        This is the initializer of the half triangular lag function.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            - lag-time : total length (base) of the lag function.
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
