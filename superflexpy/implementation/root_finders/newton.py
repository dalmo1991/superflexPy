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

This file contains the implementation of the Newton method for root finding. The
solution is forced to be bounded by the limits of acceptability.
"""

import numba as nb
import numpy as np

from ...utils.root_finder import RootFinder


class NewtonPython(RootFinder):
    """
    This class defines the root finder, using the Newton method. The solution
    is forced to be bounded by the limits of acceptability.
    """

    def __init__(self, tol_F=1e-8, tol_x=1e-8, iter_max=10):
        """
        This is the initializer of the class NewtonPython.

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
        super().__init__(tol_F=tol_F, tol_x=tol_x, iter_max=iter_max)
        self._name = "NewtonPython"
        self.architecture = "python"
        self._error_message = "module : superflexPy, solver : {},".format(self._name)
        self._error_message += " Error message : "

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
            - Derivative of the differential equation wrt the root
        fluxes : function
            Function to be passed to diff_eq. See specification in
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

        a_orig, b_orig = diff_eq(fluxes=fluxes, S=None, S0=S0, dt=dt, args=args, ind=ind)[1:3]

        # Swap if a_orig > b_orig
        if a_orig > b_orig:
            a_orig, b_orig = b_orig, a_orig

        a, b = a_orig, b_orig
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

        if fa * fb > 0:
            message = "{}fa and fb have the same sign: {} vs {}".format(self._error_message, fa, fb)
            raise ValueError(message)

        if need_solve:
            root = (a_orig + b_orig) / 2

            for j in range(self._iter_max):
                f, *_, df = diff_eq(fluxes=fluxes, S=root, S0=S0, dt=dt, args=args, ind=ind)

                if np.abs(f) < self._tol_F:
                    # Success
                    output = root
                    break

                if fa * f < 0:
                    fb = f
                    b = root
                else:
                    fa = f
                    a = root

                # Calculate new root
                dx = -f / df
                root = root + dx

                if np.abs(dx) < self._tol_x:
                    # Success
                    output = root
                    break

                if (root > b_orig) or (root < a_orig):
                    # We are overshooting
                    middle = (a + b) / 2

                    f_middle = diff_eq(fluxes=fluxes, S=middle, S0=S0, dt=dt, args=args, ind=ind)[0]

                    if fa * f_middle < 0:
                        b = middle
                        fb = f_middle
                        root = (a + b) / 2
                    else:
                        a = middle
                        fa = f_middle
                        root = (a + b) / 2

                if j + 1 == self._iter_max:
                    message = "{}not converged. iter_max : {}".format(self._error_message, self._iter_max)
                    raise RuntimeError(message)

            return output


class NewtonNumba(RootFinder):
    """
    This class defines the root finder, using the Newton method. The solution
    is forced to be bounded by the limits of acceptability.
    """

    def __init__(self, tol_F=1e-8, tol_x=1e-8, iter_max=10):
        """
        This is the initializer of the class NewtonNumba.

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
        super().__init__(tol_F=tol_F, tol_x=tol_x, iter_max=iter_max)
        self._name = "NewtonNumba"
        self.architecture = "numba"
        self._error_message = "module : superflexPy, solver : {},".format(self._name)
        self._error_message += " Error message : "

    @staticmethod
    @nb.jit(nopython=True)
    def solve(diff_eq, fluxes, S0, dt, ind, args, tol_F, tol_x, iter_max):
        a_orig, b_orig = diff_eq(fluxes=fluxes, S=None, S0=S0, dt=dt, args=args, ind=ind)[1:3]

        # Swap if a_orig > b_orig
        if a_orig > b_orig:
            a_orig, b_orig = b_orig, a_orig

        a, b = a_orig, b_orig
        fa = diff_eq(fluxes=fluxes, S=a, S0=S0, dt=dt, args=args, ind=ind)[0]
        fb = diff_eq(fluxes=fluxes, S=b, S0=S0, dt=dt, args=args, ind=ind)[0]

        # Check if a or b are already the solution
        need_solve = True

        if np.abs(fa) < tol_F:
            output = a
            need_solve = False
        elif np.abs(fb) < tol_F:
            output = b
            need_solve = False

        if fa * fb > 0:
            # I cannot raise exceptions with Numba
            output = np.nan
            need_solve = False

        if need_solve:
            root = (a_orig + b_orig) / 2

            for j in range(iter_max):
                f, *_, df = diff_eq(fluxes=fluxes, S=root, S0=S0, dt=dt, args=args, ind=ind)

                if np.abs(f) < tol_F:
                    # Success
                    output = root
                    break

                if fa * f < 0:
                    fb = f
                    b = root
                else:
                    fa = f
                    a = root

                # Calculate new root
                dx = -f / df
                root = root + dx

                if np.abs(dx) < tol_x:
                    # Success
                    output = root
                    break

                if (root > b_orig) or (root < a_orig):
                    # We are overshooting
                    middle = (a + b) / 2

                    f_middle = diff_eq(fluxes=fluxes, S=middle, S0=S0, dt=dt, args=args, ind=ind)[0]

                    if fa * f_middle < 0:
                        b = middle
                        fb = f_middle
                        root = (a + b) / 2
                    else:
                        a = middle
                        fa = f_middle
                        root = (a + b) / 2

                if j + 1 == iter_max:
                    # I cannot raise exceptions with Numba
                    output = np.nan

            return output
