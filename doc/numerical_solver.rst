.. note:: Last update 08/10/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _numerical_solver:

Numerical routines for solving ODEs
===================================

:ref:`reservoirs` are the most common elements in conceptual hyrdological
models. Reservoirs are controlled by one (or more) ordinary differential
equations (ODEs) of the form

.. math::
   \frac{\textrm{d}\mathbf{S}}{\textrm{d}t}=\mathbf{I}(\mathbf{\theta}, t)-\mathbf{O}(S, \mathbf{\theta}, t)

Such differential equations are usually difficult/impossible to solve
analytically, therefore, numerical approximations are employed.

Many robust numerical approximations (e.g. Implicit Euler) require an iterative
root-finding procedure at each time step.

The solution of the ODE, therefore, can be seen as a two-step approach:

1. Construct the equations defining the a numerical approximation of the ODEs
2. Solve the numerical approximation

This can be done in SuperflexPy using two components:
:code:`NumericalApproximator` and :code:`RootFinder`. The first uses the fluxes
from the reservoir element to construct numerical approximation of the ODE, the
second finds, numerically, the root of these equations.

SuperflexPy provides two built-in numerical approximators (implicit and explicit
Euler) and a root finder (Pegasus method). Other algorithms can be used
extending the  classes :code:`NumericalApproximator` or :code:`RootFinder`.

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
:code:`S` the state that solve the ODE, :code:`S0` is the initial state,
:code:`dt` is the time step, :code:`args` is a list of additional arguments used
by the functions in :code:`fluxes`, and :code:`ind` is the index of the input
arrays to use.

The first method (:code:`_get_fluxes`) is responsible for calculating the fluxes
after the ODE has been solved and operates with a vector of states. The second
method (:code:`_differential_equation`) calculates the approximation of the ODE,
returning the value of the numerical approximation of the  differential
equation given a value of :code:`S` and the minimum and maximum boundary for its
search. This method is designed to be interfaced with the root finder.

To understand better how these methods work, please have a look at the
implementation of :code:`ImplicitEuler` and :code:`ExplicitEuler`.

Root finder
-----------

A customized root finder can implemented by extending the class
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

To understand better how this method works, please see the implementation of
:code:`Pegasus`.

Computational efficiency with Numpy and Numba
---------------------------------------------

Conceptual hydrological models are often used in computationally demanding
contexts, such as parameter calibration and uncertainty quantification, which
require many model runs (thousands or even millions). Computational efficiency
is therefore an important requirement of SuperflexPy.

Computational efficiency is not the greatest strength of pure Python, but
libraries like Numpy and Numba can help in pushing the performance close to
Fortran or C.

Numpy provides highly efficient arrays that can be transformed with C-time
performance, as long as vector operations (i.e. elementwise operations between
arrays) are run. Numba provides a “just-in-time compiler” that can be applied to
a normal Python method to compile, at runtime, its content to machine code
that interacts efficiently with NumPy arrays. This operation is extremely
effective when solving ODEs where the method loops through a vector to perform
some element-wise operations.

For this reason we provide a Numba-optimized version of
:code:`NumericalApproximator` and :code:`RootFinder`, which enable efficient
solution of ODEs describing the reservoir elements.

The figure shows the results of a benchmark that compares the execution times
of pure Python vs. the Numba implementation, in relation to the length of
the time series (panel a) and the number of model runs (panel b). The plot
clearly shows the tradeoff between compilation time (which is zero for Python
and around 2 seconds for Numba) versus run time, where Numba is 30 times faster
than Python. This means that the choice of the implementation to use, which can
be done simply using a different :code:`NumericalApproximator` implementation,
may depend on the application. For example, a single run of 1000 time steps of
the  :ref:`hymod` model, solved using the implicit Euler numerical solver takes
0.11 seconds with Python and 1.85 with Numba. In contrast, if the same model is
run 100 times (e.g., as part of a calibration) the Python version takes 11.75
seconds while the Numba version takes 2.35 seconds.

.. image:: pics/numerical_solver/bench_all.png
   :align: center
