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

This file contains the implementation of some common reservoirs that can be
found, for example, in the HBV model.
"""


from ...framework.element import ODEsElement
import numba as nb


class FastReservoir(ODEsElement):
    """
    This class implements the FastReservoir present in HBV.
    """

    def __init__(self, parameters, states, solver, id):
        """
        This is the initializer of the class FastReservoir.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            - 'k' : multiplier of the state
            - 'alpha' : exponent of the state
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

    # METHODS FOR THE USER

    def set_input(self, input):
        """
        Set the input of the element.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List containing the input fluxes of the element. It contains 1
            flux:
            1. Rainfall
        """

        self.input = {'P': input[0]}

    def get_output(self, solve=True):
        """
        This method solves the differential equation governing the routing
        store.

        Returns
        -------
        list(numpy.ndarray)
            Output fluxes in the following order:
            1. Streamflow (Q)
        """

        if solve:
            self._solver_states = [self._states[self._prefix_states + 'S0']]
            self._solve_differential_equation()

            # Update the state
            self.set_states({self._prefix_states + 'S0': self.state_array[-1, 0]})

        k = self._parameters[self._prefix_parameters + 'k']
        alpha = self._parameters[self._prefix_parameters + 'alpha']
        return [k * self.state_array[:, 0] ** alpha]

    # PROTECTED METHODS

    @staticmethod
    def _differential_equation_python(S, S0, P, k, alpha, dt):
        if S is None:
            S = 0
        return ((S - S0) / dt - P + k * S**alpha, 0.0, S0 + P)

    @staticmethod
    @nb.jit('UniTuple(f8, 3)(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:])',
            nopython=True)
    def _differential_equation_numba(S, S0, ind, P, k, alpha, dt):
        if S is None:
            S = 0
        dt = dt[ind]
        P = P[ind]
        k = k[ind]
        alpha = alpha[ind]
        return ((S - S0) / dt - P + k * S**alpha, 0.0, S0 + P)


class UnsaturatedReservoir(ODEsElement):
    """
    This class implements the UnsaturatedReservoir of HBV.
    """

    def __init__(self, parameters, states, solver, id):
        """
        This is the initializer of the class UnsaturatedReservoir.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            'Smax' : maximum reservoir storage
            'Ce' : Potential evapotranspiration multiplier
            'm' : Smoothing factor for evapotranspiration
            'beta' : Exponent in the relation for the streamflow
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

    # METHODS FOR THE USER

    def set_input(self, input):
        """
        Set the input of the element.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List containing the input fluxes of the element. It contains 2
            fluxes:
            1. Rainfall
            2. PET
        """

        self.input = {'P': input[0],
                      'PET': input[1]}

    def get_output(self, solve=True):
        """
        This method solves the differential equation governing the routing
        store.

        Returns
        -------
        list(numpy.ndarray)
            Output fluxes in the following order:
            1. Streamflow (Q)
        """

        if solve:
            self._solver_states = [self._states[self._prefix_states + 'S0']]

            self._solve_differential_equation()

            # Update the state
            self.set_states({self._prefix_states + 'S0': self.state_array[-1, 0]})

        Smax = self._parameters[self._prefix_parameters + 'Smax']
        beta = self._parameters[self._prefix_parameters + 'beta']
        return [self.input['P'] * (self.state_array[:, 0] / Smax) ** beta]

    def get_AET(self):
        """
        This method calculates the actual evapotranspiration

        Returns
        -------
        numpy.ndarray
            Array of actual evapotranspiration
        """

        try:
            S = self.state_array[:, 0]
        except AttributeError:
            message = '{}get_aet method has to be run after running '.format(self._error_message)
            message += 'the model using the method get_output'
            raise AttributeError(message)
        Ce = self._parameters[self._prefix_parameters + 'Ce']
        PET = self.input['PET']
        Smax = self._parameters[self._prefix_parameters + 'Smax']
        m = self._parameters[self._prefix_parameters + 'm']

        return Ce * PET * ((S / Smax) * (1 + m)) / ((S / Smax) + m)

    # PROTECTED METHODS

    @staticmethod
    def _differential_equation_python(S, S0, P, Smax, Ce, m, beta, PET, dt):
        # TODO: handle time variable parameters (Smax) -> overflow
        if S is None:
            S = 0
        return ((S - S0) / dt - P + Ce * PET * ((S / Smax) * (1 + m))
                / ((S / Smax) + m) + P * (S / Smax)**beta, 0.0, S0 + P)

    @staticmethod
    @nb.jit('UniTuple(f8, 3)(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])',
            nopython=True)
    def _differential_equation_numba(S, S0, ind, P, Smax, Ce, m, beta, PET, dt):
        if S is None:
            S = 0
        P = P[ind]
        Smax = Smax[ind]
        Ce = Ce[ind]
        m = m[ind]
        beta = beta[ind]
        PET = PET[ind]
        dt = dt[ind]
        return ((S - S0) / dt - P + Ce * PET * ((S / Smax) * (1 + m))
                / ((S / Smax) + m) + P * (S / Smax)**beta, 0.0, S0 + P)
