.. note:: Last update 04/05/2021

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _numerical_solver:

Numerical implementation
========================

Numerical routines for solving ODEs
-----------------------------------

:ref:`reservoirs` are the most common elements in conceptual hydrological
models. Reservoirs are controlled by one (or more) ordinary differential
equations (ODEs) of the form

.. math::
   \frac{\textrm{d}\mathbf{S}}{\textrm{d}t}=\mathbf{I}(\mathbf{\theta}, t)-\mathbf{O}(\mathbf{S}, \mathbf{\theta}, t)

and associated initial conditions.

Such differential equations are usually difficult or impossible to solve
analytically, therefore, numerical approximations are employed. These numerical
approximations take the form of time stepping schemes.

Moreover, many robust numerical approximations (e.g. implicit Euler) require an iterative
root-finding procedure at each time step.

The current implementation of SuperflexPy conceptualizes the solution
of the ODE as a two-step procedure:

1. Construct the discrete-time equations defining the numerical approximation of
   the ODEs at a single time step
2. Solve the numerical approximation for the storage(s)

These steps can be performed using two SuperflexPy components:
:code:`NumericalApproximator` and :code:`RootFinder`.

SuperflexPy provides two built-in numerical approximators (implicit and explicit
Euler) and a root finder (Pegasus method). These methods are best suited when
dealing with smooth flux functions. If a user wants to experiment with
discontinuous flux functions, other ODE solution algorithms should be
considered.

Other ODE solution algorithms, e.g. Runge-Kutta, can be
implemented by  extending the classes :code:`NumericalApproximator` and/or
:code:`RootFinder`. Even more generally, ODE solvers from external libraries
can be used within SuperflexPy by incorporating them in a class that respects
the interface expected by the :code:`NumericalApproximator`.

The following sections describe the standard approach to create customized
numerical approximators and root finders.

Numerical approximator
......................

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
the ODE has been solved. This method operates with a vector of states.

The method :code:`_differential_equation` calculates the approximation of the
ODE. It returns the residual of the approximated mass balance equations for a
given value of :code:`S` and the minimum and maximum bounds for the
search of the solution. This method is designed to be interfaced with the root
finder.

For further details, please see the implementation of :code:`ImplicitEuler` and
:code:`ExplicitEuler`.

Root finder
...........

A customized root finder can constructed by extending the class
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
the approximated ODE. In case of failure, the method should either raise a
:code:`RuntimeError` (Python implementation) or return :code:`numpy.nan` (this
is not ideal but it is the suggested workaround because Numba does not support
exceptions handling).

To understand better how the method :code:`solve` works, please see the
implementation of the Pegasus root finder that is currently used in the SuperflexPy
applications.

Sequential solution of the elements
-----------------------------------

The SuperflexPy framework is built on a model representation that maps to a
directional acyclic graph. Model elements are solved sequentially from upstream
to downstream, with the output from each element being used as input to
its downstream elements.

When fixed-step solvers are used (e.g. implicit Euler), this
"one-element-at-a-time" strategy is equivalent to applying the same (fixed-step)
solver to the entire ODE system simultaneously.

When solvers with internal substepping are used, the
"one-element-at-a-time" strategy does introduces additional approximation error.
This additional approximation error is due to treating all fluxes as constant
over the time step, whereas in reality fluxes vary within
the time step. In most practical applications, this "uniform flux"
approximation is already applied to the meteorological inputs (precipitation and
PET), hence applying it to internal fluxes does not represent a large additional
approximation.

Computational efficiency with Numpy and Numba
---------------------------------------------

Conceptual hydrological models are often used in computationally demanding
contexts, such as parameter calibration and uncertainty quantification, which
require many model runs (thousands or even millions). Computational efficiency
is therefore an important requirement of SuperflexPy.

Computational efficiency is a potential limitation of pure Python, but
libraries like Numpy and Numba can help in pushing the performance closer to
traditionally fast languages such as Fortran and C.

Numpy provides highly efficient arrays for vectorized operations (i.e.
elementwise operations between arrays). Numba provides a “just-in-time compiler”
that can be used to compile (at runtime) a normal Python method to machine code
that operates efficiently with Numpy arrays. The combined use of Numpy and
Numba is extremely effective when solving ODEs using time stepping schemes, where the method loops through a
vector to perform elementwise operations.

SuperflexPy includes Numba-optimized versions of
:code:`NumericalApproximator` and :code:`RootFinder`, which enable efficient
solution of ODEs describing the reservoir elements.

The figure below compares the execution times of pure Python vs. the Numba
implementation, as a function of the length of the time series (upper panel) and
the number of model runs (lower panel). Simulations were run on a laptop (single
thread), using the :ref:`hymod` model, solved using the implicit Euler numerical solver.

The plot clearly shows the tradeoff between compilation time (which is zero for
Python and around 2 seconds for Numba) versus run time (where Numba is 30 times
faster than Python). For example, a single run of 1000 time steps takes 0.11
seconds with Python and 1.85 seconds with Numba. In contrast, if the same model is run
100 times (e.g., as part of a calibration) the Python version takes 11.75
seconds while the Numba version takes 2.35 seconds.

.. note:: The objective of these plots is to give an idea of time that is topically
          required to perform common modelling applications (e.g., calibration) with SuperflexPy,
          to show the impact of the Numba implementation, and to explain the
          tradeoff between compilation and run time. The results do not
          have to be considered as accurate measurements of the performance
          of SuperflexPy (i.e., rigorous benchmarking).

.. image:: pics/numerical_solver/bench_all.png
   :align: center

The green line "net numba" in the lower panel express the run time of the Numba
implementation, i.e., excluding the compilation time.