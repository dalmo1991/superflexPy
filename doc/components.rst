.. note:: Last update 18/11/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _components:

Organization of SuperflexPy
===========================

SuperflexPy is designed to operate at multiple levels of complexity, from a
single reservoir to a complex river network.

All SuperflexPy components, namely elements, units, nodes, network, are designed
to operate alone or within other components. For this reason, all components
have methods that enable the execution of basic functionality (e.g. parameter
handling) at all levels.

We will first describe each component in specific detail and, then, highlight
some :ref:`generalities` that apply to all the components.

Elements
--------

Elements represent the basic level of the SuperflexPy's architecture.
Conceptually, SuperflexPy uses the following elements: reservoirs, lag
functions, and connections. Elements can be used to represent a complete model
structure, or combined together to form one or more :ref:`unit`.

Depending on their type, the conceptual elements can have parameters or
states, can handle multiple fluxes as input or as output, can be designed to
operate with one or more elements upstream or downstream, can be controlled by
differential equations, or by a convolution operations.

Programmatically, the conceptual elements can be implemented extending the
following classes:

- :code:`BaseElement`: for elements without states and parameters;

- :code:`StateElement`: for elements with states but without parameters;

- :code:`ParameterizedElement`: for elements with parameters but without states;

- :code:`StateParameterizedElement`: for elements with states and parameters.

To facilitate the building of the conceptual elements, SuperflexPy provides some
specific classes that implement already most of the code needed to solve
reservoirs, lag functions, and connections. The next sections focus on these
elements.

.. _reservoirs:

Reservoirs
**********

A reservoir is a storage element described by the differential equation

.. math::
   \frac{\textrm{d}\mathbf{S}}{\textrm{d}t}=\mathbf{I}(\mathbf{\theta}, t)-\mathbf{O}(\mathbf{S}, \mathbf{\theta}, t)

where :math:`\mathbf{S}` is the internal states of the reservoir,
:math:`\mathbf{I}` represents the sum of all input fluxes (usually independent
from the states), :math:`\mathbf{O}` represents the sum of all output fluxes,
and :math:`\mathbf{\theta}` represents the parameters that control the behavior
of the reservoir.

SuperflexPy provides the class :code:`ODEsElement` that contains all the logic
needed to solve an element controlled by a differential equation. The user needs
only to specify the equations defining input and output fluxes.

The differential equation is solved numerically; the choice of approximation
(e.g. the implicit Euler scheme) is made by the user when initializing the
reservoir.

SuperflexPy provides several "numerical approximators", including implicit or
explicit Euler. The user can either employ the numerical routines provided by
the framework, or implement the interface necessary to use an external solver
(e.g. from scipy), which may be needed when the numerical problem becomes more
complex (e.g. coupled differential equations). For more information about the
numerical solver refer to the page :ref:`numerical_solver`.

Lag functions
*************

A lag function is an element that applies a delay to the incoming faxes;
mathematically, the lag function applies a convolution to the incoming fluxes.
Here, this result is usually achieved distributing the fluxes at each time step
into the following time steps, according to a weight array.

SuperflexPy provides the class :code:`LagElement` that implements all the
methods needed to represent a lag function, leaving to user only to define the
weight array.

.. _connections:

Connections
***********

Connection elements are needed to link together different elements, when
building a unit. For example, if an element has several elements downstream, its
fluxes need to be split using a :code:`Splitter`; on the other hand, when the
outflow of several elements is collected by a single element, a :code:`Junction`
element is used.

SuperflexPy provides several types of connection elements. These elements are
designed to operate with an arbitrarily number of fluxes and upstream/downstream
elements (depending on the element type).

Splitter
........

.. image:: pics/components/splitter.png
   :align: center

A :code:`Splitter` is an element that takes the outputs of a single upstream
element and distributes them to several downstream elements.

The behavior of a splitter in SuperflexPy is controlled by two matrices:
direction and weight. The "direction" controls which of the input fluxes each
downstream element receives, and in which order. The "weight" defines the
proportion of each of the input fluxes that goes into each the downstream
element.

Looking at the picture, S receives 3 input fluxes, which are indexed based on
their order: red (index 0), black (index 1), and blue (index 2). E2 receives the
black flux as first input, and the blue flux as second input, and does not
receive the third flux. E3 receives the blue flux as first input, the red flux
as second input, and does not receive the black flux. This information is
represented by the direction matrix D, which is represented as follows:

.. math::
   D=
   \begin{pmatrix}
   1 & 2 & \textrm{None}\\
   2 & 0 & \textrm{None}
   \end{pmatrix}

