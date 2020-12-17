.. note:: Last update 18/11/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _numerical_solver:

Numerical routines for solving ODEs
===================================

:ref:`reservoirs` are the most common elements in conceptual hydrological
models. Reservoirs are controlled by one (or more) ordinary differential
equations (ODEs) of the form

.. math::
   \frac{\textrm{d}\mathbf{S}}{\textrm{d}t}=\mathbf{I}(\mathbf{\theta}, t)-\mathbf{O}(\mathbf{S}, \mathbf{\theta}, t)

and associated initial conditions.

Such differential equations are usually difficult or impossible to solve
analytically, therefore, numerical approximations are employed.

Many robust numerical approximations (e.g. implicit Euler) require an iterative
root-finding procedure at each time step.

Therefore, the current implementation of SuperflexPy conceptualizes the solution
of the ODE as a two-step procedure:

1. Construct the discrete-time equations defining the numerical approximation of
   the ODEs
2. Solve the numerical approximation

These steps can be performed using two SuperflexPy components:
:code:`NumericalApproximator` and :code:`RootFinder`.

SuperflexPy provides two built-in numerical approximators (implicit and explicit
Euler) and a root finder (Pegasus method).

Other ODE solution algorithms, e.g. Runge-Kutta, can be accommodated
by extending the classes :code:`NumericalApproximator` and/or
:code:`RootFinder`. Even more generally, ODE solvers from external libraries
could be used within SuperflexPy by incorporating them in a class that respects
the interface expected by the :code:`NumericalApproximator`.

The following sections describe the standard approach to create customized
numerical approximators and root finders.

Numerical approximator
----------------------

A customized numerical approximator can be implemented by extending the class
:code:`NumericalApproximator` and implementing two methods: :code:`_get_fluxes`
and :code:`_differential_equation`.

.. literalinclude:: numerical_solver_code.py
   :language: python
   :lines: 20-34
   :linenos:

where :code:`fluxes` is a list of functions used to calculate the fluxes,
:code:`S` is the state that solves the ODE, :code:`S0` is the initial state,
:code:`dt` is the time step, :code:`args` is a list of additional arguments used
by the functions in :code:`fluxes`, and :code:`ind` is the index of the input
arrays to use.

The method :code:`_get_fluxes` is responsible for calculating the fluxes after
the ODE has been solved and operates with a vector of states.

The method :code:`_differential_equation` calculates the approximation of the
ODE, returning the value of the numerical approximation of the  differential
equation given a value of :code:`S` and the minimum and maximum boundary for the
search of the solution. This method is designed to be interfaced with the root
finder.

For further details, please see the implementation of :code:`ImplicitEuler` and
:code:`ExplicitEuler`.

Root finder
-----------

A customized root finder can implemented by extending the class
:code:`RootFinder` implementing the method :code:`solve`.

.. literalinclude:: numerical_solver_code.py
   :language: python
   :lines: 11-17
   :linenos:

where :code:`diff_eq` is a function that calculates the value of the
approximated ODE, :code:`fluxes` is a list of functions used to calculate
the fluxes, :code:`S0` is the initial state, :code:`dt` is the time step,
:code:`args` is a list of additional arguments used by the functions in
:code:`fluxes`, and :code:`ind` is the index of the input arrays to use.

The method :code:`solve` is responsible for finding the numerical solution of
the approximated ODE.

To understand better how this method works, please see the implementation of
:code:`Pegasus`.

Computational efficiency with Numpy and Numba
---------------------------------------------

Conceptual hydrological models are often used in computationally demanding
contexts, such as parameter calibration and uncertainty quantification, which
require many model runs (thousands or even millions). Computational efficiency
is therefore an important requirement of SuperflexPy.

Computational efficiency is not the greatest strength of pure Python, but
libraries like Numpy and Numba can help in pushing the performance closer to
traditionally fast languages such as Fortran and C.

Numpy provides highly efficient arrays for vectorized operations (i.e.
elementwise operations between arrays). Numba provides a “just-in-time compiler”
that can be used to compile (at runtime) a normal Python method to machine code
that interacts efficiently with Numpy arrays. The combined use of Numpy and
Numba is extremely effective when solving ODEs, where the method loops through a
vector to perform elementwise operations.

For this reason we provide Numba-optimized versions of
:code:`NumericalApproximator` and :code:`RootFinder`, which enable efficient
solution of ODEs describing the reservoir elements.

The figure below compares the execution times of pure Python vs. the Numba
implementation, as a function of the length of the time series (upper panel) and
the number of model runs (lower panel).

The plot clearly shows the tradeoff between compilation time (which is zero for
Python and around 2 seconds for Numba) versus run time (where Numba is 30 times
faster than Python). For example, a single run of 1000 time steps of the
:ref:`hymod` model solved using the implicit Euler numerical solver takes 0.11
seconds with Python and 1.85 with Numba. In contrast, if the same model is run
100 times (e.g., as part of a calibration) the Python version takes 11.75
seconds while the Numba version takes 2.35 seconds.

.. image:: pics/numerical_solver/bench_all.png
   :align: center

The SuperflexPy user can choose between the available
:code:`NumericalApproximator` implementations (which offer pure Python and Numba
implementations of the Implicit Euler and Pegasus methods), or build their own
implementations.