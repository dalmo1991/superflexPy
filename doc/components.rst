.. TODO:
.. - check reservoir equations and maybe copy from paper
.. - add lag equations

.. note:: Last update 26/06/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _components:

Organization of SuperflexPy
===========================

Superflex is designed to operate at several levels of complexity, from a single
reservoir to a complex river network. To do so, all components (i.e.
elements, units, nodes, network) are designed to operate alone or inside
other components.

For this reason, all components have methods that enable the execution of basic
functionality (e.g. parameter handling) at all levels.

We will first describe the common aspects of components and then describe each
component in specific detail.

Generalities
------------

Common methods
**************

All components share the following methods.

-  **Parameters and states**: each component may have parameters and/or states
   with unique identifiers. Each component of SuperflexPy has methods to set and
   get states and parameters of the component, and of its child components:

    - :code:`set_parameters`: change the current parameter values

    - :code:`get_parameters`:  get the current parameter values

    - :code:`get_parameters_name`: get the identifier of the parameters

    - :code:`set_states`: change the current state values

    - :code:`get_states`: get the current state value

    - :code:`get_states_name`: get the identifier of the parameters

    - :code:`reset_states`: reset the states to their initialization value

-  **Time step**: as commonly done in hydrological modeling, inputs and outputs
   are assumed to have the same constant time step. In SuperflexPy, all
   components that require the definition of a time step (e.g. reservoirs
   described by a differential equation) contain methods that enable to set and
   get the time step.

    - :code:`set_timestep`: set the time step used in the model; all components
      at a higher level (e.g. units) have this method; when called, it applies
      the change to all elements within the component;

    - :code:`get_timestep`: returns the time step used in the model.

- **Inputs and outputs**: all components have functionalities to receive the
  inputs and generate the outputs.

    - :code:`set_input`: set the input fluxes of the component;

    - :code:`get_output`: run the component (and all components contained in it)
      and return the output fluxes.

.. _identifier:

Usage of the identifier
***********************

Parameters and states in SuperflexPy are identified using a string. The string
can have an arbitrary length, with the only restriction that it cannot contain
the character underscore :code:`_`.

Every component of SuperflexPy (except for the network) must have a unique
identifier (that cannot contain the underscore :code:`_`). When an element is
inserted into a unit or when the unit is inserted into the node, the identifier
of the component is prepended to the name of the parameter using the underscore
:code:`_` as separator.

If, for example, the element with identifier :code:`e1` has the parameter
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
numpy 1D arrays of the same length as the input fluxes. In the first case, the
parameter will be interpreted as time constant, while, in the second case, the
parameter will be considered as time variant and may have a different value for
each time step.

.. _timestep:

Time step and length of the simulation
**************************************

As common practice in hydrological modeling, SuperflexPy uses a single uniform
time step. This means that all the input time series of fluxes must have the
same time resolution that will be, then, used to generate the outputs.

It has been decided to not have a parameter of the model fixing the length of
the simulation (i.e. the number of time steps that needs to be run); this will
be inferred at runtime from the length of the input fluxes that, for this
reason, must all have the same length.

Inputs and outputs formats
**************************

Inputs and outputs fluxes of SuperflexPy’s components are represented using 1D
numpy arrays.

For the inputs, regardless the number of fluxes, the method :code:`set_input`
takes a list of numpy arrays (one array per flux); the order of the arrays
inside the list must follow the indications of the docstring of the method.
All the input fluxes must have the same length since, as explained in the
section :ref:`timestep`, the length of the simulation is defined by this
length.

The outputs are also returned as a list of numpy 1D arrays, from the
:code:`get_output` method.

Only for the elements (this does not apply to units, nodes, and network),
whenever the number of upstream or downstream elements is different from one
(e.g. :ref:`connections`), the :code:`set_input` or the :code:`get_output`
methods will use 2D lists of numpy arrays: this solution is used to route fluxes
from and to multiple elements.

Elements
--------

Elements represent the basic level of the SuperflexPy's architecture; they can
operate either alone or, connected together as part of a unit.

Depending on their type, the elements can have parameters or states, can handle
multiple fluxes as input or as output, can be designed to operate with one or
more elements upstream or downstream, can be controlled by differential
equations, or by a convolution operations.

The framework provides the following basic elements that can be extended by the
user to satisfy all these possible modeling needs.

- :code:`BaseElement`: element without states and parameters;