The direction matrix is a 2D matrix that has as many columns as the number of
fluxes and as many rows as the number of downstream elements. The row index
refers to the downstream element (in this case row 1 refers to E2, and row 2 to
E3), whereas the column index refers to the input flux to the element, which
should be in the order the element is expected to receive the inputs (e.g. if an
element is supposed to receive black and red flux as input in a prescribed
order, the inputs should respect this order).

The value of the matrix element can be an integer referring to the index of the
input flux to S, or :code:`None`, if an input flux to S does not reach a
downstream element.

As such, the direction matrix can be used to select the fluxes and change the
order in which they are transmitted to downstream elements.

The red flux is taken entirely by element E3, the black flux is taken entirely
by element E2, and the blue flux is split at 30% to E2 and 70% to E3. This
information is represented by the weight matrix W, which is represented as
follows:

.. math::
   W=
   \begin{pmatrix}
   0 & 1.0 & 0.3\\
   1.0 & 0 & 0.7
   \end{pmatrix}

The weight matrix has the same dimensionality of the direction matrix. The row
index refers to the downstream element, in the same order as the D matrix,
whereas the column index refers to the input flux to S. The value of the matrix
elements represents the weight of each input flux to S in the downstream
element. In the example, the first downstream element (first row of the matrix
W) receives 0% of the first (red) flux, 100% of the second (black) flux, and 30%
of the third (blue) flux.

Note that, as a quick check, the columns of the weight matrix should sum up to 1
to ensure conservation of mass.

Junction
........

.. image:: pics/components/junction.png
   :align: center

A :code:`Junction` is an element that takes the outputs of several upstream
elements and directs them into a single downstream element.

The behavior of a junction in SuperflexPy is controlled by direction matrix that
defines how the incoming fluxes have to be aggregated (summed) to feed the
downstream element.

Looking at the picture, E3 receives 3 input fluxes, which are indexed based on
their order: red (index 0), black (index 1), and blue (index 2). The red flux
comes from both upstream elements (index 0 and 1, respectively); the black flux
comes only from E1 (index 1); the blue flux comes only from E2 (index 2). This
information is represented by the direction matrix D, which is represented as
follows:

.. math::
   D=
   \begin{pmatrix}
   0 & 1\\
   1 & \textrm{None}\\
   \textrm{None} & 0
   \end{pmatrix}

The direction matrix is a 2D matrix that has as many rows as the number of
fluxes and as many columns as number of upstream elements. The row index refers
to the flux (in this case row 1 refers to the red flux, row 2 to the black, and
row 3 to the blue), whereas the column index refers to the upstream element
input flux to the element (in this case column 1 refers to E1, column 2 do E2).

The value of the matrix element can be an integer referring to the index of the
input flux to J coming from the specific element, or :code:`None`, if an input
flux to J does not come from the upstream element.


Linker
......

.. image:: pics/components/linker.png
   :align: center

A :code:`Linker` is an element that can be used to connect multiple elements
upstream to multiple elements downstream without mixing fluxes.

Its usefulness is due to the fact that in SuperflexPy the structure of the unit
is defined as an ordered list of elements. This means that if we want to connect
the first element of a layer with the second element of the following layer
(e.g., E1 with E4, in the example above) we have to put an additional layer in
between that contains a linker that direct the fluxes to the proper downstream
element. Further details on the organization of the units in layers are
presented in section :ref:`unit`.

Transparent
...........

.. image:: pics/components/transparent.png
   :align: center

A transparent element is an element that returns, as output, the same fluxes
that it takes as input. It is needed to fill gaps in the structure defined in
the unit (refer to :ref:`unit`).

.. _unit:

Unit
----

.. image:: pics/components/unit.png
   :align: center

A unit is a collection of multiple connected elements. The unit can be used
either alone, when intended to represent a lumped catchment model, or as part
of a :ref:`components_node`, to create a semi-distributed model.

Elements are *copied* into the unit: this means that an element that belongs
to a unit is completely independent from the originally defined element and
from any other copy of the same element in other units. Therefore, changes to
the state or to the parameters of an element inside a unit will not affect any
element outside the unit. The code below lustrates the implications of this
behavior:

.. literalinclude:: components_code.py
   :language: python
   :lines: 1-8
   :linenos:

In the code, element :code:`e1` is included in units :code:`u1` and :code:`u2`.
In lines 6-8 the value of parameter :code:`p1` of element :code:`e1` is changed
at the element level and at the unit level. Since elements are *copied* into a
unit, these changes apply to different elements (in the sense of different
Python objects in memory).

