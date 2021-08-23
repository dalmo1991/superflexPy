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

This file contains the implementation of the base class for the numerical
approximator to be used to solve the elements governed by ODEs.
"""
import numpy as np
import numba as nb
import inspect


class NumericalApproximator():
    """
    This is the abstract class for the creation of a NumericalApproximator. It
    defines how the approximator of the differential equation must be
    implemented to fit in the framework
    """

    architecture = None
    """
    Defines if the element is implemented using some pre-compiled libraries
    (e.g. numba)
    """

    _error_message = ''
    """
    String to use when displaying errors. It should contain general information
    about the class
    """

    def __init__(self, root_finder):
        """
        The constructor of the subclass must accept the parameters of the
        approximator.

        Parameters
        ----------
        root_finder : superflexpy.utils.root_finder.RootFinder
            Solver used to find the root(s) of the differential equation(s).
         """

        self._root_finder = root_finder

    def solve(self, fun, S0, **kwargs):
        """
        This method solves an approximation of the ODE.

        Parameters
        ----------
        fun : list(function)
            List of functions to calculate the fluxes of the ODEs. One equation
            for ODE. The function must accept:

            - State, called S, used to evaluate the fluxes

            - Initial state of the element, called S0, used to calculate
              the mainimum and maximum possible state of the reservoir

            - Other parameters (**kwargs) needed to calculate the fluxes

            The function must return:

            - list of fluxes with positive sign if incoming and negative if
              outgoing

            - minimum possible value of the state

            - maximum possible value of the state
        S0 : list(float)
            Initial states used for the ODEs. One value per fun
        **kwargs
            Additional arguments needed by fun. It must also contain dt.

        Returns
        -------
        numpy.ndarray
            Array of solutions of the ODEs. It is a 2D array with dimensions
            (#timesteps, #functions)
        """

        # Divide between scalar and vector parameters
        scalars = []
        vectors = []

        for k in kwargs:
            if isinstance(kwargs[k], np.ndarray):
                vectors.append(k)
            elif isinstance(kwargs[k], float):
                scalars.append(k)
            else:
                message = '{}the parameter {} is of type {}'.format(self._error_message,
                                                                    k, type(kwargs[k]))
                raise TypeError(message)

        if len(vectors) == 0:
            num_ts = 1
        else:
            num_ts = len(kwargs[vectors[0]])

        if 'dt' not in kwargs:
            message = '{}\'dt\' must be in kwargs'
            raise KeyError(message)

        # Transform dt in vector since we always need it
        if 'dt' not in vectors:
            kwargs['dt'] = np.array([kwargs['dt']] * num_ts)

        # Construct the output array
        output = []

        # Set architecture
        if self.architecture == 'python':
            self._solve = self._solve_python
        elif self.architecture == 'numba':
            self._solve = self._solve_numba

        for f, s_zero in zip(fun, S0):
            # Find which parameters the function needs
            if self.architecture == 'python':
                fun_pars = list(inspect.signature(f).parameters)
            elif self.architecture == 'numba':
                # fun_pars = list(inspect.signature(f).parameters)
                fun_pars = list(inspect.signature(f.py_func).parameters)

            args = []
            for arg in fun_pars:
                if arg in ['S', 'S0', 'ind']:
                    continue
                elif arg == 'dt':
                    args.append(kwargs[arg])  # We want to treat it differently
                elif arg in vectors:
                    args.append(kwargs[arg])
                elif arg in scalars:
                    args.append(np.array([kwargs[arg]] * num_ts))

            args = tuple(args)

            root_settings = self._root_finder.get_settings()

            output.append(self._solve(root_finder=self._root_finder.solve,  # Passing just the method
                                      diff_eq=self._differential_equation,
                                      fun=f,
                                      S0=s_zero,
                                      dt=kwargs['dt'],
                                      num_ts=num_ts,
                                      args=args,
                                      root_settings=root_settings))

        return np.array(output).reshape((-1, len(fun)))

    def get_fluxes(self, fluxes, S, S0, **kwargs):

        output = []
        for i, (f, s_zero) in enumerate(zip(fluxes, S0)):

            # The function is only python. No need of numba in get_fluxes
            fun_pars = list(inspect.signature(f).parameters)

            args = []

            for arg in fun_pars:
                if arg in ['S', 'S0', 'ind']:
                    continue
                else:
                    args.append(kwargs[arg])

            args = tuple(args)

            output.append(self._get_fluxes(fluxes=f,
                                           S=S[:, i],  # S is a 2d np array
                                           S0=s_zero,
                                           args=args,
                                           dt=kwargs['dt']))

        return output

    @staticmethod
    def _solve_python(root_finder, diff_eq, fun, S0, dt, num_ts, args, root_settings):  # here args are all vectors of the same lenght

        # Note: root_settings not used. Here only to have uniform interface
        output = np.zeros(num_ts)

        for i in range(num_ts):

            # Call the root finder
            root = root_finder(diff_eq=diff_eq,
                               fluxes=fun,
                               S0=S0,
                               dt=dt,
                               ind=i,
                               args=args)

            output[i] = root
            S0 = output[i]

        return output

    @staticmethod
    @nb.jit(nopython=True)
    def _solve_numba(root_finder, diff_eq, fun, S0, dt, num_ts, args, root_settings):  # here args are all vectors of the same lenght

        output = np.zeros(num_ts)

        for i in range(num_ts):

            # Call the root finder
            root = root_finder(diff_eq=diff_eq,
                               fluxes=fun,
                               S0=S0,
                               dt=dt,
                               ind=i,
                               args=args,
                               tol_F=root_settings[0],
                               tol_x=root_settings[1],
                               iter_max=root_settings[2])

            output[i] = root
            S0 = output[i]

        return output

    @staticmethod
    def _differential_equation(fluxes, S, S0, dt, args):
        raise NotImplementedError('The method _differential_equation must be implemented')

    @staticmethod
    def _get_fluxes(fluxes, S, S0, args, dt):
        raise NotImplementedError('The method _get_fluxes must be implemented')
