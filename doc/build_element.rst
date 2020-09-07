.. TODO
.. - review the conde inserted

.. note:: Last update 26/06/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. note:: If you build your own component using SuperflexPy, you should also
          share your implementation with the community and contribute to the
          :ref:`elements_list` page to make other users aware of your
          implementation.

.. _build_element:

Expand SuperflexPy: build customized elements
=============================================

In this page we will illustrate how to create customized elements using the
SuperflexPy framework.

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

In this page we report, for brevity, only the code, without docstring. The
complete code used to generate this page is available at the path
:code:`doc/source/build_element_code.py`.

Linear reservoir
----------------

The linear reservoir is one of the simplest reservoir that can be built. The
idea is that the output flux is a linear function of the state of the
reservoir.

The element is controlled by the following differential equation

.. math::

   \frac{\textrm{d}S}{\textrm{d}t}=P-Q

with

.. math::

   Q=kS

The solution of the differential equation can be approximated using a numerical
method with the equation that, in the general case, becomes:

.. math::

   \frac{S_{t+1} - S_{t}}{\Delta t}=P - Q(S)

Several numerical methods exist to approximate the solution of the differential
equation and, usually, they differ for the state used to evaluate the fluxes:
implicit Euler, for example, uses the state at the end of the time step
(:math:`S_{t+1}`)

.. math::

   \frac{S_{t+1} - S_{t}}{\Delta t}=P - kS_{t+1}

explicit Euler uses the state at the beginning of the time step (:math:`S_t`)

.. math::

   \frac{S_{t+1} - S_{t}}{\Delta t}=P - kS_{t}

and so on for other methods.

Note that, even if for this simple case the differential equation can be solved
analytically and the solution of the numerical approximation can be found
without iteration, we will use anyway the numerical solver offered by
SuperflexPy to illustrate how to proceed in a more general case where such
option is not available.

The framework provides the class :code:`ODEsElement` that has most of the
methods required to solve the element. The class implementing the element will
inherit from this and implement only a few methods.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 1, 3, 9, 10
   :linenos:

The first method to implement is the class initializer

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 29-46
   :linenos:

The main purpose of the method (lines 9-16) is to deal with the numerical
solver used for solving the differential equation. In this case we can accept
two architectures: pure python or numba. The option selected will change the
function used to calculate the fluxes. Keep in mind that, since some operations
the python implementation of the fluxes is still used, this must be always
present.

The second method to define is the one that maps the (ordered) list of input
fluxes to a dictionary that gives a name to these fluxes.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 48, 59-60
   :linenos:

Note that the name (key) of the input flux must be the same used for the
correspondent variable in the flux functions.

The third method to implement is the one that runs the model, solving the
differential equation and returning the output flux.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 62, 73-77, 79-88
   :linenos:

The method takes, as input, the parameter solve: if :code:`False`, the state
array of the reservoir will not be calculated again, potentially producing a
different result, and the output will be computed based on the state that is
already stored. This is the desired behavior in case of post-run inspection of
the element.

Line 4 transforms the states dictionary in an ordered list, line 5 call the
built-in solver of the differential equation, line 7 updates the state of the
model to the one of the updated value, lines 9-14 call the external numerical
solver to get the values of the fluxes (note that, for this operation, the
python implementation of the fluxes is used always).

The last method(s) to implement is the one that defines the fluxes:
in this case the methods are two, one for the python implementation and one for
numba.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 90-124
   :linenos:

They are both private static methods. Their input consists of the state used to
compute the fluxes (:code:`S`), initial state (:code:`S0`, used to define the
maximum possible state for the reservoir), index to use in the arrays
(:code:`ind`, all inputs are arrays and, when solving for a single time step,
the index indicates the time step to look for), input fluxes (:code:`P`), and
parameters (:code:`k`). The output is a tuple containing three elements:

- tuple with the values of the fluxes calculated according to the state;
  positive sign for incoming fluxes, negative for outgoing;
- lower bound for the search of the state;
- upper bound for the search of the state;

The implementation for the numba solver differs in two aspects:

- the usage of the numba decorator that defines the types of the input
  variables (lines 24-25)
- the fact that the method works only for a single time step and not for the
  vectorized solution (use python method for that)

.. _build_lag:

Half-triangular lag function
----------------------------

The half-triangular lag function is a function that has the shape of a right
triangle, growing linearly until :math:`t_{\textrm{lag}}` and then zero. The
growth rate (:math:`\alpha`) is designed such as the total area of the triangle
is one.

.. math::

    & f_{\textrm{lag}}=\alpha t & \quad \textrm{for }t\leq t_{\textrm{lag}}\\
    & f_{\textrm{lag}}=0 & \quad \textrm{for }t>t_{\textrm{lag}}

SuperflexPy provides the class :code:`LagElement` that contains most of the
functionalities needed to solve a lag function. The class implementing a
customized lag function will inherit from it and implement only the necessary
methods that are needed to calculate the transformation that needs to be
applied to the incoming flux.

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

that makes use of a secondary private static method

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 162-172
   :linenos:

This method returns the value of the area of a triangle that is proportional
to the lag function, with a smaller base :code:`bin`. The
:code:`_build_weight` method, on the other hand, uses the output of this
function to calculate the weight array.

Note that this choice of using a second static method to calculate the weight
array, while being convenient, is specific to this particular case; other
implementation of the :code:`_build_weight` method are possible and welcome.

Parameterized splitter
----------------------

A splitter is an element that takes the flux coming from one element upstream
and divides it to feed multiple elements downstream. Usually, the behavior of
such an element is controlled by some parameters that define the part of the
flux that goes into a specific element.

While SuperflexPy can support infinite fluxes (e.g., for simulating transport
processes) and an infinite number of downstream elements, the simplest case
that we are presenting here has a single flux that gets split into two
downstream elements. In this example, the system needs only one parameter
(:math:`\alpha_{\textrm{split}}`) to be defined, with the downstream fluxes
that are

.. math::

   & Q_1^{\textrm{out}} = \alpha_{\textrm{split}} Q^{\textrm{in}} \\
   & Q_2^{\textrm{out}} = \left(1-\alpha_{\textrm{split}}\right) Q^{\textrm{in}}

SuperflexPy provides the class :code:`ParameterizedElement` that is designed for
all the generic elements that are controlled by some parameters but do not have
a state. The class implementing the parameterized splitter will inherit from
this and implement only some methods.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 5, 176, 177
   :linenos:

The first thing to define are two private attributes defining how many upstream
and downstream elements the splitter has; this information is used by the unit
when constructing the model structure.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 194-195
   :linenos:

After that we need to define the function that takes the inputs and the one
that calculates the outputs of the splitter.

.. literalinclude:: build_element_code.py
   :language: python
   :lines: 197, 208-211, 227-233
   :linenos:

The two methods have the same structure of the one implemented as part of the
linear reservoir example. Note that, in this case, the argument :code:`solve` of
the :code:`get_output` method is not used but it is still required to maintain
the interface consistent.