As shown in the picture, elements are organized as a succession of layers,
from left (upstream) to right (downstream).

The first and last layers must contain only a single element, since the
inputs of the unit are transferred to the first element and the outputs of the
unit are taken from the last element.

The order of elements inside each layer defines how they are connected: the
first element of a layer (e.g. E2 in the picture) will transfer its outputs to
the first element of the downstream layer (e.g. E4); the second element of a
layer (e.g. E3) will transfer its outputs to the second element of the
downstream layer (e.g. T), and so on.

When the output of an element is split between multiple downstream elements
(e.g. E1) an additional intermediate layer with a splitter is needed: in the
example, the splitter S has two downstream elements (E2 and E3); the framework
will route the first group of outputs of the splitter to E2 and the second group
of outputs to E3.

Whenever there is a gap in the structure, a transparent element should be used
to fill the gap. In the example, the output of E3 is aggregated with the output
of E4; since these elements belong to different layers, making this connection
directly would create a gap in Layer 3. Such problem is solved specifying a
transparent element in Layer 3, parallel to E4.

Since the unit must have a single element in the last layer, the outputs of E4
and T must be collected using a Junction.

Each element is aware of its expected number of upstream and downstream
elements. For example, a reservoir must have an upstream element and a
downstream element, a splitter must have a single upstream element and
potentially multiple downstream elements, and so on. A unit is valid only if all
layers connect to each other using the expected number of elements. In the
example, Layer 1 must have two downstream elements that is consistent with the
configuration of Layer 2.

For more information on how to define a unit structure in SuperflexPy refer to
the page :ref:`popular_models`, where the framework is used to reproduce some
existing lumped models.

.. _components_node:

Node
----

.. image:: pics/components/node.png
   :align: center

A node is a collection of multiple units assumed to operate in parallel. In the
context of semi-distributed models, the node represents a single catchment and
the units represent multiple landscape elements (areas) within the catchment.
The node can be run either alone or as part of a bigger
:ref:`components_network`.

The default behavior of the nodes is that parameters are shared between elements
of the same unit, even if it belongs to multiple nodes. This SuperflexPy design
choice is motivated by the fact that the unit is supposed to represent areas
that have the same hydrological response. The idea is that the hydrological
response is controlled by the parameters and, therefore, elements of the same
unit (e.g. HRU) belonging to multiple nodes should have the same parameter
values.

On the other hand, each node has its own states that are tracked separately
from the states of other nodes. In particular, when multiple nodes that share
the same parameter values receive different inputs (e.g., rainfall), their
states will evolve differently.

This design choice can support the most common use of nodes, which is the
discretisation of a catchment into potentially overlapping HRUs and
subcatchments. Parameters are then assumed constant within HRUs (units), and
inputs are assumed to be constant within subcatchments (nodes).

In term of SuperflexPy usage, this behavior is achieved by (1) copying the
states of the elements belonging to the unit when this unit becomes part of a
node; (2) sharing, rather than copying, the parameter values. This means that
changes to the parameter values of an elements within a node will affect the
parameter values in the elements of all other nodes that share the same unit.
In contrast, changes to the states will be node-specific.

This default behavior can be changed, by setting :code:`shared_parameters=False`
at the initialization of the node. In this case, all parameters become
node-specific, with no sharing of parameter values even within the same unit.

Refer to the section :ref:`demo_mult_nodes` for details on how to incorporate
the units inside the node.

Routing
*******

.. image:: pics/components/node_routing.png
   :align: center

A node can include routing functions that delay the fluxes. As shown in the
picture, two types of routing are possible:

- internal routing;

- external routing.

A typical usage of these routing functions, in semi-distributed hydrological
modelling, is to represent delays due to the routing of fluxes across the
catchment to the river network (internal routing) and/or the delay that derives
from the routing of the fluxes within the river network (external routing),
from the outlets of the present node to the inlet of the downstream node.

More generally, routing functions can be used for representing any type of delay
between the units and the node, and between nodes.

In the default implementation of the node in SuperflexPy, the two routing
functions simply return their input (i.e. no delay is applied). The user can
implement a different behavior following the example provided in the section
:ref:`routing_node`.

.. _components_network:

Network
-------

.. image:: pics/components/network.png
   :align: center

