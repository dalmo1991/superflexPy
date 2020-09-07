.. note:: Last update 04/09/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _numerical_solver:

Numerical routines for solving ODEs
===================================

:ref:`reservoirs` are among the most common elements in conceptual hyrdological
models. While their dynamic changes, reservoirs are still controlled by one (or
more) ordinary differential equation (ODE) of the form

.. math::
   \frac{\textrm{d}S}{\textrm{d}t}=\mathbf{I}(\mathbf{\theta}, t)-\mathbf{O}(S, \mathbf{\theta}, t)

The analytical solution of such differential equation is almost always
impossible to obtain and, therefore, a numerical approximation has to be
constructed and solved.

In most of the cases, when a robust numerical approximation is used (e.g.
Implicit Euler), the solution of the numerical approximation (i.e. finding a
value of the state :math:`S` that solves the algebraic equation) requires an
iterative procedure, since an algebraic solution cannot be defined.

The solution of the ODE, therefore, can be seen as a two-steps approach:

1. Find a numerical approximation of the ODE
2. Solve such numerical approximation

This can be done in SuperflexPy using two components:
:code:`NumericalApproximator` and :code:`RootFinder`. The first uses the fluxes
from the reservoir element to construct a numerical approximation of the ODE,
the second finds, numerically, the root of such approximation.

SuperflexPy provides already two numerical approximators (implicit and explicit
Euler) and a root finder (which uses the Pegasus method). Other algorithms can
be used extending the classes :code:`NumericalApproximator` and
:code:`RootFinder`.

Numerical approximator
----------------------

The implementation of a customized numerical approximator can be done extending
the class :code:`NumericalApproximator` and implementing two methods:
:code:`_get_fluxes` and :code:`_differential_equation`.

.. literalinclude:: numerical_solver_code.py
   :language: python
   :lines: 20-34
   :linenos:

where :code:`fluxes` is a list of functions used to calculate the fluxes,
:code:`S` is an array of states that solve the ODE for the different time
steps, :code:`S0` is the initial state, :code:`dt` is the time step,
:code:`args` is a list of additional arguments used by the functions in
:code:`fluxes`, and :code:`ind` is the index of the input arrays to use.

The first method (:code:`_get_fluxes`) is responsible for calculating the fluxes
after the ODE has been solved and operates with a vector of states. The second
method (:code:`_differential_equation`) calculates the approximation of the ODE
and it is designed to be interfaced to the root finder, returning the value of
the differential equation and the minimum and maximum boundary for the search of
the root.

To understand better how these methods work, please have a look at the
implementation of :code:`ImplicitEuler` and :code:`ExplicitEuler`.

Root finder
-----------

The implementation of a root finder can be done extending the class
:code:`RootFinder` implementing the method :code:`solve`.

.. literalinclude:: numerical_solver_code.py
   :language: python
   :lines: 11-17
   :linenos:

where :code:`dif_eq` is a function that calculates the value of the
approximated ODE, :code:`fluxes` is a list of functions used to calculate
the fluxes, :code:`S0` is the initial state, :code:`dt` is the time step,
:code:`args` is a list of additional arguments used by the functions in
:code:`fluxes`, and :code:`ind` is the index of the input arrays to use.

The method :code:`solve` is responsible for finding the numerical solution of
the approximated ODE.

To understand better how this method works, please have a look at the
implementation of :code:`Pegasus`.

Computational efficiency with Numpy and Numba
---------------------------------------------

Conceptual hydrological models are often associated to computationally demanding
tasks, such as parameter calibration and uncertainty quantification, which
require multiple model runs (even millions). Computational efficiency is
therefore an important requirement of a SuperflexPy.

Computational efficiency is not the greatest strength of pure Python but
libraries like Numpy and Numba can help in pushing the performance close to
Fortran or C.

Numpy provides highly efficient arrays that can be transformed with C-time
performance, as long as vector operations (i.e. elementwise operations between
arrays) are run; Numba provides a “just-in-time compiler” that can be applied to
a normal Python method to compile, at runtime, its content to machine code
that interacts efficiently with NumPy arrays. This operation is extremely
effective when solving ODEs where the method loops through a vector to perform
some element-wise operations.

For this reason we provide a Numba-optimized version of the
:code:`NumericalApproximator` and of the :code:`RootFinder` that enables to
solve ODEs efficiently.

The figure shows the results of a benchmark that compares the execution times
of the pure Python vs. the Numba implementation, in relation to the length of
the time series (panel a) and to the number of model runs (panel b). The plots
clearly show the tradeoff between compile time (which is zero for Python and
around 2 seconds for Numba) and run time, where Numba is 30 times faster than
Python. This means that the choice of the implementation to use, which can be
done simply using a different :code:`NumericalApproximator` implementation, may
depend on the application: a single run of the :ref:`hymod` model, with the
implicit Euler numerical solver and a time series of 1000 time steps takes 0.11
seconds with Python and 1.85 with Numba while, if the same model is run 100
times (for a calibration, for example) the Numba version takes 2.35 seconds
while the Python version 11.75 seconds.

.. image:: pics/numerical_solver/bench_all.png
   :align: center
