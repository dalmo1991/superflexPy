.. TODO
.. - review the conde inserted

.. note:: Last update 08/10/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. note:: If you build your own component using SuperflexPy, we would appreciate
          if share your implementation with the community (see
          :ref:`contribute`). Remember to contribute also to the
          :ref:`elements_list` page to make other users aware of your
          implementation.

.. _build_element:

Expand SuperflexPy: build customized elements
=============================================

This page illustrates how to create customized elements using the SuperflexPy
framework.

The examples include three elements:

- Linear reservoir
- Half-triangular lag function
- Parameterized splitter

The elements presented here are as simple as possible, since the focus is in
explaining how the framework works, rather than providing code to use in a
practical application. To understand deeper how to exploit all the
functionalities of SuperflexPy, please have a look at the elements that have
been already implemented (importing path
:code:`superflexpy.implementation.elements`).

.. _linear_reservoir:

Linear reservoir
----------------

.. image:: pics/build_element/reservoir.png
   :align: center

The linear reservoir is the simplest type of dynamic reservoir. Its output flux
is a linear function of the state of the reservoir.

The reservoir is controlled by the following differential equation

.. math::

   \frac{\textrm{d}S}{\textrm{d}t}=P-Q

with

.. math::

   Q=kS

Note that, even if for this simple case the differential equation can be solved
analytically and the solution of the numerical approximation can be found
without iteration, we will use anyway the numerical approximator offered by
SuperflexPy (see :ref:`numerical_solver`) to illustrate how to proceed in a
more general case where analytical solutions are not available.

The framework provides the class :code:`ODEsElement` that has most of the
methods required to solve the element. The class implementing the reservoir will
inherit from :code:`ODEsElement` and implement only a few methods that
specialize its behavior.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 1, 3, 9, 10
   :linenos:

The first method to implement is the class initializer :code:`__init__`

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 29-46
   :linenos:

The main purpose of the method (lines 9-16) is to deal with the numerical
solver. In this case we can accept two architectures: pure Python or numba. The
option selected will change the function used to calculate the fluxes. Keep in
mind that, since some methods may still need the Python implementation of the
fluxes is still used, this must be always implemented.

The second method to define is :code:`set_input`, which maps the (ordered) list
of input fluxes to a dictionary that gives a name to these fluxes.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 48, 59-60
   :linenos:

Note that the key of the dictionary used to identify the input flux must be the
same used for the corresponding variable in the flux functions.

The third method to implement is :code:`get_output`, which runs the model,
solving the differential equation and returning the output flux.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 62, 73-77, 79-88
   :linenos:

The method takes, as input, the parameter :code:`solve`: if :code:`False`, the
state array of the reservoir will not be calculated again. The outputs will,
therefore, be computed based on the state that is already stored from a previous
run of the reservoir. This is the desired behavior in case of post-run
inspection, when we want to get the output of the reservoir without solving it
again.

Line 4 transforms the states dictionary to an ordered list. Line 5 calls the
built-in solver of the differential equation. Line 7 updates the state of the
model to the one of the updated value. Lines 9-14 call the external numerical
approximator to get the values of the fluxes (note that, for this operation, the
Python implementation of the fluxes is used always).

The last methods to implement are :code:`_fluxes_function_python` (pure Python)
and :code:`_fluxes_function_numba` (numba optimized), which are responsible for
calculating the fluxes of the reservoir.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 90-124
   :linenos:

:code:`_fluxes_function_python` and :code:`_fluxes_function_numba` are both
private static methods. Their input consists of the state used to
compute the fluxes (:code:`S`), initial state (:code:`S0`, used to define the
maximum possible state for the reservoir), index to use in the arrays
(:code:`ind`, all inputs are arrays and, when solving for a single time step,
the index indicates the time step to look for), input fluxes (:code:`P`), and
parameters (:code:`k`). The output is a tuple containing three elements:

- tuple with the values of the fluxes calculated according to the state;
  positive sign for incoming fluxes (e.g. precipitation, :code:`P`), negative
  for outgoing  (e.g. streamflow, :code:`- k * S`);
- lower bound for the search of the state;
- upper bound for the search of the state;

The implementation for the numba solver differs in two aspects:

- the usage of the numba decorator that defines the types of the input
  variables (lines 24-25)
- the method works only for a single time step and not for the vectorized
  solution since, for this operation, the Python implementation is fast enough

.. _build_lag:

Half-triangular lag function
----------------------------

.. image:: pics/build_element/lag.png
   :align: center


The half-triangular lag function is a function that has the shape of a right
triangle, growing linearly until :math:`t_{\textrm{lag}}` and then zero. The
growth rate :math:`\alpha` is calculated such as the total area of the triangle
is one.

.. math::

    & f_{\textrm{lag}}=\alpha t & \quad \textrm{for }t\leq t_{\textrm{lag}}\\
    & f_{\textrm{lag}}=0 & \quad \textrm{for }t>t_{\textrm{lag}}

SuperflexPy provides the class :code:`LagElement` that contains most of the
functionalities needed to calculate the output of a lag function. The class
implementing a customized lag function will inherit from :code:`LagElement` and
implement only the methods needed to apply the transformation to the incoming
flux.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 2, 128, 129
   :linenos:

The only method to implement is the private method used to calculate the
:code:`weight` array, that is used to distribute the incoming flux.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 146-160
   :linenos:

The method :code:`_build_weight` makes use of a secondary private static method

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 162-172
   :linenos:

This method returns the value of the area :math:`A_i` of a triangle that is
proportional to the lag function, with a smaller base :code:`bin`. The
:code:`_build_weight` method, on the other hand, uses the output of this
function (:math:`A_i` and :math:`A_{i-1}`) to calculate the weight array
:math:`W_i`.

Note that other implementations of the :code:`_build_weight` method (without
using auxiliary methods) are possible.

Parameterized splitter
----------------------

A splitter is an element that takes the flux from an upstream element and
divides it to feed multiple downstream elements. Usually, the behavior of
such an element is controlled by parameters that define the portion of the
flux that goes into a specific element.

The simple case that we are presenting here has a single flux that gets split
into two downstream elements. In this example, the system needs only one
parameter (:math:`\alpha_{\textrm{split}}`) to be defined, with the downstream
fluxes that are

.. math::

   & Q_1^{\textrm{out}} = \alpha_{\textrm{split}} Q^{\textrm{in}} \\
   & Q_2^{\textrm{out}} = \left(1-\alpha_{\textrm{split}}\right) Q^{\textrm{in}}

SuperflexPy provides the class :code:`ParameterizedElement` that can be extended
to implement all the elements that are controlled by parameters but do not have
a state. The class implementing the parameterized splitter will inherit from
:code:`ParameterizedElement` and implement only some methods.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 5, 176, 177
   :linenos:

First, we have to define two private attributes defining how many upstream and
downstream elements the splitter has; this information is used by the unit when
constructing the model structure.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 194-195
   :linenos:

After that we need to define the method that takes the inputs and the method
that calculates the outputs.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 197, 208-211, 227-233
   :linenos:

The two methods have the same structure of the ones implemented as part of the
:ref:`linear_reservoir` example. Note that, in this case, the argument
:code:`solve` of :code:`get_output` is not used, but it is still required to
maintain a consistent interface.