A network connects multiple nodes into a tree structure, and is typically
intended to develop a distributed model that generates predictions at internal
subcatchment locations (e.g. to reflect a nested catchment setup.

The connectivity of the network is defined by assigning to each node the
information about its downstream node. The network will then solve the nodes,
starting from the inlets and then moving downstream, solving the remaining nodes
and routing the fluxes towards the outlet.

The network is the only component of SuperflexPy that does not have the
:code:`set_input` method (see :ref:`generalities`) since the input, which is
node-specific, has to be assigned to each node within the network.

A node is *inserted* (rather than *copied*) in the network. In other words, we
initialize a node object and then insert it into the network. This node can then
be configured either directly or through the network. Any changes occurring
within the node as part of the network affect also the node *outside* the
network because they are the same Python object.

The output of the network is a dictionary that contains the output of all the
nodes of the network.

.. _generalities:

Generalities
------------

Common methods
**************

All components share the following methods.

-  **Parameters and states**: each component has its own parameters and/or
   states with unique identifiers. Each component of SuperflexPy has methods to
   set and get states and parameters of the component, and of the components
   contained in it:

    - :code:`set_parameters`: change the current parameter values

    - :code:`get_parameters`:  get the current parameter values

    - :code:`get_parameters_name`: get the identifier of the parameters

    - :code:`set_states`: change the current state values

    - :code:`get_states`: get the current state value

    - :code:`get_states_name`: get the identifier of the states

    - :code:`reset_states`: reset the states to their initialization value

-  **Time step**: as common in hydrological modeling, inputs and outputs are
   assumed to have the same time resolution (i.e. data must share the same
   timestamps), which is then used to generate outputs. There is no requirement
   for timestamps to be uniformly distributed, meaning that time series can have
   irregular time steps. In SuperflexPy, all components that require the
   definition of a time step (e.g. reservoirs described by a differential
   equation) contain methods that enable to set and get the time step. In case
   of not uniform time resolution, an array of time steps is required.

    - :code:`set_timestep`: set the time step used in the model; all components
      at a higher level (e.g. units) have this method; when called, it applies
      the change to all elements within the component;

    - :code:`get_timestep`: returns the time step used in the model.

- **Inputs and outputs**: all components have functionalities to receive inputs
  and generate outputs.

    - :code:`set_input`: set the input fluxes of the component;

    - :code:`get_output`: run the component (and all components contained in it)
      and return the output fluxes.

.. _identifier:

Usage of the identifier
***********************

Parameters, states, and components (except for the network) in SuperflexPy are
identified using an identifier string. The identifier string can have an
arbitrary length, with the only restriction that it cannot contain the
underscore :code:`_`.

When an element is inserted into a unit or when the unit is inserted into the
node, the identifier of the component is prepended to the name of the parameter
using the underscore :code:`_` as separator.

For example, if the element with identifier :code:`e1` has the parameter
:code:`par1`, the name of the parameter becomes, at initialization,
:code:`e1_par1`. When the element :code:`e1` is inserted into unit  :code:`u1`,
the parameter name becomes :code:`u1_e1_par1`, and so on.

In this way, every parameter and state of the model has its own unique
identifier that can be used to change its value from any component of
SuperflexPy.

Time variant parameters
***********************

In hydrological modelling, time variant parameters can be useful for
representing seasonal phenomena or stochasticity.

SuperflexPy is designed to operate both with constant and time variant
parameters. Parameters, in fact, can be either scalar float numbers or
Numpy 1D arrays of the same length as the input fluxes. In the first case, the
parameter will be interpreted as time constant, while, in the second case, the
parameter will be considered as time variant and may have a different value for
each time step.

.. _timestep:

Length of the simulation
************************

It has been decided to not have a parameter of the model fixing the length of
the simulation (i.e. the number of time steps that needs to be run); this will
be inferred at runtime from the length of the input fluxes that, for this
reason, must all have the same length.

Format of inputs and outputs
****************************

Input and output fluxes of SuperflexPy components are represented using 1D
Numpy arrays.

For the inputs, regardless of the number of fluxes, the method :code:`set_input`
takes a list of Numpy arrays (one array per flux); the order of the arrays
inside the list is relevant and must follow the indications of the docstring of
the method. All input fluxes must have the same length because the number of t
ime steps in the model simulation is determined by the length of the input time
series; see also :ref:`timestep`.

The outputs are also returned as a list of Numpy 1D arrays, from the
:code:`get_output` method.

Only for the :ref:`connections`, whenever the number of upstream or downstream
elements is different from one, the :code:`set_input` or the :code:`get_output`
methods will use 2D lists of Numpy arrays: this solution is used to route fluxes
between multiple elements.
