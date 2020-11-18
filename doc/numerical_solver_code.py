"""
This code contains a quick example to implement the nomerical approximator
and the root finder. The only purpose of this code is being put in the
documentation.
"""

from ...superflexpy.utils.numerical_approximator import NumericalApproximator
from ...superflexpy.utils.root_finder import RootFinder


class CustomRootFinder(RootFinder):

    def solve(self, diff_eq, fluxes, S0, dt, ind, args):

        # Some code here

        return root


class CustomNumericalApproximator(NumericalApproximator):

    @staticmethod
    def _get_fluxes(fluxes, S, S0, args):

        # Some code here

        return fluxes

    @staticmethod
    def _differential_equation(fluxes, S, S0, dt, args, ind):

        # Some code here

        return [diff_eq, min_val, max_val]