- :code:`StateElement`: element with states but without parameters;

- :code:`ParameterizedElement`: element with parameters but without states;

- :code:`StateParameterizedElement`: element with states and parameters.

All possible elements can be generated from the four general elements listed
above. To facilitate the extension of the framework, we offer also
some specific elements of common use in hydrological modeling: reservoirs, lag
functions, and connections.

.. _reservoirs:

Reservoirs
**********

A reservoir is a storage element described by the differential equation

.. math::
   \frac{\textrm{d}\mathbf{S}}{\textrm{d}t}=\mathbf{I}(\mathbf{\theta}, t)-\mathbf{O}(S, \mathbf{\theta}, t)

where :math:`\mathbf{S}` is the internal states of the reservoir,
:math:`\mathbf{I}` represents the sum of all input fluxes (usually independent
from the state), :math:`\mathbf{O}` represents the sum of all output fluxes, and
:math:`\mathbf{\theta}` represents the parameters that control the behavior of
the reservoir.

SuperflexPy provides the class :code:`ODEsElement` that contains all the logic
needed to solve an element controlled by a differential equation. The user needs
only to specify the equations defining the fluxes.

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
building a unit. If an element has several elements downstream its fluxes need
to be split using a :code:`Splitter`; on the other hand, when the outflow of
several elements is collected by a single element, a :code:`Junction` element is
used.

SuperflexPy provides several types of connection elements. These elements are
designed to operate with an arbitrarily number of fluxes and upstream/downstream
elements.

Splitter
........

.. image:: pics/components/splitter.png
   :align: center

A :code:`Splitter` is an element that takes the outputs of a single upstream
element and distributes them to several downstream elements.

The behavior of a splitter in SuperflexPy is controlled by two matrices:
direction and weight. The "direction" controls into which downstream elements
the incoming fluxes are directed; the "weight" defines the proportion of each
flux that goes into each the downstream element.

Looking at the picture, the element E1 has 3 incoming fluxes: in order, red,
black, and blue. The red flux is taken entirely by element E3, the black
flux is taken entirely by element E2, and the blue flux is split at 30% to
E2 and 70% to E3.

The direction matrix for the splitter in the picture is here reported:

.. math::
   D=
   \begin{pmatrix}
   1 & 2 & \textrm{None}\\
   0 & 2 & \textrm{None}
   \end{pmatrix}

The direction matrix is a 2D matrix that has as many columns as the number of
fluxes and as many rows as the number of downstream elements. Each element of
the matrix contains the index identifying the incoming flux that is transferred
in that position to the downstream element. The blue flux, for example, is the
third (index 2) incoming flux and gets distributed as the second input (index 1)
to both downstream elements; the direction matrix will contain, therefore, the
number 2 in position (0,1) and (1,1), with the first number (row) that indicates
the downstream element and the second (column) that indicates the flux position.
When a flux is not sent to a downstream element (e.g red flux to E2) it
will be identified as :code:`None` in the direction matrix.

The direction matrix can be, therefore, used to change the order or to select
the fluxes that are transmitted to downstream elements.

The weight matrix for the splitter in the picture is here reported:

.. math::
   W=
   \begin{pmatrix}
   0 & 1.0 & 0.3\\
   1.0 & 0 & 0.7
   \end{pmatrix}

The weight matrix has the same dimensionality of the direction matrix. Each
element of this matrix represents the proportion of the respective incoming flux
that gets distributed to the specific downstream element. Looking at the blue
flux, it will occupy the third column in the weight matrix (because it is the
third incoming flux) and have value 0.3 in the first row (first downstream
element) and 0.7 in the second row (second downstream element).

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

Looking at the picture, the element E3 takes three fluxes as input: in order,
red, black, and blue. The red flux comes from both upstream elements; the black
flux comes only from E1; the blue flux comes only from E2.

The direction matrix for the junction in the picture is:

.. math::
   D=
   \begin{pmatrix}
   0 & 1\\
   1 & \textrm{None}\\
   \textrm{None} & 0
   \end{pmatrix}

The direction matrix has as many rows as the number of fluxes and as many
columns as number of upstream elements. Each entry of the matrix indicates the
position of the flux of the upstream elements that compose a specific flux of
the downstream element. The blue flux, that is the third incoming flux to E3,
for example, is represented by the third row of the matrix with the couple
(None, 0) since the flux is not present in E1 and it is the first flux of E2.

Linker
......

