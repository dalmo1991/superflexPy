.. TODO:
.. - check if the inspect are implemented correctly

.. note:: Last update 26/06/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _demo:

How to build a model with SuperflexPy
=====================================

In this page we will build a complete semi-distributed conceptual model with
SuperflexPy, showing:

1. how the elements are initialized, configured, and run
2. how to use the model at any level of complexity, from single element to
   multiple nodes.

All the models developed in this section are made available also as runnable
examples (see :ref:`examples`).

Examples of existing models are given in the pages :ref:`popular_models` and
:ref:`case_studies`.

Importing SuperflexPy
---------------------

Assuming that SuperflexPy is already installed (see :ref:`installation_label`
guide), the elements needed to build the model are imported from the SuperflexPy
package. For this demo, this is done with the following lines

.. literalinclude:: demo_code.py
   :language: python
   :lines: 8-14
   :linenos:

Lines 1-2 import the two element that we will use (a reservoir and a lag
function), lines 3-4 import the numerical solver used to solve the
differential equation of the reservoir, lines 5-7 import the components of
SuperflexPy needed to make the model spatially distributed.

A complete list of the elements already implemented in SuperflexPy, including
the equations used and the import path, is available at the :ref:`elements_list`
page. If the desired element is not available it can be built following the
instructions given in the :ref:`build_element` page.

Simplest lumped model structure with single element
---------------------------------------------------

.. image:: pics/demo/SingleReservoir_scheme.png
   :align: center

The single-element model is composed by a single reservoir governed by the
following differential equation

.. math::
   \frac{\textrm{d}S}{\textrm{d}t}=P-Q

where :math:`S` is the state of the reservoir, :math:`P` is the precipitation
input, and :math:`Q` is the outflow, defined by the equation:

.. math::
   Q = kS^\alpha

where :math:`k` and :math:`\alpha` are parameters of the element. For
simplicity, evapotranspiration is not considered in this demo.

The first step is to initialize the numerical approximator (see
:ref:`numerical_solver`). In this case, we will use the Python implementation of
the implicit Euler (numerical approximator) and the Pegasus algorithm (root
finder). This can be done with the following code, where the default settings
of the solver are used (refer to the solver docstring).

.. literalinclude:: demo_code.py
   :language: python
   :lines: 20, 18, 21
   :linenos:

After that, the element can be initialized

.. literalinclude:: demo_code.py
   :language: python
   :lines: 24-29
   :linenos:

During initialization, parameters (line 2) and initial state (line 3) are
defined, together with the numerical approximator and the identifier (the
identifier must be unique and cannot contain the character :code:`_`, see
:ref:`identifier`).

After initialization, the time step used to solve the differential equation and
the inputs of the element must be specified.

.. literalinclude:: demo_code.py
   :language: python
   :lines: 31, 38
   :linenos:

Precipitation is a numpy array containing the precipitation time series. Note
that the length of the simulation (i.e., number of time steps to run the model)
is automatically set equal to the length of the input arrays.

At this point, the element can be run, calling the method get_output

.. literalinclude:: demo_code.py
   :language: python
   :lines: 41
   :linenos:

The method will run the element for all the time steps, solving the differential
equation and returning a list containing all output arrays of the element (in
this specific case there is only one output, :math:`Q`).

After running, the state of the reservoir (for all the time steps) is saved in
the :code:`state_array` attribute of the element and can be inspected

.. literalinclude:: demo_code.py
   :language: python
   :lines: 42
   :linenos:

the :code:`state_array` is a 2D array with the number of rows equal to the
number of time steps, and the number of columns equal to the number of states.
The order of states is defined in the docstring of the element.

With the following code we can create a plot showing the outputs of the
simulation.

.. literalinclude:: demo_code.py
   :language: python
   :lines: 45, 46, 48, 50, 51
   :linenos:

.. image:: pics/demo/SingleReservoir.png
   :align: center

Note that the :code:`get_output` method also sets the element states to their value at
the final time step (in this case 8.98). This is done because it may be
necessary to continue the simulation afterwards (e.g. real time applications
with new inputs coming in time). As a consequence, if the method is called
again, it will use this value as initial state instead of the one defined at
initialization. The states of the model can be reset calling the
:code:`reset_states` method.

.. literalinclude:: demo_code.py
   :language: python
   :lines: 66
   :linenos:

Lumped model structure with 2 elements
--------------------------------------

.. image:: pics/demo/SingleUnit_scheme.png
   :align: center

We now move from a single-element to multiple elements connected in a unit.
For simplicity, we limit the complexity to two elements; more complex
configurations can be found in the :ref:`popular_models` page.

The unit structure comprises a reservoir that feeds a lag function. The lag
function convolves the incoming flux using the function

.. math::
   Q_{\textrm{out}}=Q_{\textrm{in}} \left(\frac{t}{t_{\textrm{lag}}}\right)^
   {\frac{5}{2}} \qquad \textrm{for }t<t_{\textrm{lag}}

and its behavior is controlled by parameter :math:`t_{\textrm{lag}}`.

First, we initialize the two elements that compose the unit structure

.. literalinclude:: demo_code.py
   :language: python
   :lines: 24-30, 69-73
   :linenos:

Note that the initial state of the lag function has been set to :code:`None`
(line 10); in this case the element will initialize the state to an arrays of
zeros of the proper length, depending on the value of :math:`t_{\textrm{lag}}`
(in this specific case, 3).

Next, we initialize the unit that connect the elements, defining the model
structure

.. literalinclude:: demo_code.py
   :language: python
   :lines: 76-79
   :linenos:

Line 2 defines the unit structure; it is a 2D list where the inner level sets the
elements belonging to each layer an the outer level lists the layers.

After initialization, time step and inputs must be defined

.. literalinclude:: demo_code.py
   :language: python
   :lines: 81, 83
   :linenos:

The unit sets the time step of all the elements that contains to the provided
value and transfers the inputs to the first element (the reservoir, in this
example).

After that, the unit can be run

.. literalinclude:: demo_code.py
   :language: python
   :lines: 86
   :linenos:

The unit will call the :code:`get_output` method of all its elements, from
upstream to downstream, set the inputs of the downstream elements to the output
of their respective upstream elements, and return the output of the last
element.

The outputs and the states of the internal elements can be retrieved after
running the model

.. literalinclude:: demo_code.py
   :language: python
   :lines: 89-90
   :linenos:

Note that in line 2 we pass to the function :code:`get_output` of the
reservoir the argument :code:`solve=False` in order to avoid to re-run the
element.

The plot shows the output of the simulation.

.. image:: pics/demo/SingleUnit.png
   :align: center

The elements of the unit can be re-set to their initial state

.. literalinclude:: demo_code.py
   :language: python
   :lines: 126
   :linenos:

.. _demo_mult_nodes:

Simple semi-distributed model
-----------------------------

.. image:: pics/demo/SingleNode_scheme.png
   :align: center

This model is intended to represent a spatially semi-distributed configuration.
In this case, a node can be used to represent a catchment that is composed by
different areas that react differently to the same inputs. We may have 70% of
the catchment that can be represented with the structure described in the
previous section and 30% that can be described simply by a single reservoir.

This configuration can be simulated with SuperflexPy creating a node that contains
multiple units.

First, we initialize the two units and the elements
composing them, as done in the previous sections.

.. literalinclude:: demo_code.py
   :language: python
   :lines: 24-30, 69-74, 76-80, 130-133
   :linenos:

Note that, once the elements are added to a unit, they become independent (see
:ref:`unit`), meaning that any change to the reservoir contained in
:code:`unit-1` does not affect the reservoir in :code:`unit-2`.

At this point, the node can be initialized, putting together the two units

.. literalinclude:: demo_code.py
   :language: python
   :lines: 136-141
   :linenos:

Line 2 contains the list of the units that belong to the node, line 3 gives
their weight (i.e. the portion of the node outflow coming from this unit). The
representative area of the node (line 4) will be used, in case, by the network.

Next, we define time step and inputs

.. literalinclude:: demo_code.py
   :language: python
   :lines: 143-144
   :linenos:

The same time step will be specified in the elements composing all the units of
the node, and the inputs will be passed to all the units of the node.

We can now run the node and collect its output

.. literalinclude:: demo_code.py
   :language: python
   :lines: 147
   :linenos:

The node will call the :code:`get_output` method of all the units and aggregate
their outputs using the weights.

The outputs of the single units, as well as the states and fluxes of the
elements composing them, can be retrieved

.. literalinclude:: demo_code.py
   :language: python
   :lines: 149-150
   :linenos:

The plot shows the output of the simulation.

.. image:: pics/demo/SingleNode.png
   :align: center

All elements within the node can be re-set to their initial states

.. literalinclude:: demo_code.py
   :language: python
   :lines: 178
   :linenos:

Semi-distributed model with multiple nodes
------------------------------------------

.. image:: pics/demo/Network_scheme.png
   :align: center

A watershed can be composed by several catchments (nodes) connected in a network
that have different inputs but share areas with the same hydrological behavior
(defined by units). This semi-distributed configuration can be simulated with
SuperflexPy creating a network that contains multiple nodes.

First, we initialize the nodes composing it.

.. literalinclude:: demo_code.py
   :language: python
   :lines: 24-30, 69-74, 76-80, 130-134, 136-142, 182-194
   :linenos:

:code:`node-1` and :code:`node-2` contain both the units but with different
proportions; :code:`node-3` contains only :code:`unit-2`. When units are added
to a catchment the states of the elements belonging to them remain independent
while the parameters stay linked, meaning that the change of a parameter in
:code:`unit-1` in :code:`node-1` is applied also in :code:`unit-1` in
:code:`node-2`. Different behavior can be achieved setting the parameter
:code:`shared_parameters` equal to :code:`False` when initializing the nodes.

At this point, the network can be initialized

.. literalinclude:: demo_code.py
   :language: python
   :lines: 197-204
   :linenos:

Line 2 lists the nodes belonging to the network. Lines 4-6 define the
connectivity of the network; this is done using a dictionary with the keys given
by the node identifiers and values given by the single downstream node. The
most downstream node has value :code:`None`.

The inputs are catchment-specific and must be provided to each node.

.. literalinclude:: demo_code.py
   :language: python
   :lines: 206-208
   :linenos:

The time step is defined at the network level.

.. literalinclude:: demo_code.py
   :language: python
   :lines: 210
   :linenos:

We can now run the network and get the output values

.. literalinclude:: demo_code.py
   :language: python
   :lines: 212
   :linenos:

The network runs the nodes from upstream to downstream, collects their outputs,
and routes them to the outlet. The output of the network is a dictionary the
keys given by the node identifiers and values given by the list of output
fluxes. It is also possible to retrieve the internals of the nodes.

.. literalinclude:: demo_code.py
   :language: python
   :lines: 214-216
   :linenos:

The plot shows the results of the simulation.

.. image:: pics/demo/Network.png
   :align: center
