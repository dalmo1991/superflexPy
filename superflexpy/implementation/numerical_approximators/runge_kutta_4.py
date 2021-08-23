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

This file contains the implementation a class that solved the ODEs using the
implicit Runge Kutta of 4th order numerical approximation.
"""

import numpy as np
import numba as nb
from ...utils.numerical_approximator import NumericalApproximator


class RungeKutta4Python(NumericalApproximator):

    def __init__(self, root_finder):
        """
        This class creates an approximation of an ODE using Runge Kutta of 4th
        order and solves it (finds the value of the state that sets to zero the
        approximation) for all the time steps. The class is designed to operate
        with multiple independent ODEs. For dependent ODEs (i.e. ODE1 depends
        on the state of ODE2 and vice versa) custom solutions must be created.

        Note that this approximator operates under the assumption of constant
        fluxes (see documentation).

        Parameters
        ----------
        root_finder : superflexpy.utils.RootFinder
            Solver used to find the root of the differential equation.
        """

        super().__init__(root_finder=root_finder)

        self.architecture = 'python'
        self._error_message = 'module : superflexPy, solver : Runge Kutta 4'
        self._error_message += ' Error message : '

        if root_finder.architecture != 'python':
            message = '{}: architecture of the root_finder must be python. Given {}'.format(self._error_message, root_finder.architecture)
            raise ValueError(message)


    @staticmethod
    def _get_fluxes(fluxes, S, S0, args, dt):

        # Calculate the state used to calculate the fluxes
        S = S[:-1]
        S = np.insert(S, 0, S0)  # In the following, S is actually S0

        k1_fluxes = fluxes(S, S0, None, *args)[0]
        k2_state = S + (np.sum(k1_fluxes, axis=0) * dt) / 2
        k2_fluxes = fluxes(k2_state, S0, None, *args)[0]
        k3_state = S + (np.sum(k2_fluxes, axis=0) * dt) / 2
        k3_fluxes = fluxes(k3_state, S0, None, *args)[0]
        k4_state = S + (np.sum(k3_fluxes, axis=0) * dt)
        k4_fluxes = fluxes(k4_state, S0, None, *args)[0]

        fluxes = np.array(k1_fluxes) / 6 + np.array(k2_fluxes) / 3 + np.array(k3_fluxes) / 3 + np.array(k4_fluxes) / 6

        return fluxes

    @staticmethod
    def _differential_equation(fluxes, S, S0, dt, args, ind):

        # Specify a state in case None
        if S is None:
            S = S0

        flux_S0, min_S, max_S = fluxes(S0, S0, ind, *args)[:3]  # [flux, min, max, df]

        # Call the ks of RK
        k1 = dt[ind] * sum(flux_S0)
        k2 = dt[ind] * sum(fluxes(S0 + k1 / 2, S0, ind, *args)[0])
        k3 = dt[ind] * sum(fluxes(S0 + k2 / 2, S0, ind, *args)[0])
        k4 = dt[ind] * sum(fluxes(S0 + k3, S0, ind, *args)[0])

        # Calculate the function to set to zero
        fun_to_zero = S - (S0 + k1 / 6 + k2 / 3 + k3 / 3 + k4 / 6)

        # No need to calculate the derivative since the method is explicit

        return (fun_to_zero,     # Fun to set to zero
                min_S,           # Min search
                max_S,           # Max search
                None)            # Derivative of fun -> don't need it because explicit


class RungeKutta4Numba(NumericalApproximator):

    def __init__(self, root_finder):
        """
        This class creates an approximation of an ODE using Runge Kutta of 4th
        order and solves it (finds the value of the state that sets to zero the
        approximation) for all the time steps. The class is designed to operate
        with multiple independent ODEs. For dependent ODEs (i.e. ODE1 depends
        on the state of ODE2 and vice versa) custom solutions must be created.

        Note that this approximator operates under the assumption of constant
        fluxes (see documentation).

        Parameters
        ----------
        root_finder : superflexpy.utils.RootFinder
            Solver used to find the root of the differential equation.
        """

        super().__init__(root_finder=root_finder)

        self.architecture = 'numba'
        self._error_message = 'module : superflexPy, solver : Runge Kutta 4'
        self._error_message += ' Error message : '

        if root_finder.architecture != 'numba':
            message = '{}: architecture of the root_finder must be numba. Given {}'.format(self._error_message, root_finder.architecture)
            raise ValueError(message)

    @staticmethod
    def _get_fluxes(fluxes, S, S0, args, dt):

        # Calculate the state used to calculate the fluxes
        S = S[:-1]
        S = np.insert(S, 0, S0)  # In the following, S is actually S0

        k1_fluxes = fluxes(S, S0, None, *args)[0]
        k2_state = S + (np.sum(k1_fluxes, axis=0) * dt) / 2
        k2_fluxes = fluxes(k2_state, S0, None, *args)[0]
        k3_state = S + (np.sum(k2_fluxes, axis=0) * dt) / 2
        k3_fluxes = fluxes(k3_state, S0, None, *args)[0]
        k4_state = S + (np.sum(k3_fluxes, axis=0) * dt)
        k4_fluxes = fluxes(k4_state, S0, None, *args)[0]

        fluxes = np.array(k1_fluxes) / 6 + np.array(k2_fluxes) / 3 + np.array(k3_fluxes) / 3 + np.array(k4_fluxes) / 6

        return fluxes

    @staticmethod
    @nb.jit(nopython=True)
    def _differential_equation(fluxes, S, S0, dt, args, ind):

        # Specify a state in case None
        if S is None:
            S = S0

        flux_S0, min_S, max_S = fluxes(S0, S0, ind, *args)[:3]  # [flux, min, max, df]

        # Call the ks of RK
        k1 = dt[ind] * sum(flux_S0)
        k2 = dt[ind] * sum(fluxes(S0 + k1 / 2, S0, ind, *args)[0])
        k3 = dt[ind] * sum(fluxes(S0 + k2 / 2, S0, ind, *args)[0])
        k4 = dt[ind] * sum(fluxes(S0 + k3, S0, ind, *args)[0])

        # Calculate the function to set to zero
        fun_to_zero = S - (S0 + k1 / 6 + k2 / 3 + k3 / 3 + k4 / 6)

        # No need to calculate the derivative since the method is explicit

        return (fun_to_zero,     # Fun to set to zero
                min_S,           # Min search
                max_S,           # Max search
                None)            # Derivative of fun -> don't need it because explicit