.. image:: pics/components/linker.png
   :align: center

A :code:`Linker` is an element that can be used to connect multiple elements
upstream to multiple elements downstream.

Its usefulness is due to the fact that in SuperflexPy the structure of the model
is defined as an ordered list of elements. This means that (refer to the
:ref:`unit` section for further details) if we want to connect the first
element of a layer with the second element of the following layer (e.g., E1
with E4, in the example above) we have to put an additional layer in between
that contains a linker that direct the fluxes to the proper downstream element.

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

The unit represents the second level of components in a SuperflexPy model and is
used to connect multiple elements. The unit can be used either alone in a lumped
configuration or, as part of a node, to create a semi-distributed model.

The elements are copied into the unit: this means that an element that belongs
to a unit is completely independent from the original element and from any
other copy of the same element in another units. Changes to the state or to the
parameters of an element inside a unit will, therefore, not reflect outside
the unit. The code below shows a consequence of this:

.. literalinclude:: components_code.py
   :language: python
   :lines: 1-8
   :linenos:

In the code, the element :code:`e1` is included in units :code:`u1` and
:code:`u2`. In lines 6-8 the value of the parameter :code:`p1` of :code:`e1` is
changed at the element and at the unit level. Since elements are **copied**
inside the unit, these changes are actuated on different elements (in the sense
of different Python objects in memory).

As shown in the picture, the elements are organized as a succession of layers,
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
(e.g. E1) an additional intermediate layer with a splitter: in the example,
the splitter S has two downstream elements (E2 and E3); the framework will route
the first group of outputs of the splitter to E2 and the second to E3.

Whenever there is a gap in the structure, a transparent element should be used
to fill the gap. In the example, the output of E3 have to be aggregated with
the output of E4; since the elements belong to different layers, making this
connection directly would create a gap in Layer 3. Such problem is solved
putting a transparent element in Layer 3, parallel to E4.

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
existing model structures.

Node
----

.. image:: pics/components/node.png
   :align: center

The node represents the third level of components in SuperflexPy and it is used
to aggregate different units, summing their contribution in the creation of the
total outflow. The node can be run either alone or as part of a bigger network.

The default behavior of the nodes is that parameters are shared between elements
of the same unit that belong to different nodes. This is motivated by the fact
that the unit is supposed to represent areas that have the same hydrological
response. The idea is that the hydrological response is controlled by the
parameters and that, therefore, elements of the same unit belonging to different
nodes should have the same parameter values. The states, on the other hand,
should be independent because different nodes may get different inputs and,
therefore, the evolution of their states should be independent.

This is achieved copying the states of the elements belonging to the unit when
this becomes part of a node while parameters are not copied but shared. This
means that changes to the values of the parameters of the elements in a node A
will reflect also in all the other nodes while changes to the states will be
node-specific.

This default behavior can be changed, making also the parameters independent, by
setting :code:`shared_parameters=False` at the initialization of the node.

Refer to the page :ref:`demo_mult_nodes` for details on how to incorporate
the units inside the node.

Routing
*******

The probably most common use of a node is to represent a catchment. A catchment
can be part of a larger system, composing a network.

For this reason, the node has the possibility of defining routing functions
that delay the fluxes; two types of routing are possible:

- internal routing;

- external routing.

The internal routing is designed to simulate the delays due to the routing of
fluxes from the catchment area to the river network; the external routing is
meant to represent the delay that derives from the routing of the fluxes inside
the river network, between the outlets of the present node and of the downstream
one.

In the default implementation of the node in SuperflexPy, the two routing
functions simply return their input (i.e. no delay is applied); the user can
implement a different behavior following the example provided in the page
:ref:`routing_node`.

Network
-------

.. image:: pics/components/network.png
   :align: center

The network represents the fourth level of components in SuperflexPy and it is
used to connect together several nodes, routing the fluxes from upstream to
downstream.

The topology of the network is defined assigning to each node the information
about its downstream node. The network will then solve the nodes, starting from
the inlets and then moving downstream, solving the remaining nodes and routing
the fluxes towards the outlet.

The network is the only component of SuperflexPy that does not have the
:code:`set_input` method since the input, which is node-specific, has to be
assigned to each node within the network.

When a node is inserted in the network it is not copied, meaning that any
change the node (e.g. setting different inputs) outside the network reflects also
inside.

The output of the network is not only the output of the outlet node but a
dictionary that contains the output of all the nodes of the network.
