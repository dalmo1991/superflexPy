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

This file contains the implementation of a trivial solver to use when the
algebraic equation to solve is explicit and, therefore does not require
iteration (e.g., with Explicit Euler or Runge Kutta).
"""


import numba as nb
from ...utils.root_finder import RootFinder


class ExplicitPython(RootFinder):
    """
    This class defined a root finder to be used when the algebraic equation is
    explicit.
    """

    def __init__(self):
        """
        This is the initializer of the ExplicitRootFinderPython class. As the
        root finder it not iterative, no parameters defining the convergence are
        needed.
        """

        super().__init__(tol_F=None,
                         tol_x=None,
                         iter_max=None)

        self._name = 'ExplicitRootFinderPython'
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

        return - diff_eq(fluxes=fluxes, S=0, S0=S0, dt=dt, args=args, ind=ind)[0]


class ExplicitNumba(RootFinder):
    """
    This class defined a root finder to be used when the algebraic equation is
    explicit.
    """

    def __init__(self):
        """
        This is the initializer of the ExplicitRootFinderNumba class. As the
        root finder it not iterative, no parameters defining the convergence are
        needed.
        """

        super().__init__(tol_F=None,
                         tol_x=None,
                         iter_max=None)

        self._name = 'ExplicitRootFinderPython'
        self.architecture = 'python'
        self._error_message = 'module : superflexPy, solver : {},'.format(self._name)
        self._error_message += ' Error message : '

    @staticmethod
    @nb.jit(nopython=True)
    def solve(diff_eq, fluxes, S0, dt, ind, args, tol_F, tol_x, iter_max):

        return - diff_eq(fluxes=fluxes, S=0, S0=S0, dt=dt, args=args, ind=ind)[0]
