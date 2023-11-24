"""
This code contains a quick example to implement the nomerical approximator
and the root finder. The only purpose of this code is being put in the
documentation.
"""

from ...superflexpy.utils.numerical_approximator import NumericalApproximator
from ...superflexpy.utils.root_finder import RootFinder


class CustomRootFinder(RootFinder):
    def solve(self, diff_eq_fun, fluxes_fun, S0, dt, ind, args):
        # Some code here

        return root


class CustomNumericalApproximator(NumericalApproximator):
    @staticmethod
    def _get_fluxes(fluxes_fun, S, S0, args, dt):
        # Some code here

        return fluxes

    @staticmethod
    def _differential_equation(fluxes_fun, S, S0, dt, args, ind):
        # Some code here

        return [diff_eq, min_val, max_val, d_diff_eq]


class CustomODESolver:
    # The class may implement other methods

    def solve(self, fluxes_fun, S0, dt, args):
        # Some code here

        return states

    def get_fluxes(self, fluxes_fun, S, S0, dt, args):
        # Some code here

        return fluxes
