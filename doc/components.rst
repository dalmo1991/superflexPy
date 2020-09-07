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
reservoir to a complex river network. To do so, all the components are designed
to operate alone or inside other components.

For this reason, all the components have a series of methods that are
implemented to enable the execution of some basic functionality (e.g.
parameters handling) at all the levels.

We will first describe the common aspects of all the components of the
framework and, then, go specific in describing each one of them.

Generalities
------------

Common methods
**************

All the components share the following common methods.

-  **Parameters and states**: each component may have parameters or
   states that are identified by a unique identifier. Each component of
   SuperflexPy have implemented some methods that enable to set or get states
   and parameters of the component and of the components that it contains:

    - :code:`set_parameters`: change the value of the parameters

    - :code:`get_parameters`:  get the current value of the parameters

    - :code:`get_parameters_name`: get the identifier of the parameters

    - :code:`set_states`: change the value of the states

    - :code:`get_states`: get the current value of the states

    - :code:`get_states_name`: get the identifier of the parameters

    - :code:`reset_states`: reset the states to their initialization value

-  **Time step**: as commonly done in hydrological modeling, inputs and outputs
   are assumed to have the same constant time step. In SuperflexPy, all the
   components that require the definition of a time step (e.g. reservoirs that
   are controlled  by a differential equation) contain the methods that enable
   to set and get the time step.

    - :code:`set_timestep`: set the time step used in the model; all the
      components at a higher level (e.g. units) have this method; when called,
      it applies the change to all the elements contained in the component;

    - :code:`get_timestep`: returns the time step used in the model.

- **Inputs and outputs**: all the components have functionalities to handle the
  inputs and to generate the outputs.

    - :code:`set_input`: set the input fluxes of the component;

    - :code:`get_output`: run the component (and all the components contained in
      it) and return the output fluxes.

Usage of the identifier
***********************

Parameters and states in SuperflexPy are identified using a string. The string
can have an arbitrary length with the only requirement that it cannot contain
the character underscore :code:`_`.

Every component of SuperflexPy (except for the network) must have a unique
identifier (that cannot contain the character :code:`_`). When an element is
inserted into a unit or when the unit is inserted into the node, the identifier
of the component is prepended to the name of the parameter using the character
:code:`_` as separator.

If, for example, the element with identifier :code:`e1` has the parameter
:code:`par1`, the name of the parameter becomes, at initialization,
:code:`e1_par1`. When, then, the element is inserted into the unit :code:`u1`
its name becomes :code:`u1_e1_par1`, and so on.

In this way, every parameter and state of the model has its own unique
identifier that can be used to change its value from every component of
SuperflexPy.

Time variant parameters
***********************

In hydrological modelling, time variant parameters can be useful for
representing seasonal phenomena or stochasticity.

SuperflexPy is designed to operate both with constant and time variant
parameters. Parameters, in fact, can be either scalar float numbers or
numpy 1D arrays of the same length of the input fluxes; in the first case, the
parameter will be interpreted as time constant while, in the second case, the
parameter will be considered as time variant and have a specific value for each
time step.

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
inside the list must follow the indications of the documentation of the method.
All the input fluxes must have the same dimension since, as explained in the
section :ref:`timestep`, the length of the simulation is defined by this
dimension.

The output fluxes are also returned as a list of numpy 1D arrays from the
:code:`get_output` method.

Only for the elements, whenever the number of upstream or downstream elements
is different from one (e.g. :ref:`connections`), the :code:`set_input` or the
:code:`get_output` methods will use bidimensional lists of numpy arrays: this
solution is used to route fluxes from and to multiple elements.

Elements
--------

Elements represent the basic level of the SuperflexPy's architecture; they can
operate either alone or, connected together, as part of a unit.

Depending on the type, the elements can have parameters or states, can handle
multiple fluxes as input or as output, can be designed to operate with one or
more elements upstream or downstream, can be controlled by differential
equations, or can be designed to operate a convolution operation on the
incoming fluxes.

The framework provides a series of basic elements that can be extended by the
user to satisfy all these possible modeling needs.

- :code:`BaseElement`: element without states and parameters;

- :code:`StateElement`: element with states but without parameters;

- :code:`ParameterizedElement`: element with parameters but without states;

- :code:`StateParameterizedElement`: element with states and parameters.

All the possible elements can be generated starting from the four general
elements proposed; to facilitate the extension of the framework, we offer also
some specific elements of common use in hydrological modeling; those are
reservoirs, lag functions, and connections.

.. _reservoirs:

Reservoirs
**********

A reservoir is an element that receives an input and transforms it, based on
its internal state and on some parameters. It is usually governed by the
differential equation

.. math::
   \frac{\textrm{d}S}{\textrm{d}t}=\mathbf{I}(\mathbf{\theta}, t)-\mathbf{O}(S, \mathbf{\theta}, t)

