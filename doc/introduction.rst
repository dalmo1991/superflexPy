.. TODO (review 26 Jun 2020):
.. - Add link to paper

.. note:: Last update 26/06/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. tip:: If interested in the context in which SuperflexPy operates, please
         check our publication (**link here when available**)

Principles of SuperflexPy
=========================

Numerical models are widely used in hydrology for prediction, process
understanding, and engineering applications.

Models can differ depending on how the processes are represented (conceptual
vs. physical based models) or on how the physical domain gets discretized (from
lumped configurations to detailed grid-based models).

Conceptual models are, at the catchment scale, among the most used due to their
limited number of parameters and high interpretability.

Conceptual models
-----------------

Conceptual models are hydrological models that describe the dynamics directly
at the catchment scale, providing relationship between the storage of the
catchment and the outflow. Such models are usually relatively simple and cheap
to run; their simplicity allows to use conceptual models to explore the
processes directly at the catchment scale.

Thanks to their appealing features, a large variety of conceptual models has
been proposed in the last 40 years. These models are usually quite similar,
being composed by general elements such as reservoirs, lag functions, and
connections but, at the same time, they are all slightly different one from the
other, making model selection and comparison complicated.

Differences may appear in several levels:

- **conceptualization**: different models may decide to represent different
  processes;

- **mathematical model**: the same process (e.g. a flux) may be represented by
  different equations;

- **numerical model**: the same equation may be solved with different numerical
  techniques.

In order to overcome these 3 problems and to facilitate the configuration and
comparison of different solutions, several flexible modeling frameworks have
been proposed in the last decade.

Flexible modelling frameworks
-----------------------------

A flexible modeling framework is a software platform that allows the user to
build customized hydrological models that, usually, differ in the
conceptualization but share the same mathematical and numerical formulation.

In order to achieve this result, flexible modeling frameworks usually offer a
library of generic elements (e.g., reservoirs, lag functions, connections, etc.)
and the possibility of connecting them freely.

In the last decade several flexible modeling frameworks have been proposed;
while representing a step forward compared to classical conceptual models in
terms of flexibility, these frameworks still present problematics:

- the promised infinite flexibility is actually lost in the implementation,
  with some frameworks that have a master structure with the possibility
  selecting the elements and fluxes to use;

- the choice of the numerical model is sometimes fixed, not allowing user to
  assess its impact on the results;

- the spatial discretization is usually pre-defined (e.g., some frameworks can
  operate only in lumped configuration while others are designed to operate on
  grids) not allowing the user to assess the impact of different
  discretizations;

- the frameworks are usually difficult to modify or extend by users that are
  not part of the core development team since these operations require a deep
  understanding of the source code;

- the source code itself may not be available as open-source and distributed
  only as executable;

These limitations, mainly due to implementation issues, limit the possibility
of fully exploiting the potential of flexible modelling frameworks and can be
addressed with a careful software implementation.

Spatial organization
--------------------

Another important aspect to consider when designing a hydrological model is the
spatial resolution to utilize to represent the catchment. Most of the existing
models and frameworks can be classified in one or more of the following
categories:

- **lumped configuration**, when all the physical domain is considered uniform;

- **grid-based configuration**, when the physical domain is subdivided with a
  (usually) uniform grid;

- **semi-distributed configuration**, when the physical domain is subdivided in
  irregular areas that have the same hydrological response.

The first approach produces the simplest model, with a limited number of
parameters and usually fairly good predictions; the limitation of this choice
is that, if there are areas of the catchment behaving differently, the model
will not be able to represent this difference, with consequences on the values
of the calibrated parameters and on their interpretation.

The second approach produces models with high computational demand and a large
number of parameters; the catchment gets divided with a grid and the underlying
assumption, that each pixel has its own hydrological behavior, may be relaxed
aggregating different areas.

The third approach, which is in between the other two in terms of spatial
complexity and number of parameters, tries to find a subdivision of the
catchment that is driven by process understanding; this results is a
subdivision in irregular areas that are supposed to have the same hydrological
behavior; this approach enables the modeller to reflect his/her understanding
of the dominant processes at the catchment scale.

SuperflexPy
-----------

In order to overcome most of the problems illustrated above, we have developed
SuperflexPy, a new flexible framework for building conceptual hydrological
models with different levels of spatial complexity, from lumped to
semi-distributed.

SuperflexPy contains the functionalities to build all the common elements that
can be found in the conceptual models or in the flexible modeling frameworks
and to connect them, constructing spatially distributed configurations.

In order to do that, SuperflexPy is internally organized in four different
levels to satisfy different degrees of spatial complexity:

- elements;

- units;

- nodes;

- network.

The lower level is represented by the elements; they can be, for example,
reservoirs, lag functions, or connections and are designed to represent
specific processes affecting the hydrological cycle (e.g. soil dynamics).

The second level is represented by the units; a unit is a component that
connects together several elements creating the structure of a lumped
configuration.

The third level is represented by the nodes; a node contains several units that
operate in parallel. Each unit should represent the contribution of different
hydrological behaving areas of the node.

The fourth level is represented by the network; a network connects different
nodes, routing the fluxes from the upstream to the downstream ones. This
enables the representation of complex watersheds that are composed by several
subcatchments, creating a semi-distributed hydrological model.

Technical details on these components are provided in the :ref:`components`
page.
