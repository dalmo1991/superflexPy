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
implicit Euler numerical approximation.
"""


import numba as nb
import numpy as np

from ...utils.numerical_approximator import NumericalApproximator


class ImplicitEulerPython(NumericalApproximator):
    def __init__(self, root_finder):
        """
        This class creates an approximation of an ODE using implicit Euler and
        solves it (finds the value of the state that sets to zero the
        approximation) for all the time steps. The class is designed to operate
        with multiple independent ODEs. For dependent ODEs (i.e. ODE1 depends
        on the state of ODE2 and vice versa) custom solutions must be created.

        Parameters
        ----------
        root_finder : superflexpy.utils.RootFinder
            Solver used to find the root of the differential equation.
        """

        NumericalApproximator.__init__(self, root_finder=root_finder)

        self.architecture = "python"
        self._error_message = "module : superflexPy, solver : implicit Euler"
        self._error_message += " Error message : "

        if root_finder.architecture != "python":
            message = "{}: architecture of the root_finder must be python. Given {}".format(
                self._error_message, root_finder.architecture
            )
            raise ValueError(message)

    @staticmethod
    def _get_fluxes(fluxes, S, S0, args, dt):
        flux = fluxes(
            S, S0, None, *args
        )  # If different method we would provide a different first argument. S0 not used.

        return np.array(flux[0])  # It is a list of vectors

    @staticmethod
    def _differential_equation(fluxes, S, S0, dt, args, ind):
        # Specify a state in case None
        if S is None:
            S = S0

        # Call the function that calculates the fluxes
        fluxes_out = fluxes(S, S0, ind, *args)

        # Calculate the numerical approximation of the differential equation
        fl = fluxes_out[0]
        diff_eq = (S - S0) / dt[ind] - sum(fl)

        # Calculate its derivative
        try:
            d_fl = fluxes_out[3]
            d_diff_eq = (1 / dt[ind]) - sum(d_fl)
        except IndexError:
            # in case the element does not calculate derivatives
            d_diff_eq = np.nan

        return (
            diff_eq,  # Fun to set to zero
            fluxes_out[1],  # Min search
            fluxes_out[2],  # Max search
            d_diff_eq,
        )  # Derivative of fun


class ImplicitEulerNumba(NumericalApproximator):
    def __init__(self, root_finder):
        """
        This class creates an approximation of an ODE using implicit Euler and
        solves it (finds the value of the state that sets to zero the
        approximation) for all the time steps. The class is designed to operate
        with multiple independent ODEs. For dependent ODEs (i.e. ODE1 depends
        on the state of ODE2 and vice versa) custom solutions must be created.

        Parameters
        ----------
        root_finder : superflexpy.utils.RootFinder
            Solver used to find the root of the differential equation.
        """

        NumericalApproximator.__init__(self, root_finder=root_finder)

        self.architecture = "numba"
        self._error_message = "module : superflexPy, solver : implicit Euler"
        self._error_message += " Error message : "

        if root_finder.architecture != "numba":
            message = "{}: architecture of the root_finder must be numba. Given {}".format(
                self._error_message, root_finder.architecture
            )
            raise ValueError(message)

    @staticmethod  # I do not use numba. Do not need it
    def _get_fluxes(fluxes, S, S0, args, dt):
        flux = fluxes(
            S, S0, None, *args
        )  # If different method we would provide a different first argument. S0 not used.

        return np.array(flux[0])  # It is a list of vectors

    @staticmethod
    @nb.jit(nopython=True)
    def _differential_equation(fluxes, S, S0, dt, ind, args):
        # Specify a state in case None
        if S is None:
            S = S0

        # Call the function that calculates the fluxes
        fluxes_out = fluxes(S, S0, ind, *args)

        # Calculate the numerical approximation of the differential equation
        fl = fluxes_out[0]
        sum_flux = 0
        for f in fl:
            sum_flux += f

        diff_eq = (S - S0) / dt[ind] - sum_flux

        # Calculate its derivative
        d_fl = fluxes_out[3]
        sum_d_flux = 0
        for df in d_fl:
            sum_d_flux += df

        d_diff_eq = (1 / dt[ind]) - sum_d_flux

        return (
            diff_eq,  # Fun to set to zero
            fluxes_out[1],  # Min search
            fluxes_out[2],  # Max search
            d_diff_eq,
        )  # Derivative of fun