Where :math:`S` is the internal state of the reservoir, :math:`\mathbf{I}`
represents the incoming fluxes (usually independent from the state),
:math:`\mathbf{O}` represents the outgoing fluxes, and :math:`\mathbf{\theta}`
is a vector representing the parameters that control the behavior of the
reservoir.

The framework provides the class :code:`ODEsElement` that contains all the logic
that is needed to solve an element that is controlled by a differential
equation. The user needs only to define the equations needed to calculate the
fluxes.

The solution of the differential equation is done using a numerical
approximation; the choice of the numerical approximation (e.g. implicit Euler)
is left to the user, when initializing the reservoir.

SuperflexPy provides already some "numerical approximators" that can be used to
create a numerical approximation of the differential equation (e.g. implicit or
explicit Euler). These approximators are designed to operate coupled with a
"root finder" that finds the solution (root) of the numerical approximation of
the differential equation. The user can either use the numerical routines
provided by the framework or implement the interface necessary to use an
external solver (e.g. from scipy), which may be needed when the numerical
problem becomes more complex (e.g. coupled differential equations). For more
information about the numerical solver refer to the page
:ref:`numerical_solver`.

Lag functions
*************

A lag function is an element that applies a delay to the incoming faxes;
mathematically, the lag function applies a convolution to the incoming fluxes.
In practice, the result is usually achieved distributing the fluxes at each
time step in the following ones, according to weight array.

SuperflexPy already provides class, called :code:`LagElement`, that implements
all the methods needed to represent a lag function, leaving to user only the
duty of defining weight array that has to be used.

.. _connections:

Connections
***********

Connection elements are needed to link together different elements, when
building a unit. If an element has several elements downstream, for example,
its fluxes need to be split using a :code:`Splitter`; on the other hand, when
the outflow of several elements is collected by a single one, this operation has
to be done through a :code:`Junction` element.

SuperflexPy provides several elements to connect and to fill the gaps in the
structure; these elements are designed to operate with an arbitrarily large
number of fluxes and upstream or downstream elements.

Splitter
........

.. image:: pics/components/splitter.png
   :align: center

A :code:`Splitter` is an element that takes the outputs of a single upstream
element and distributes them to feed several downstream elements.

The behavior of a splitter in SuperflexPy is controlled by two matrices:
direction and weight. The first controls into which downstream elements the
incoming fluxes are directed; the second defines the proportion of each flux
that goes to the downstream elements.

Looking at the picture, the element E1 has 3 incoming fluxes: in order, red,
black, and blue. The red flux is taken entirely by the element E3, the black
flux is taken entirely by the element E2, and the blue flux is split at 30% to
E2 and 70% to E3.

That direction matrix is a 2D matrix that has as many columns as the number of
fluxes and as many rows as the number of downstream elements. Each element of
the matrix contains the index identifying the incoming flux that is transferred
in that position to the downstream element. The blue flux, for example, is the
third (index 2) incoming flux and gets distributed as second input (index 1)
to both downstream elements; the direction matrix will contain, therefore,
the number 2 in position (0,1) and (1,1), with the first number (row) that
indicates the downstream element and the second (column) that indicates the
flux position. When a flux is not sent to a downstream element (e.g red flux
to E2) it will be identified as None in the direction matrix.

The direction matrix for the splitter in the picture is here reported:

.. math::
   D=
   \begin{pmatrix}
   1 & 2 & \textrm{None}\\
   0 & 2 & \textrm{None}
   \end{pmatrix}

The weight matrix has the same dimensionality of the direction matrix. Each
element of this matrix represents the proportion of the respective incoming flux
that gets distributed to the specific downstream element. Looking at the blue
flux, it will occupy the third column in the weight matrix (because it is the
third incoming flux) and have value 0.3 in the first row (first downstream
element) and 0.7 in the second row (second downstream element).

The weight matrix for the splitter in the picture is here reported:

.. math::
   W=
   \begin{pmatrix}
   0 & 1.0 & 0.3\\
   1.0 & 0 & 0.7
   \end{pmatrix}

Note that, as a quick check, the sum of each column of the weight matrix should
be 1 otherwise a portion of the flux is lost.

Junction
........

.. image:: pics/components/junction.png
   :align: center

A :code:`Junction` is an element that takes the outputs of several upstream
elements and converges them into a single downstream element.

The behavior of a junction in SuperflexPy is controlled by direction matrix that
defines how the incoming fluxes have to be aggregated (summed) to feed the
downstream element.

Looking at the picture, the element E3 takes three fluxes as input: in order,
red, black, and blue. The red flux comes from both upstream elements; the black
flux comes only from E1; the blue flux comes only from E2.

The direction matrix has as many rows as the number of fluxes and as many
columns as number of upstream elements. Each entry of the matrix indicates the
position of the flux of the upstream elements that compose a specific flux of
the downstream element. The blue flux, that is the third incoming flux to E3,
for example, is represented by the third row of the matrix with the couple
(None, 0) since the flux is not present in E1 and it is the first flux of E2.

The direction matrix for the junction in the picture is here reported:

