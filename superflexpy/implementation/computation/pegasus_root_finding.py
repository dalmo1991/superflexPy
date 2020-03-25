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
DESIGNED BY: Dmitri Kavetski, Marco Dal Molin

This file contains the implementation of the Pegasus method for root finding,
as it is implemented in Superflex.

References
----------
Dowell, M. & Jarratt, P. BIT (1972) 12: 503. https://doi.org/10.1007/BF01932959
"""

import numpy as np
import numba as nb
import inspect
from ...utils.root_finder import RootFinder


class PegasusPython(RootFinder):
    """
    This class defines the root finder, using the Pegasus method. The
    implementation follows the one used in Superflex.
    """

    def __init__(self, tol_F=1e-8, tol_x=1e-8, iter_max=10):
        """
        This is the initializer of the class PegasusPython.

        Parameters
        ----------
        tol_F : float
            Tollerance on the y axis (distance from 0) that stops the solver
        tol_x : float
            Tollerance on the x axis (distance between two roots) that stops
            the solver
        iter_max : int
            Maximum number of iteration of the solver. After this value it
            raises a runtime error
        """
        super().__init__(tol_F=tol_F,
                         tol_x=tol_x,
                         iter_max=iter_max)
        self._name = 'PegasusPython'
        self.architecture = 'python'
        self._error_message = 'module : superflexPy, solver : {},'.format(self._name)
        self._error_message += ' Error message : '

    def solve(self, fun, **kwargs):
        """
        This method calculated the root of the input function. The solver
        iterates over the provided vectors.

        Parameters
        ----------
        fun : function or list(function)
            Function or list of functions to be solved. The function must
            accept the inputs in the followig order:
            - root. If None, the function must initialize the root
            - **kwargs (the initial state must be called S0)
            It must return three float values:
            - Value of the function given the root and the kwargs
            - Lower x boundary for the search
            - Upper x boundary for the search
        **kwargs :
            Arguments of fun

        Returns
        -------
        numpy.ndarray
            Array of roots. It is a 2D array with dimensions (#timesteps,
            #functions)
        """

        if 'S0' not in kwargs:
            message = '{}\'S0\' must be in **kwargs'.format(self._error_message)
            raise KeyError(message)

        # Divide the parameters of fun between arrays (time variant) and float
        vectors = []
        scalars = []

        for k in kwargs:
            if k == 'S0':
                continue
            if isinstance(kwargs[k], np.ndarray):
                vectors.append(k)
            elif isinstance(kwargs[k], float):
                scalars.append(k)
            else:
                message = '{}parameter of type {}'.format(self._error_message, type(kwargs[k]))
                raise TypeError(message)

        # Construct the output array
        output = []

        if not isinstance(fun, list):
            fun = [fun]

        if not isinstance(kwargs['S0'], list):
            kwargs['S0'] = [kwargs['S0']]

        for f, S0 in zip(fun, kwargs['S0']):
            output.append(self._solve(fun=f,
                                      S0=S0,
                                      kwargs=kwargs,
                                      vectors=vectors,
                                      scalars=scalars))

        return np.array(output).reshape((-1, len(fun)))

    def _solve(self, fun, S0, kwargs, vectors, scalars):

        output = []

        fun_pars = list(inspect.signature(fun).parameters)

        # Loop in time
        for i in range(kwargs[vectors[0]].shape[0]):
            # Create the **kwargs for the timestep
            loc_kwargs = {}
            for k in kwargs:
                if (k in vectors) and (k in fun_pars):
                    loc_kwargs[k] = float(kwargs[k][i])
                elif (k in scalars) and (k in fun_pars):
                    loc_kwargs[k] = kwargs[k]
                else:
                    continue

            # Initialize the function
            a, b = fun(S=None, S0=S0, **loc_kwargs)[1:]
            fa = fun(S=a, S0=S0, **loc_kwargs)[0]
            fb = fun(S=b, S0=S0, **loc_kwargs)[0]

            # Check if a or b are already the solution
            need_solve = True

            if np.abs(fa) < self._tol_F:
                output.append(a)
                need_solve = False
            elif np.abs(fb) < self._tol_F:
                output.append(b)
                need_solve = False

            if fa * fb > 0 and need_solve:
                message = '{}fa and fb have the same sign: {} vs {}'.format(self._error_message, fa, fb)
                raise ValueError(message)

            if need_solve:

                # Iterate the solver
                for j in range(self._iter_max):

                    xmin = min(a, b)
                    xmax = max(a, b)

                    dx = -(fa / (fb - fa)) * (b - a)
                    root = a + dx

                    if root < xmin:
                        root = xmin
                    elif root > xmax:
                        root = xmax

                    dx = root - a

                    f_root = fun(root, S0=S0, **loc_kwargs)[0]

                    if f_root * fa < 0:
                        b = a
                        fb = fa
                    else:
                        fFac = fa / (fa + f_root)
                        fb = fb * fFac

                    a = root
                    fa = f_root

                    if np.abs(f_root) < self._tol_F:
                        output.append(root)
                        break

                    if np.abs(a - b) < self._tol_x:
                        output.append(root)
                        break

                    if j + 1 == self._iter_max:
                        message = '{}not converged. iter_max : {}'.format(self._error_message, self._iter_max)
                        raise RuntimeError(message)

            S0 = output[i]

        return np.array(output)


class PegasusNumba(RootFinder):
    """
    This class defines the root finder, using the Pegasus method. The
    implementation follows the one used in Superflex. This version is
    implemented using Numba.
    """

    def __init__(self, tol_F=1e-8, tol_x=1e-8, iter_max=10):
        """
        This is the initializer of the class PegasusNumba.

        Parameters
        ----------
        tol_F : float
            Tollerance on the y axis (distance from 0) that stops the solver
        tol_x : float
            Tollerance on the x axis (distance between two roots) that stops
            the solver
        iter_max : int
            Maximum number of iteration of the solver. After this value it
            raises a runtime error
        """
        super().__init__(tol_F=tol_F,
                         tol_x=tol_x,
                         iter_max=iter_max)
        self._name = 'PegasusNumba'
        self.architecture = 'numba'
        self._error_message = 'module : superflexPy, solver : {},'.format(self._name)
        self._error_message += ' Error message : '

    def solve(self, fun, **kwargs):
        """
        This method calculates the root of the input function. The solver
        iterates over the provided vectors.

        Parameters
        ----------
        fun : function or list(function)
            Function or list of functions to be solved. The function must be
            "numba decorated" and accept the inputs in the followig order:
            - root: if None, the function must initialize the root. The root
                    must be called S and be of type float64.
            - S0: initial state of type float64
            - ind: index of the array to look for (type int32)
            - **kwargs: inputs and parameters. All of type float64[:]
            It must return three float values:
            - Value of the function given the root and the kwargs
            - Lower x boundary for the search
            - Upper x boundary for the search
        **kwargs :
            Arguments of fun

        Returns
        -------
        numpy.ndarray
            Array of roots. It is a 2D array with dimensions (#timesteps,
            #functions)
        """

        if 'S0' not in kwargs:
            message = '{}\'S0\' must be in **kwargs'.format(self._error_message)
            raise KeyError(message)

        if not isinstance(fun, list):
            fun = [fun]

        if not isinstance(kwargs['S0'], list):
            kwargs['S0'] = [kwargs['S0']]

        # Construct the output array
        output = []

        for f, S0 in zip(fun, kwargs['S0']):
            # Get the arguments of the function -> this line will give error if the
            # function  is not numba because of the "py_func"
            arg_names = list(inspect.signature(f.py_func).parameters)
            # arg_names = list(inspect.signature(f).parameters)

            # Collect the args for the function
            args = []
            for name in arg_names:
                if name in ['S0', 'S', 'ind']:
                    continue
                if isinstance(kwargs[name], float):
                    args.append(np.array([kwargs[name]]))
                elif isinstance(kwargs[name], np.ndarray):
                    args.append(kwargs[name])
                else:
                    message = '{}parameter of type {}'.format(self._error_message, type(kwargs[name]))
                    raise TypeError(message)

            # Find the length
            num_timestep = 0
            floats = []
            for i, a in enumerate(args):
                if a.shape[0] != 1:
                    if num_timestep == 0:
                        num_timestep = a.shape[0]
                    elif a.shape[0] != num_timestep:
                        message = '{}some elements have different length: {} vs. {}'.format(self._error_message, a.shape[0], num_timestep)
                        raise ValueError(message)
                else:
                    floats.append(i)

            if num_timestep == 0:
                num_timestep = 1

            # Extend the float
            if num_timestep != 1:
                for i in floats:
                    args[i] = args[i] * np.ones(num_timestep)  # np.broadcast_to(args[i], (num_timestep))

            args = tuple(args)

            output.append(self._solve(f, S0, self._tol_F, self._tol_x,
                                      self._iter_max, *args))

        return np.array(output).reshape((-1, len(fun)))

    @staticmethod
    @nb.jit(nopython=True)
    def _solve(fun, S0, tol_F, tol_x, iter_max, *args):

        num_ts = args[0].shape[0]
        output = np.zeros(num_ts)

        # Loop in time
        for i in range(num_ts):
            a, b = fun(None, S0, i, *args)[1:]
            fa = fun(a, S0, i, *args)[0]
            fb = fun(b, S0, i, *args)[0]

            # Check if a or b are already the solution
            need_solve = True

            if np.abs(fa) < tol_F:
                output[i] = a
                need_solve = False
            elif np.abs(fb) < tol_F:
                output[i] = b
                need_solve = False

            # We avoid to raise value error if fa and fb have the same
            # sign because I don't know if it works with numba

            if need_solve:

                # Iterate the solver
                for j in range(iter_max):

                    if a > b:
                        xmin = b
                        xmax = a
                    else:
                        xmin = a
                        xmax = b

                    dx = -(fa / (fb - fa)) * (b - a)
                    root = a + dx

                    if root < xmin:
                        root = xmin
                    elif root > xmax:
                        root = xmax

                    dx = root - a

                    f_root = fun(root, S0, i, *args)[0]

                    if f_root * fa < 0:
                        b = a
                        fb = fa
                    else:
                        fFac = fa / (fa + f_root)
                        fb = fb * fFac

                    a = root
                    fa = f_root

                    if np.abs(f_root) < tol_F:
                        output[i] = root
                        break

                    if np.abs(a - b) < tol_x:
                        output[i] = root
                        break

                    if j + 1 == iter_max:
                        output[i] = np.nan  # I should raise an error here

            S0 = output[i]

        return output
