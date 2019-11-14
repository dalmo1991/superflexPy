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

This file contains the implementation of the elements of the GR4J model,
combining the continuous state-space representation of Santos et al., 2018
with the original model form Perrin et al., 2003

References
----------
Santos, L., Thirel, G., and Perrin, C.: Continuous state-space representation
of a bucket-type rainfall-runoff model: a case study with the GR4 model using
state-space GR4 (version 1.0), Geosci. Model Dev., 11, 1591–1605,
https://doi.org/10.5194/gmd-11-1591-2018, 2018.

Perrin, C., Michel, C., and Andréassian, V.: Improvement of a parsimonious
model for streamflow simulation, Journal of Hydrology, Volume 279, Issues 1–4,
https://doi.org/10.1016/S0022-1694(03)00225-7, 2003.
"""

from ...framework.element import BaseElement, ODEsElement, LagElement
import numpy as np


class InterceptionFilter(BaseElement):
    """
    This class implement the Interception filter of the GR4J model. The filter
    is a reservoir with zero storage and without parameters. It calculates the
    net input, calculating the difference between potential evapotranspiration
    and precipitation.
    """

    _num_upstream = 1
    _num_downstream = 1

    def set_input(self, input):
        """
        Set the input of the element.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List containing the input fluxes of the element. It contains 2
            fluxes and the order must be the following:
            1. Potential evapotranspiration
            2. Total rainfall
        """

        self.input = {}
        self.input['PET'] = input[0]
        self.input['P'] = input[1]

    def get_output(self, solve=True):
        """
        This method calculates the ammounts of evapotranspiration and
        precipitation that are filtered by the element.

        Parameters
        ----------
        solve : bool
            True if the element has to be solved (i.e. calcualte the states).

        Returns
        -------
        list(numpy.ndarray)
            Output fluxes in the following order:
            1. Net evapotranspiration
            2. Net precipitation
        """

        remove = np.minimum(self.input['PET'], self.input['P'])

        return [self.input['PET'] - remove, self.input['P'] - remove]


class ProductionStore(ODEsElement):
    """
    This class implements the production store of GR4J.
    """

    def __init__(self, parameters, states, solver, id):
        """
        This is the initializer of the class ProductionStore.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            - x1 : maximum soi moisture capacity.
            - alpha : exponent in the evapotranspiration (Es) and main outflow
                      (Ps) equations. Suggested value: 2.0.
            - beta : exponent in the percolation equation. Suggested value: 5.0.
            - ni : coefficient in the percolation equation. Suggested value: 4/9.
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
            message = '{}numba differential equation not implemented'.format(self._error_message)
            raise NotImplementedError(message)
        elif solver.architecture == 'python':
            self._differential_equation = self._differential_equation_python

    def set_input(self, input):
        """
        Set the input of the element.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List containing the input fluxes of the element. It contains 2
            fluxes and the order must be the following:
            1. Potential evapotranspiration
            2. Total rainfall
        """

        self.input = {}
        self.input['PET'] = input[0]
        self.input['P'] = input[1]

    def get_output(self, solve=True):
        """
        This method solves the differential equation governing the production
        store.

        Parameters
        ----------
        solve : bool
            True if the element has to be solved (i.e. calcualte the states).

        Returns
        -------
        list(numpy.ndarray)
            Output fluxes in the following order:
            1. Total outflow (Perc + Pn - Ps)
        """

        if solve:
            # Solve the differential equation
            self._solver_states = [self._states[self._prefix_states + 'S0']]
            self._solve_differential_equation()

            # Update the states
            self.set_states({self._prefix_states + 'S0': self.state_array[-1, 0]})

        x1 = self._parameters[self._prefix_parameters + 'x1']
        alpha = self._parameters[self._prefix_parameters + 'alpha']
        beta = self._parameters[self._prefix_parameters + 'beta']
        ni = self._parameters[self._prefix_parameters + 'ni']

        Pn_minus_Ps = self.input['P'] * np.power(self.state_array[:, 0] / x1, alpha)
        Perc = (np.power(x1, 1 - beta) / ((beta - 1) * self._dt)) *\
            np.power(ni, beta - 1) *\
            np.power(self.state_array[:, 0], beta)

        return [Pn_minus_Ps + Perc]

    def get_aet(self):
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

        PET = self.input['PET']
        x1 = self._parameters[self._prefix_parameters + 'x1']
        alpha = self._parameters[self._prefix_parameters + 'alpha']

        return PET * (2 * (S / x1) - np.power(S / x1, alpha))

    @staticmethod
    def _differential_equation_python(S, S0, P, x1, alpha, beta, ni, PET, dt):

        if S is None:
            S = 0

        return(
            (S - S0) / dt - P * (1 - (S / x1)**alpha) + PET * (2 * (S / x1) - (S / x1)**alpha)
            + ((x1**(1 - beta)) / ((beta - 1) * dt)) * (ni**(beta - 1)) * (S**beta),
            0.0,
            S0 + P
        )


