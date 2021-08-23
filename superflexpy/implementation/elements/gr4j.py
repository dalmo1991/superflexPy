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
import numba as nb


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

    def __init__(self, parameters, states, approximation, id):
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
        approximation : superflexpy.utils.numerical_approximation.NumericalApproximator
            Numerial method used to approximate the differential equation
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
            self._fluxes = [self._flux_function_python]

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

        fluxes = self._num_app.get_fluxes(fluxes=self._fluxes_python,
                                          S=self.state_array,
                                          S0=self._solver_states,
                                          dt=self._dt,
                                          **self.input,
                                          **{k[len(self._prefix_parameters):]: self._parameters[k] for k in self._parameters},
                                          )

        Pn_minus_Ps = self.input['P'] - fluxes[0][0]
        Perc = - fluxes[0][2]
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
            S = self.state_array
        except AttributeError:
            message = '{}get_aet method has to be run after running '.format(self._error_message)
            message += 'the model using the method get_output'
            raise AttributeError(message)

        fluxes = self._num_app.get_fluxes(fluxes=self._fluxes_python,
                                          S=S,
                                          S0=self._solver_states,
                                          dt=self._dt,
                                          **self.input,
                                          **{k[len(self._prefix_parameters):]: self._parameters[k] for k in self._parameters},
                                          )

        return [- fluxes[0][1]]

    @staticmethod
    def _flux_function_python(S, S0, ind, P, x1, alpha, beta, ni, PET, dt):

        if ind is None:
            return(
                [
                    P * (1 - (S / x1)**alpha),  # Ps
                    - PET * (2 * (S / x1) - (S / x1)**alpha),  # Evaporation
                    - ((x1**(1 - beta)) / ((beta - 1) * dt)) * (ni**(beta - 1)) * (S**beta)  # Perc
                ],
                0.0,
                S0 + P * (1 - (S / x1)**alpha) * dt
            )
        else:
            return(
                [
                    P[ind] * (1 - (S / x1[ind])**alpha[ind]),  # Ps
                    - PET[ind] * (2 * (S / x1[ind]) - (S / x1[ind])**alpha[ind]),  # Evaporation
                    - ((x1[ind]**(1 - beta[ind])) / ((beta[ind] - 1) * dt[ind])) * (ni[ind]**(beta[ind] - 1)) * (S**beta[ind])  # Perc
                ],
                0.0,
                S0 + P[ind] * (1 - (S / x1[ind])**alpha[ind]) * dt[ind],
                [
                    - (P[ind] * alpha[ind] / x1[ind]) * ((S / x1[ind])**(alpha[ind] - 1)),
                    - (PET[ind] / x1[ind]) * (2 - alpha[ind] * ((S / x1[ind])**(alpha[ind] - 1))),
                    - beta[ind] * ((x1[ind]**(1 - beta[ind])) / ((beta[ind] - 1) * dt[ind])) * (ni[ind]**(beta[ind] - 1)) * (S**(beta[ind] - 1))
                ]
            )

    @staticmethod
    @nb.jit('Tuple((UniTuple(f8, 3), f8, f8, UniTuple(f8, 3)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])',
            nopython=True)
    def _flux_function_numba(S, S0, ind, P, x1, alpha, beta, ni, PET, dt):

        return(
            (
                P[ind] * (1 - (S / x1[ind])**alpha[ind]),  # Ps
                - PET[ind] * (2 * (S / x1[ind]) - (S / x1[ind])**alpha[ind]),  # Evaporation
                - ((x1[ind]**(1 - beta[ind])) / ((beta[ind] - 1) * dt[ind])) * (ni[ind]**(beta[ind] - 1)) * (S**beta[ind])  # Perc
            ),
            0.0,
            S0 + P[ind] * (1 - (S / x1[ind])**alpha[ind]) * dt[ind],
            (
                - (P[ind] * alpha[ind] / x1[ind]) * ((S / x1[ind])**(alpha[ind] - 1)),
                - (PET[ind] / x1[ind]) * (2 - alpha[ind] * ((S / x1[ind])**(alpha[ind] - 1))),
                - beta[ind] * ((x1[ind]**(1 - beta[ind])) / ((beta[ind] - 1) * dt[ind])) * (ni[ind]**(beta[ind] - 1)) * (S**(beta[ind] - 1))
            )
        )


class RoutingStore(ODEsElement):
    """
    This class implements the routing store of GR4J.
    """

    def __init__(self, parameters, states, approximation, id):
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
        approximation : superflexpy.utils.numerical_approximation.NumericalApproximator
            Numerial method used to approximate the differential equation
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
            self._fluxes = [self._flux_function_python]

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

        fluxes = self._num_app.get_fluxes(fluxes=self._fluxes_python,
                                          S=self.state_array,
                                          S0=self._solver_states,
                                          dt=self._dt,
                                          **self.input,
                                          **{k[len(self._prefix_parameters):]: self._parameters[k] for k in self._parameters},
                                          )

        Qr = - fluxes[0][1]
        F = -fluxes[0][2]

        return [Qr, F]

    @staticmethod
    def _flux_function_python(S, S0, ind, P, x2, x3, gamma, omega, dt):

        if ind is None:
            return(
                [
                    P,  # P
                    - ((x3**(1 - gamma)) / ((gamma - 1) * dt)) * (S**gamma),  # Qr
                    - (x2 * (S / x3)**omega),  # F
                ],
                0.0,
                S0 + P * dt
            )
        else:
            return(
                [
                    P[ind],  # P
                    - ((x3[ind]**(1 - gamma[ind])) / ((gamma[ind] - 1) * dt[ind])) * (S**gamma[ind]),  # Qr
                    - (x2[ind] * (S / x3[ind])**omega[ind]),  # F
                ],
                0.0,
                S0 + P[ind] * dt[ind],
                [
                    0.0,
                    - ((x3[ind]**(1 - gamma[ind])) / ((gamma[ind] - 1) * dt[ind])) * (S**(gamma[ind] - 1)) * gamma[ind],
                    - (omega[ind] * x2[ind] * ((S / x3[ind])**(omega[ind] - 1))) / x3[ind]
                ]
            )

    @staticmethod
    @nb.jit('Tuple((UniTuple(f8, 3), f8, f8, UniTuple(f8, 3)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])',
            nopython=True)
    def _flux_function_numba(S, S0, ind, P, x2, x3, gamma, omega, dt):

        return(
            (
                P[ind],  # P
                - ((x3[ind]**(1 - gamma[ind])) / ((gamma[ind] - 1) * dt[ind])) * (S**gamma[ind]),  # Qr
                - (x2[ind] * (S / x3[ind])**omega[ind]),  # F
            ),
            0.0,
            S0 + P[ind] * dt[ind],
            (
                0.0,
                - ((x3[ind]**(1 - gamma[ind])) / ((gamma[ind] - 1) * dt[ind])) * (S**(gamma[ind] - 1)) * gamma[ind],
                - (omega[ind] * x2[ind] * ((S / x3[ind])**(omega[ind] - 1)))
            )
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
