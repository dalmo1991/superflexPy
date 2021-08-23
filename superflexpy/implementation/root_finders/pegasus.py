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

This file contains the implementation of the Pegasus method for root finding,
as it is implemented in Superflex.

References
----------
Dowell, M. & Jarratt, P. BIT (1972) 12: 503. https://doi.org/10.1007/BF01932959
"""

import numpy as np
import numba as nb
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

    def solve(self, diff_eq, fluxes, S0, dt, ind, args):
        """
        This method calculated the root of the input function.

        Parameters
        ----------
        diff_eq : function
            Function be solved. The function must accept the following inputs:
            - fluxes : function used to calculate the fluxes given parameters
                       and state
            - S : proposed root. If None, the function must initialize the root
            - S0 : state at the beginning of the time step
            - dt : time step
            - kwargs : other parameters needed by diff_eq
            It must return three float values:
            - Value of the function given the root and the kwargs
            - Lower x boundary for the search
            - Upper x boundary for the search
        fluxes : function
            Function to be passed to diff_eq. See specificatio in
            superflexpy.utils.numerical_approximator
        S0 : float
            state at the beginning of the time step
        dt : float
            time step
        kwargs : dict(str: float)
            parameters needed by diff_eq

        Returns
        -------
        float
            Root of the function
        """

        a, b = diff_eq(fluxes=fluxes, S=None, S0=S0, dt=dt, args=args, ind=ind)[1:3]
        fa = diff_eq(fluxes=fluxes, S=a, S0=S0, dt=dt, args=args, ind=ind)[0]
        fb = diff_eq(fluxes=fluxes, S=b, S0=S0, dt=dt, args=args, ind=ind)[0]

        # Check if a or b are already the solution
        need_solve = True

        if np.abs(fa) < self._tol_F:
            output = a
            need_solve = False
        elif np.abs(fb) < self._tol_F:
            output = b
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

                f_root = diff_eq(fluxes=fluxes, S=root, S0=S0, dt=dt, args=args, ind=ind)[0]

                if f_root * fa < 0:
                    b = a
                    fb = fa
                else:
                    fFac = fa / (fa + f_root)
                    fb = fb * fFac

                a = root
                fa = f_root

                if np.abs(f_root) < self._tol_F:
                    output = root
                    break

                if np.abs(a - b) < self._tol_x:
                    output = root
                    break

                if j + 1 == self._iter_max:
                    message = '{}not converged. iter_max : {}'.format(self._error_message, self._iter_max)
                    raise RuntimeError(message)

        return output


class PegasusNumba(RootFinder):
    """
    This class defines the root finder, using the Pegasus method. The
    implementation follows the one used in Superflex.
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

    @staticmethod
    @nb.jit(nopython=True)
    def solve(diff_eq, fluxes, S0, dt, ind, args, tol_F, tol_x, iter_max):

        a, b = diff_eq(fluxes=fluxes, S=None, S0=S0, dt=dt, ind=ind, args=args)[1:3]
        fa = diff_eq(fluxes=fluxes, S=a, S0=S0, dt=dt, ind=ind, args=args)[0]
        fb = diff_eq(fluxes=fluxes, S=b, S0=S0, dt=dt, ind=ind, args=args)[0]

        # Check if a or b are already the solution
        need_solve = True

        if np.abs(fa) < tol_F:
            output = a
            need_solve = False
        elif np.abs(fb) < tol_F:
            output = b
            need_solve = False

        if fa * fb > 0 and need_solve:
            # Raise doesn't work with Numba
            output = np.nan
            need_solve = False

        if need_solve:

            # Iterate the solver
            for j in range(iter_max):

                xmin = min(a, b)
                xmax = max(a, b)

                dx = -(fa / (fb - fa)) * (b - a)
                root = a + dx

                if root < xmin:
                    root = xmin
                elif root > xmax:
                    root = xmax

                dx = root - a

                f_root = diff_eq(fluxes=fluxes, S=root, S0=S0, dt=dt, ind=ind, args=args)[0]

                if f_root * fa < 0:
                    b = a
                    fb = fa
                else:
                    fFac = fa / (fa + f_root)
                    fb = fb * fFac

                a = root
                fa = f_root

                if np.abs(f_root) < tol_F:
                    output = root
                    break

                if np.abs(a - b) < tol_x:
                    output = root
                    break

                if j + 1 == iter_max:
                    # Raise doesn't work with Numba
                    output = np.nan

        return output
