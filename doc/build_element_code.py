import numba as nb
import numpy as np

from superflexpy.framework.element import LagElement, ODEsElement, ParameterizedElement

# Implement a linear reservoir


class LinearReservoir(ODEsElement):
    """
    This class implements a simple linear reservoir.

    Parameters
    ----------
    parameters : dict
        Parameters of the element. The keys must be:
            - k : multiplier of the state
    states : dict
            Initial state of the element. The keys must be:
            - 'S0' : initial storage of the reservoir.
    approximation : superflexpy.utils.numerical_approximation.NumericalApproximator
        Numerial method used to approximate the differential equation
    id : str
        Itentifier of the element. All the elements of the framework must
        have an id.
    """

    def __init__(self, parameters, states, approximation, id):
        ODEsElement.__init__(self, parameters=parameters, states=states, approximation=approximation, id=id)

        self._fluxes_python = [self._fluxes_function_python]  # Used by get fluxes, regardless of the architecture

        if approximation.architecture == "numba":
            self._fluxes = [self._fluxes_function_numba]
        elif approximation.architecture == "python":
            self._fluxes = [self._fluxes_function_python]
        else:
            message = "{}The architecture ({}) of the approximation is not correct".format(
                self._error_message, approximation.architecture
            )
            raise ValueError(message)

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

        self.input = {"P": input[0]}

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
            self._solver_states = [self._states[self._prefix_states + "S0"]]
            self._solve_differential_equation()

            # Update the state
            self.set_states({self._prefix_states + "S0": self.state_array[-1, 0]})

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,
            S=self.state_array,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )
        return [-fluxes[0][1]]

    @staticmethod
    def _fluxes_function_python(S, S0, ind, P, k, dt):
        if ind is None:
            return (
                [
                    P,
                    -k * S,
                ],
                0.0,
                S0 + P * dt,
            )
        else:
            return (
                [
                    P[ind],
                    -k[ind] * S,
                ],
                0.0,
                S0 + P[ind] * dt[ind],
                [0.0, -k[ind]],
            )

    @staticmethod
    @nb.jit("Tuple((UniTuple(f8, 2), f8, f8))(optional(f8), f8, i4, f8[:], f8[:], f8[:])", nopython=True)
    def _fluxes_function_numba(S, S0, ind, P, k, dt):
        return (
            (
                P[ind],
                -k[ind] * S,
            ),
            0.0,
            S0 + P[ind] * dt[ind],
            (0.0, -k[ind]),
        )


# Implement lag function


class TriangularLag(LagElement):
    """
    This class defines the half-triangular lag function.

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

    def _build_weight(self, lag_time):
        weight = []

        for t in lag_time:
            array_length = np.ceil(t)
            w_i = []

            for i in range(int(array_length)):
                w_i.append(self._calculate_lag_area(i + 1, t) - self._calculate_lag_area(i, t))

            weight.append(np.array(w_i))

        return weight

    @staticmethod
    def _calculate_lag_area(bin, len):
        if bin <= 0:
            value = 0
        elif bin < len:
            value = (bin / len) ** 2
        else:
            value = 1

        return value


# Implement a parametrized splitter


class ParameterizedSingleFluxSplitter(ParameterizedElement):
    """
    This class implements an element that takes a single flux and splits it
    between two downstream element based on the value of a parameter.

    Parameters
    ----------
    parameters : dict
        Parameters of the element. The keys must be:
        - split-par : Parameter used for splitting; split-par goes to the
                      first downstream element, (1 - split-par) goes to the
                      second downstream element
    id : str
        Itentifier of the element. All the elements of the framework must have
        an id.
    """

    _num_downstream = 2
    _num_upstream = 1

    def set_input(self, input):
        """
        Set the input of the element.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List containing the input fluxes of the element. It contains 1
            flux:
            1. Incoming flow
        """

        self.input = {"Q_in": input[0]}

    def get_output(self, solve=True):
        """
        This method returns the output of the element.

        Parameters
        ----------
        solve : bool
            Always set Ture. Not needed for this element

        Returns
        -------
        list(numpy.ndarray)
            List of output fluxes.
        """

        # solve is not needed but kept in the interface

        split_par = self._parameters[self._prefix_parameters + "split-par"]

        return [self.input["Q_in"] * split_par, self.input["Q_in"] * (1 - split_par)]
