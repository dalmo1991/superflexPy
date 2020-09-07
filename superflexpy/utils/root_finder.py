"""
Copyright 2020 Marco Dal Molin et al.

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
DESIGNED BY: Marco Dal Molin

This file contains the implementation of the base class for the root finder in
case of elements governed by ODEs
"""


class RootFinder():
    """
    This is the abstract class for the creation of a RootFinder. It defines how
    the solver of the differential equation must be implemented.
    """

    architecture = None
    """
    Implementation required to increase the performance (e.g. numba)
    """

    def __init__(self, tol_F=1e-8, tol_x=1e-8, iter_max=10):
        """
        The constructor of the subclass must accept the parameters of the
        solver.

        Parameters
        ----------
        tol_F : float
            Tolerance on the y axis (distance from 0) that stops the solver
        tol_x : float
            Tolerance on the x axis (distance between two roots) that stops
            the solver
        iter_max : int
            Maximum number of iteration of the solver. After this value it
            raises a runtime error
        """

        self._tol_F = tol_F
        self._tol_x = tol_x
        self._iter_max = iter_max
        self._name = 'Solver'

    def get_settings(self):
        """
        This method returns the settings of the root finder.

        Returns
        -------
        float
            Function tollerance (tol_F)
        float
            X tollerance (tol_x)
        int
            Maximum number of iterations (iter_max)
        """

        return (
            self._tol_F,
            self._tol_x,
            self._iter_max,
        )

    def __repr__(self):
        str = 'Module: superflexPy\nClass: {}\n'.format(self._name)
        str += 'Parameters:\n'
        str += '\ttol_F = {}\n'.format(self._tol_F)
        str += '\ttol_x = {}\n'.format(self._tol_x)
        str += '\titer_max = {}'.format(self._iter_max)

        return str

    def solve(self, *args, **kwargs):
        """
        To be implemented by any child class. This method finds the root of the
        numerical approximation of the differential equation. It can operate
        over the whole time series.
        """

        raise NotImplementedError('The method solve must be implemented')