.. math::
   D=
   \begin{pmatrix}
   0 & 1\\
   1 & \textrm{None}\\
   \textrm{None} & 0
   \end{pmatrix}

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

A transparent element is an element that does nothing: it returns, as output,
the same fluxes that it takes as input. It is needed to fill gaps in the
structure defined in the unit.

.. _unit:

Unit
----

.. image:: pics/components/unit.png
   :align: center

The unit represents the second level of components in SuperflexPy and it is used
to connect different elements, moving the fluxes from upstream to downstream.
The unit can be used either alone in a lumped configuration or, as part of a
node, to create a semi-distributed model.

The elements are copied into the unit: this means that an element that belongs
to a unit is completely independent from the original element and from any
other copy of the same element in another units. Changes to the state or to the
parameters of an element inside a unit will, therefore, not reflect outside
the unit.

As shown in the picture, the elements are organized as a succession of layers,
from left (upstream) to right (downstream).

The first and the last layer must contain only a single element, since the
inputs of the unit are transferred to the first element and the outputs of the
unit are taken from the last element.

The order of the elements inside each layer defines how they are connected:
the first element of a layer (e.g. E2 in the picture) will transfer its outputs
to the first element of the downstream layer (e.g. E4); the second element of
a layer (e.g. E3) will transfer its outputs to the second element of the
downstream layer (e.g. T), and so on.

When the output of an element is split between more downstream elements
(e.g. E1) the operation has to be done putting an additional layer in between
that contains a splitter: in the example, the splitter S has two downstream
elements (E2 and E3); the framework will route the first group of outputs of
the splitter to E2 and the second to E3.

Whenever there is a gap in the structure, a transparent element should be used
to fill the gap. In the example, the output of E3 have to be aggregated with
the output of E4; since the elements belong to different layers, this can be
achieved putting a transparent element in the same layer of E4.

Since the unit must have a single element in the last layer, the outputs of E4
and T must be collected using a Junction.

Each element is aware of the number of upstream and downstream elements that it
must have (for example, a reservoir must have one element upstream and
downstream, a splitter must have one element upstream and can have several
elements downstream, and so on). The structure of a unit is valid only if the
number downstream elements that a layer must have is equal to the number of
upstream elements that the following must have. In the example, layer 1 must
have two downstream elements (information contained in the splitter) that is
consistent with the configuration of layer 2.

To get more familiar with the definition of the model structure in SuperflexPy
and to understand how to reproduce the structures of popular models,
refer to the page :ref:`popular_models`.

Node
----

The node represents the third level of components in SuperflexPy and it is used
to aggregate different units, summing their contribution in the creation of the
total outflow. The node can be run either alone or as part of a bigger network.

When a unit is inserted into a node, the default behavior is that the states of
the elements belonging to the unit get copied while the parameters no. This
means that, if same unit belongs to two different nodes (A and B), changes to
the values of the parameters of the elements in node A will reflect also in
node B while changes to the values of the states of the elements in node A will
not reflect in node B. This default behavior can be changed, making also the
parameters independent (set :code:`shared_parameters=False` at initialization).

The choice of sharing the parameters between elements of the same unit that
belong to different nodes is motivated by the fact that the unit is supposed to
represent areas that have the same hydrological response. The idea is that the
hydrological response is controlled by the parameters and that, therefore,
elements of the same unit belonging to different nodes should have the same
parameter values. The states, on the other hand, should be independent because
different nodes may get different inputs and, therefore, the evolution of
their states should be independent.

Refer to the page :ref:`demo_mult_nodes` for details on how to incorporate
the units inside the node.

Routing
*******

The most common use of a node is to represent catchment, which can be part of a
larger system, composing a network.

For this reason, the node has the possibility of defining routing functions
that delay the fluxes; two types of routing are possible:

- internal routing;

- external routing.

The first is designed to simulate the delay that the fluxes get when they are
collected from the units to the river network; the former is meant to represent
the delay that derives from the routing of the fluxes inside the river network,
between the outlets of the present node and of the downstream one.

In the default implementation of the node in SuperflexPy, the two routing
functions simply return their input (i.e. no delay is applied); the user can
change this behavior creating a customized node that implements these
functions.

An example on how to do that can be found in the page :ref:`routing_node`

Network
-------

The network represents the fourth level of components in SuperflexPy and it is
used to connect together several nodes, routing the fluxes from upstream to
downstream.

The topology of the network is defined assigning to each node the information
about its downstream node. The network will then solve the nodes, starting from
the most upstream ones and then moving downstream, solving the remaining nodes
and routing the fluxes towards the output of the network.

The network is the only component of SuperflexPy that does not have the
:code:`set_input` method since the input, which is node-specific, has to be
assigned to each node belonging to the network.

When a node is inserted in the network it is not copied, meaning that any
change the node (e.g. setting different inputs) outside the network reflects also
inside.

To respond to the practical needs of the modeler, the output of the network is
not only the output of the most downstream node but a dictionary that contains
the output of all the nodes of the network.
