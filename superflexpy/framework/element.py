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

This file contains the implementation of Element classes with different levels
of specialization.
"""

from copy import deepcopy, copy
import numpy as np


class BaseElement():
    """
    This is the abstract class for the creation of a BaseElement. A BaseElement
    does not have parameters or states.
    """

    _num_downstream = None
    """
    Number of downstream elements
    """

    _num_upstream = None
    """
    Number of upstream elements
    """

    input = {}
    """
    Dictionary of input fluxes
    """

    def __init__(self, id):
        """
        This is the initializer of the abstract class BaseElement.

        Parameters
        ----------
        id : str
            Identifier of the element. All the elements of the framework must
            have an identifier.
        """

        self.id = id
        self._error_message = 'module : superflexPy, Element : {},'.format(id)
        self._error_message += ' Error message : '

    def set_input(self, input):
        """
        To be implemented by any child class. It populates the self.input
        dictionary.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List of input fluxes to the element.
        """

        raise NotImplementedError('The set_input method must be implemented')

    def get_output(self, solve=True):
        """
        To be implemented by any child class. It solves the element and returns
        the output fluxes.

        Parameters
        ----------
        solve : bool
            True if the element has to be solved (i.e. calculate the states).

        Returns
        -------
        list(numpy.ndarray)
            List of output fluxes.
        """

        raise NotImplementedError('The get_output method must be implemented')

    @property
    def num_downstream(self):
        """
        Number of downstream elements.
        """

        return self._num_downstream

    @property
    def num_upstream(self):
        """
        Number of upstream elements
        """

        return self._num_upstream

    def __repr__(self):

        str = 'Module: superflexPy\nElement: {}\n'.format(self.id)
        return str

    def __copy__(self):
        ele = self.__class__(id=self.id)
        return ele

    def __deepcopy__(self, memo):
        ele = self.__class__(id=self.id)
        return ele


class ParameterizedElement(BaseElement):
    """
    This is the abstract class for the creation of a ParameterizedElement. A
    ParameterizedElement has parameters but not states.
    """

    _prefix_parameters = ''
    """
    Prefix applied to the original names of the parameters
    """

    def __init__(self, parameters, id):
        """
        This is the initializer of the abstract class ParameterizedElement.

        Parameters
        ----------
        parameters : dict
            Parameters controlling the element. The parameters can be either
            a float (constant in time) or a numpy.ndarray of the same length
            of the input fluxes (time variant parameters).
        id : str
            Identifier of the element. All the elements of the framework must
            have an identifier.
        """

        BaseElement.__init__(self, id)

        self._parameters = parameters
        self.add_prefix_parameters(id)

    def get_parameters(self, names=None):
        """
        This method returns the parameters of the element.

        Parameters
        ----------
        names : list(str)
            Names of the parameters to return. The names must be the ones
            returned by the method get_parameters_name. If None, all the
            parameters are returned.

        Returns
        -------
        dict:
            Parameters of the element.
        """

        if names is None:
            return self._parameters
        else:
            return {n: self._parameters[n] for n in names}

    def get_parameters_name(self):
        """
        This method returns the names of the parameters of the element.

        Returns
        -------
        list(str):
            List with the names of the parameters.
        """

        return list(self._parameters.keys())

    def set_parameters(self, parameters):
        """
        This method sets the values of the parameters.

        Parameters
        ----------
        parameters : dict
            Contains the parameters of the element to be set. The keys must be
            the ones returned by the method get_parameters_name. Only the
            parameters that have to be changed should be passed.
        """

        for k in parameters.keys():
            if k not in self._parameters.keys():
                message = '{}The parameter {} does not exist'.format(self._error_message, k)
                raise KeyError(message)
            self._parameters[k] = parameters[k]

    def add_prefix_parameters(self, prefix):
        """
        This method add a prefix to the name of the parameters of the element.

        Parameters
        ----------
        prefix : str
            Prefix to be added. It cannot contain '_'.
        """

        if '_' in prefix:
            message = '{}The prefix cannot contain \'_\''.format(self._error_message)
            raise ValueError(message)

        # Extract the prefixes in the parameters name
        splitted = list(self._parameters.keys())[0].split('_')

        if prefix not in splitted:
            # Apply the prefix
            for k in list(self._parameters.keys()):
                value = self._parameters.pop(k)
                self._parameters['{}_{}'.format(prefix, k)] = value

            # Save the prefix for furure uses
            self._prefix_parameters = '{}_{}'.format(prefix, self._prefix_parameters)

    def __repr__(self):

        str = 'Module: superflexPy\nElement: {}\n'.format(self.id)
        str += 'Parameters:\n'
        for k in self._parameters:
            str += '\t{} : {}\n'.format(k, self._parameters[k])

        return str

    def __copy__(self):
        p = self._parameters  # Only the reference
        ele = self.__class__(parameters=p,
                             id=self.id)
        ele._prefix_parameters = self._prefix_parameters
        return ele

    def __deepcopy__(self, memo):
        p = deepcopy(self._parameters)  # Create a new dictionary
        ele = self.__class__(parameters=p,
                             id=self.id)
        ele._prefix_parameters = self._prefix_parameters
        return ele


class StateElement(BaseElement):
    """
    This is the abstract class for the creation of a StateElement. A
    StateElement has states but not parameters.
    """

    _prefix_states = ''
    """
    Prefix applied to the original names of the parameters
    """

    def __init__(self, states, id):
        """
        This is the initializer of the abstract class StateElement.

        Parameters
        ----------
        states : dict
            Initial states of the element. Depending on the element the states
            can be either a float or a numpy.ndarray.
        id : str
            Identifier of the element. All the elements of the framework must
            have an id.
        """
        BaseElement.__init__(self, id)

        self._states = states
        self._init_states = deepcopy(states)  # It is used to re-set the states
        self.add_prefix_states(id)

    def get_states(self, names=None):
        """
        This method returns the states of the element.

        Parameters
        ----------
        names : list(str)
            Names of the states to return. The names must be the ones
            returned by the method get_states_name. If None, all the
            states are returned.

        Returns
        -------
        dict:
            States of the element.
        """

        if names is None:
            return self._states
        else:
            return {n: self._states[n] for n in names}

    def get_states_name(self):
        """
        This method returns the names of the states of the element.

        Returns
        -------
        list(str):
            List with the names of the states.
        """

        return list(self._states.keys())

    def set_states(self, states):
        """
        This method sets the values of the states.

        Parameters
        ----------
        states : dict
            Contains the states of the element to be set. The keys must be
            the ones returned by the method get_states_name. Only the
            states that have to be changed should be passed.
        """

        for k in states.keys():
            if k not in self._states.keys():
                message = '{}The state {} does not exist'.format(self._error_message, k)
                raise KeyError(message)
            self._states[k] = states[k]

    def reset_states(self):
        """
        This method sets the states to the values provided to the __init__
        method. If a state was initialized as None, it will not be reset.
        """

        for k in self._init_states.keys():
            k_no_prefix = k.split('_')[-1]
            if self._init_states[k] is not None:
                self._states[self._prefix_states + k_no_prefix] = deepcopy(self._init_states[k])  # I have to isolate

    def add_prefix_states(self, prefix):
        """
        This method add a prefix to the id of the states of the element.

        Parameters
        ----------
        prefix : str
            Prefix to be added. It cannot contain '_'.
        """

        if '_' in prefix:
            message = '{}The prefix cannot contain \'_\''.format(self._error_message)
            raise ValueError(message)

        # Extract the prefixes in the parameters name
        splitted = list(self._states.keys())[0].split('_')

        if prefix not in splitted:
            # Apply the prefix
            for k in list(self._states.keys()):
                value = self._states.pop(k)
                self._states['{}_{}'.format(prefix, k)] = value

            # Save the prefix for furure uses
            self._prefix_states = '{}_{}'.format(prefix, self._prefix_states)

    def __repr__(self):

        str = 'Module: superflexPy\nElement: {}\n'.format(self.id)
        str += 'States:\n'
        for k in self._states:
            str += '\t{} : {}\n'.format(k, self._states[k])

        return str

    def __copy__(self):
        s = deepcopy(self._states)  # Create a new dictionary
        ele = self.__class__(states=s,
                             id=self.id)
        ele._prefix_states = self._prefix_states
        return ele

    def __deepcopy__(self, memo):
        s = deepcopy(self._states)  # Create a new dictionary
        ele = self.__class__(states=s,
                             id=self.id)
        ele._prefix_states = self._prefix_states
        return ele


class StateParameterizedElement(StateElement, ParameterizedElement):
    """
    This is the abstract class for the creation of a StateParameterizedElement.
    A StateParameterizedElement has parameters and states.
    """

    def __init__(self, parameters, states, id):
        """
        This is the initializer of the abstract class
        StateParameterizedElement.

        Parameters
        ----------
        parameters : dict
            Parameters controlling the element. The parameters can be either
            a float (constant in time) or a numpy.ndarray of the same length
            of the input fluxes (time variant parameters).
        states : dict
            Initial states of the element. Depending on the element the states
            can be either a float or a numpy.ndarray.
        id : str
            Identifier of the element. All the elements of the framework must
            have an id.
        """

        StateElement.__init__(self, states, id)
        ParameterizedElement.__init__(self, parameters, id)

    def __repr__(self):

        str = 'Module: superflexPy\nElement: {}\n'.format(self.id)
        str += 'Parameters:\n'
        for k in self._parameters:
            str += '\t{} : {}\n'.format(k, self._parameters[k])
        str += 'States:\n'
        for k in self._states:
            str += '\t{} : {}\n'.format(k, self._states[k])

        return str

    def __copy__(self):
        p = self._parameters  # Only the reference
        s = deepcopy(self._states)  # Create a new dictionary
        ele = self.__class__(parameters=p,
                             states=s,
                             id=self.id)
        ele._prefix_states = self._prefix_states
        ele._prefix_parameters = self._prefix_parameters
        return ele

    def __deepcopy__(self, memo):
        p = deepcopy(self._parameters)  # Create a new dictionary
        s = deepcopy(self._states)  # Create a new dictionary
        ele = self.__class__(parameters=p,
                             states=s,
                             id=self.id)
        ele._prefix_states = self._prefix_states
        ele._prefix_parameters = self._prefix_parameters
        return ele


class ODEsElement(StateParameterizedElement):
    """
    This is the abstract class for the creation of a ODEsElement. An ODEsElement
    is an element with states and parameters that is controlled by an ordinary
    differential equation, of the form:

    dS/dt = input - output
    """

    _num_upstream = 1
    """
    Number of upstream elements
    """

    _num_downstream = 1
    """
    Number of downstream elements
    """

    _solver_states = []
    """
    List of states used by the solver of the differential equation
    """

    _fluxes = []
    """
    This attribute contains a list of methods (one per differential equation)
    that calculate the values of the fluxes needed to solve the differential
    equations that control the element. The single functions must return the
    fluxes as a list where incoming fluxes are positive and outgoing are
    negative. Here is a list of the required outputs of the single functions:

    list(floats)
        Values of the fluxes given states, inputs, and parameters.
    float
        Minimum value of the state. Used, sometimes, by the numerical solver
        to search for the solution.
    float
        Maximum value of the state. Used, sometimes, by the numerical solver
        to search for the solution.
    list(floats)
        Values of the derivatives of the fluxes w.r.t. the states.
    """

    def __init__(self, parameters, states, approximation, id):
        """
        This is the initializer of the abstract class ODEsElement.

        Parameters
        ----------
        parameters : dict
            Parameters controlling the element. The parameters can be either
            a float (constant in time) or a numpy.ndarray of the same length
            of the input fluxes (time variant parameters).
        states : dict
            Initial states of the element. Depending on the element the states
            can be either a float or a numpy.ndarray.
        approximation : superflexpy.utils.numerical_approximation.NumericalApproximator
            Numerial method used to approximate the differential equation
        id : str
            Identifier of the element. All the elements of the framework must
            have an id.
        """

        StateParameterizedElement.__init__(self, parameters=parameters,
                                           states=states, id=id)

        self._num_app = approximation

    def set_timestep(self, dt):
        """
        This method sets the timestep used by the element.

        Parameters
        ----------
        dt : float
            Timestep
        """
        self._dt = dt

    def get_timestep(self):
        """
        This method returns the timestep used by the element.

        Returns
        -------
        float
            Timestep
        """
        return self._dt

    def define_numerical_approximation(self, approximation):
        """
        This method define the solver to use for the differential equation.

        Parameters
        ----------
        solver : superflexpy.utils.root_finder.RootFinder
            Solver used to find the root(s) of the differential equation(s).
            Child classes may implement their own solver, therefore the type
            of the solver is not enforced.
        """

        self._num_app = approximation

    def _solve_differential_equation(self, **kwargs):
        """
        This method calls the solver of the differential equation(s). When
        called, it solves the differential equation(s) for all the timesteps
        and populates self.state_array.
        """

        if len(self._solver_states) == 0:
            message = '{}the attribute _solver_states must be filled'.format(self._error_message)
            raise ValueError(message)

        self.state_array = self._num_app.solve(fun=self._fluxes,
                                               S0=self._solver_states,
                                               dt=self._dt,
                                               **self.input,
                                               **{k[len(self._prefix_parameters):]: self._parameters[k] for k in self._parameters},
                                               **kwargs)

    def __copy__(self):
        p = self._parameters  # Only the reference
        s = deepcopy(self._states)  # Create a new dictionary
        ele = self.__class__(parameters=p,
                             states=s,
                             id=self.id,
                             approximation=self._num_app)
        ele._prefix_states = self._prefix_states
        ele._prefix_parameters = self._prefix_parameters
        return ele

    def __deepcopy__(self, memo):
        p = deepcopy(self._parameters)  # Create a new dictionary
        s = deepcopy(self._states)  # Create a new dictionary
        ele = self.__class__(parameters=p,
                             states=s,
                             id=self.id,
                             approximation=self._num_app)
        ele._prefix_states = self._prefix_states
        ele._prefix_parameters = self._prefix_parameters
        return ele


class LagElement(StateParameterizedElement):
    """
    This is the abstract class for the creation of a LagElement. An LagElement
    is an element with states and parameters that distributes the incoming
    fluxes according to a weight array

    Parameters must be called:

    - 'lag-time': characteristic time of the lag. Its definition depends on the
      specific implementations of the element. It can be a scalar (it will be
      applied to all the fluxes) or a list (with length equal to the number of
      fluxes).

    States must be called:

    - lag: initial state of the lag function. If None it will be initialized
      to zeros. It can be a numpy.ndarray (it will be applied to all the fluxes)
      of a list on numpy.ndarray (with length equal to the number of fluxes).
    """

    _num_upstream = 1
    """
    Number of upstream elements
    """

    _num_downstream = 1
    """
    Number of downstream elements
    """

    def _build_weight(self, lag_time):
        """
        This method must be implemented by any child class. It calculates the
        weight array(s) based on the lag_time.

        Parameters
        ----------
        lag_time : float
            Characteristic time of the lag function.

        Returns
        -------
        list(numpy.ndarray)
            List of weight array(s).
        """

        raise NotImplementedError('The _build_weight method must be implemented')

    def set_input(self, input):
        """
        This method sets the inputs to the elements. Since the name of the
        inputs is not important, the fluxes are stored as list.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List of input fluxes.
        """

        self.input = input

    def get_output(self, solve=True):
        """
        This method returns the output of the LagElement. It applies the lag
        to all the incoming fluxes, according to the weight array(s).

        Parameters
        ----------
        solve : bool
            True if the element has to be solved (i.e. calculate the states).

        Returns
        -------
        list(numpy.ndarray)
            List of output fluxes.
        """

        if solve:

            # Create lists if we are dealing with scalars
            if isinstance(self._parameters[self._prefix_parameters + 'lag-time'], float):
                lag_time = [self._parameters[self._prefix_parameters + 'lag-time']] * len(self.input)
            elif isinstance(self._parameters[self._prefix_parameters + 'lag-time'], list):
                lag_time = self._parameters[self._prefix_parameters + 'lag-time']
            else:
                par_type = type(self._parameters[self._prefix_parameters + 'lag-time'])
                message = '{}lag_time parameter of type {}'.format(self._error_message, par_type)
                raise TypeError(message)

            if self._states[self._prefix_states + 'lag'] is None:
                lag_state = self._init_lag_state(lag_time)
            else:
                if isinstance(self._states[self._prefix_states + 'lag'], np.ndarray):
                    lag_state = [copy(self._states[self._prefix_states + 'lag'])] * len(self.input)
                elif isinstance(self._states[self._prefix_states + 'lag'], list):
                    lag_state = self._states[self._prefix_states + 'lag']
                else:
                    state_type = type(self._states[self._prefix_states + 'lag'])
                    message = '{}lag state of type {}'.format(self._error_message, state_type)
                    raise TypeError(message)

            self._weight = self._build_weight(lag_time)

            self.state_array = self._solve_lag(self._weight, lag_state, self.input)

            # Get the new lag value to restart
            final_states = self.state_array[-1, :, :]
            final_states[:, :-1] = final_states[:, 1:]
            final_states[:, -1] = 0

            self.set_states({self._prefix_states + 'lag': [final_states[i, :len(w)] for i, w in enumerate(self._weight)]})

        return [self.state_array[:, i, 0] for i in range(len(self.input))]

    def reset_states(self):
        """
        This method sets the states to the values provided to the __init__
        method. In this case, if a state was initialized as None, it will be
        set back to None.
        """

        for k in self._init_states.keys():
            k_no_prefix = k.split('_')[-1]
            self._states[self._prefix_states + k_no_prefix] = deepcopy(self._init_states[k])  # I have to isolate

    @staticmethod
    def _solve_lag(weight, lag_state, input):
        """
        This method distributes the input fluxes according to the weight array
        and the initial state.

        Parameters
        ----------
        weight : list(numpy.ndarray)
            List of weights to use
        lag_state : list(numpy.ndarray)
            List of the initial states of the lag.
        input : list(numpy.ndarray)
            List of fluxes

        Returns
        -------
        numpy.ndarray
            3D array (dimensions: number of timesteps, number of fluxes, max
            lag length) that stores all the states of the lag in time
        """

        max_length = max([len(w) for w in weight])

        output = np.zeros((len(input[0]), len(weight), max_length))  # num_ts, num_fluxes, len_lag

        for flux_num, (w, ls, i) in enumerate(zip(weight, lag_state, input)):
            for ts in range(len(input[0])):
                updated_state = ls + i[ts] * w
                output[ts, flux_num, :len(w)] = updated_state[:]
                ls = np.append(updated_state[1:], 0)

        return output

    def _init_lag_state(self, lag_time):
        """
        This method sets the initial state of the lag to arrays of proper
        length.

        Parameters
        ----------
        lag_time : list(float)
            List of lag times

        Returns
        -------
        list(numpy.ndarray)
            List of the initial states of the lag.
        """

        ini_state = []
        for i in range(len(self.input)):
            ini_state.append(np.zeros(int(np.ceil(lag_time[i]))))
        return ini_state