class RoutingStore(ODEsElement):
    """
    This class implements the routing store of GR4J.
    """

    def __init__(self, parameters, states, solver, id):
        """
        This is the initializer of the class ProductionStore.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            - x2 : exchange coefficient
            - x3 : maximum routing capacity
            - gamma : exponent in the main outflow (Qr) equation. Suggested value: 5
            - omega : Exponent in the exchange flux (F) equation. Suggested value: 3.5
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
            message = '{}numba differential equation not implemented'.format(self._error_message)
            raise NotImplementedError(message)
        elif solver.architecture == 'python':
            self._differential_equation = self._differential_equation_python

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

        self.input = {}
        self.input['P'] = input[0]

    def get_output(self, solve=True):
        """
        This method solves the differential equation governing the routing
        store.

        Returns
        -------
        list(numpy.ndarray)
            Output fluxes in the following order:
            1. Total outflow (Qr)
            2. Exchange flux (F), positive if loss
        """

        if solve:
            # Solve the differential equation
            self._solver_states = [self._states[self._prefix_states + 'S0']]
            self._solve_differential_equation()

            # Update the states
            self.set_states({self._prefix_states + 'S0': self.state_array[-1, 0]})

        x2 = self._parameters[self._prefix_parameters + 'x2']
        x3 = self._parameters[self._prefix_parameters + 'x3']
        gamma = self._parameters[self._prefix_parameters + 'gamma']
        omega = self._parameters[self._prefix_parameters + 'omega']

        Qr = (np.power(x3, 1 - gamma) / ((gamma - 1) * self._dt)) * \
            np.power(self.state_array[:, 0], gamma)
        F = x2 * np.power(self.state_array[:, 0] / x3, omega)

        return [Qr, F]

    @staticmethod
    def _differential_equation_python(S, S0, P, x2, x3, gamma, omega, dt):

        if S is None:
            S = 0

        return(
            (S - S0) / dt - P + ((x3**(1 - gamma)) / ((gamma - 1) * dt)) * (S**gamma)
            + (x2 * (S / x3)**omega),
            0.0,
            S0 + P
        )


class FluxAggregator(BaseElement):
    """
    This class calculates the final output of GR4J, aggregating the output
    of the routing store with the one of the unit hydrograph 2 and subtracting
    the loss F.
    """

    _num_downstream = 1
    _num_upstream = 1

    def set_input(self, input):
        """
        Set the input of the element.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List containing the input fluxes of the element. It contains 3
            fluxes and the order must be the following:
            1. Outflow routing store (Qr)
            2. Exchange flux (F)
            3. Outflow UH2 (Q2_out)
        """

        self.input = {}
        self.input['Qr'] = input[0]
        self.input['F'] = input[1]
        self.input['Q2_out'] = input[2]

    def get_output(self, solve=True):
        """
        This method calculates the total outflow of GR4J.

        Returns
        -------
        list(numpy.ndarray)
            Output fluxes in the following order:
            1. Total outflow
        """

        return [self.input['Qr']
                + np.maximum(0, self.input['Q2_out'] - self.input['F'])]


class UnitHydrograph1(LagElement):
    """
    This class implements the UnitHydrograph1 of GR4J.
    """

    def __init__(self, parameters, states, id):
        """
        This is the initializer of the UnitHydrograph1.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            - lag_time : total length (base) of the lag function. It is equal
                         to x4 in GR4J.
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
            value = (bin / len)**2.5
        else:
            value = 1
        return value


class UnitHydrograph2(LagElement):
    """
    This class implements the UnitHydrograph2 of GR4J.
    """

    def __init__(self, parameters, states, id):
        """
        This is the initializer of the UnitHydrograph2.

        Parameters
        ----------
        parameters : dict
            Parameters of the element. The keys must be:
            - lag_time : total length (base) of the lag function. It is equal
                         to 2*x4 in GR4J.
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
        half_len = len / 2
        if bin <= 0:
            value = 0
        elif bin < half_len:
            value = 0.5 * (bin / half_len)**2.5
        elif bin < len:
            value = 1 - 0.5 * (2 - bin / half_len)**2.5
        else:
            value = 1
        return value
