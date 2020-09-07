"""
Copyright 2020 Marco Dal Molin et al.

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
DESIGNED BY: Marco Dal Molin

This file contains the implementation a class that solved the ODEs using the
implicit Euler numerical approximation.
"""


import numpy as np
import numba as nb
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

        NumericalApproximator.__init__(self,
                                        root_finder=root_finder)

        self.architecture = 'python'
        self._error_message = 'module : superflexPy, solver : implicit Euler'
        self._error_message += ' Error message : '

        if root_finder.architecture != 'python':
            message = '{}: architecture of the root_finder must be python. Given {}'.format(self._error_message, root_finder.architecture)
            raise ValueError(message)

    @staticmethod
    def _get_fluxes(fluxes, S, S0, args):

        flux = fluxes(S, S0, None, *args)  # If different method we would provide a different first argument. S0 not used.

        return np.array(flux[0])  # It is a list of vectors

    @staticmethod
    def _differential_equation(fluxes, S, S0, dt, args, ind):

        # Specify a state in case None
        if S is None:
            S = S0

        # Call the function that calculates the fluxes
        fluxes_out = fluxes(S, S0, ind, *args)

        fl = fluxes_out[0]

        # Calculate the numerical approximation of the differential equation
        dif_eq = (S - S0) / dt[ind] - sum(fl)

        return (dif_eq,           # Fun to set to zero
                fluxes_out[1],    # Min search
                fluxes_out[2])    # Max search


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

        NumericalApproximator.__init__(self,
                                        root_finder=root_finder)

        self.architecture = 'numba'
        self._error_message = 'module : superflexPy, solver : implicit Euler'
        self._error_message += ' Error message : '

        if root_finder.architecture != 'numba':
            message = '{}: architecture of the root_finder must be numba. Given {}'.format(self._error_message, root_finder.architecture)
            raise ValueError(message)

    @staticmethod  # I do not use numba. Do not need it
    def _get_fluxes(fluxes, S, S0, args):

        flux = fluxes(S, S0, None, *args)  # If different method we would provide a different first argument. S0 not used.

        return np.array(flux[0])  # It is a list of vectors

    @staticmethod
    @nb.jit(nopython=True)
    def _differential_equation(fluxes, S, S0, dt, ind, args):

        # Specify a state in case None
        if S is None:
            S = S0

        # Call the function that calculates the fluxes
        fluxes_out = fluxes(S, S0, ind, *args)

        fl = fluxes_out[0]

        # Calculate the numerical approximation of the differential equation
        # Need to loop because of numba
        sum_flux = 0
        for f in fl:
            sum_flux += f

        dif_eq = (S - S0) / dt[ind] - sum_flux

        return (dif_eq,           # Fun to set to zero
                fluxes_out[1],    # Min search
                fluxes_out[2])    # Max search
