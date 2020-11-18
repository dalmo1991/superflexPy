.. note:: Last update 18/11/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. tip:: If interested in the context in which SuperflexPy operates, please
         check our publication (**link here when available**)

Principles of SuperflexPy
=========================

Hydrological models are widely used in engineering and science for prediction
and process understanding.

Models can differ depending on how the processes are represented (conceptual
vs. physical based models), and how the physical domain is discretized (from
lumped configurations to detailed fully-distributed models).

At the catchment scale, conceptual models are the most widely used class of
models due to their ability to capture hydrological dynamics in a parsimonious
and computationally fast way.

Conceptual models
-----------------

Conceptual models describe hydrological dynamics directly at the catchment
scale, providing relationships between the storage of the catchment and the
outflow. Such models are usually relatively simple and cheap to run; their
simplicity allows extensive explorations of many different process
representations, uncertainty quantification using Monte Carlo methods, and so
forth.

Many conceptual models have been proposed over the last 40 years. These models
have in common that they are composed by general elements such as reservoirs,
lag functions, and connections. That said, these models differ one from the
other, making model selection and comparison complicated.

Differences may appear on several levels:

- **conceptualization**: different models may decide to represent different
  processes;

- **mathematical model**: the same process (e.g. a flux) may be represented by
  different equations;

- **numerical model**: the same equation may be solved using different numerical
  techniques.

Several flexible modeling frameworks have been proposed in the last decade to
facilitate the implementation and comparison of the diverse set of hydrological
models.

Flexible modelling frameworks
-----------------------------

A flexible modeling framework is a language for building conceptual hydrological
models, which allows to build complex model starting from low-level components.

The main objective of a flexible modeling framework is to facilitate the model
building and comparison process, giving modelers the possibility to adjust the
model structure to the necessary complexity. To do so, it provides a software
platform that allows the user to build models that differ in the
conceptualization but share the same mathematical and numerical formulation.

Although in the last decade several flexible modeling frameworks have been
proposed, there are still some challenges that impact on usability and the
types of modelling problems that can be tackled:

- implementation constrains can limit the envisaged flexibility of the
  framework;

- the choice of the numerical model can be fixed;

- the spatial organization can be limited to lumped configurations;

- ease of use of the frameworks can be limited by a complex software design.

These challenges can limit the possibility of fully exploiting the potential of
flexible modelling frameworks and are addressed with SuperflexPy.

Spatial organization
--------------------

Hydrologist may need to model large catchments where spatial heterogeneity
becomes important. The following categories can be distinguished:

- **lumped configuration**, where all the physical domain is considered uniform;

- **semi-distributed configuration**, where the physical domain is subdivided in
  areal fractions that have the same hydrological response and operate in
  parallel (without connectivity between them);

- **fully-distributed configuration**, where the physical domain is subdivided
  with a (usually) uniform grid. This configuration account for the presence of
  flux exchanges between cells that operate together to calculate the
  hydrological response.

The lumped approach yields the simplest, with a low number of parameters and
often sufficiently good predictions. However, the obvious limitation is that if
the catchment properties vary substantially in space, the lumped model will not
capture these variations. Nor can a lumped model produce distributed streamflow
predictions.

The fully-distributed approach divides the catchment into a grid. Pixels can be
modelled individually or aggregated into larger groups. This approach produces
models with high computational demand and a large number of parameters, usually
related to the resolution of the grid that is used.

The semi-distributed approach is intermediate between the other two approaches
in terms of spatial complexity and number of parameters. A typical example is
the discretisation of the catchment into Hydrological Response Units (HRUs),
defined as catchment areas assumed to behave in a hydrologically "similar" way.
The definition of HRUs represents a modelling choice and depends on the process
understanding available for the catchment of interest.

SuperflexPy
-----------

SuperflexPy is a new flexible framework for building hydrological
models. It is designed to accommodate models with a wide range of structural
complexity, and to support spatial configurations ranging from lumped to
distributed. The design of SuperflexPy is informed by the extensive experience
of its authors and their colleagues in developing and applying conceptual
hydrological models.

In order to balance flexibility and ease of use, SuperflexPy is organized in
four different levels, which correspond to different degrees of spatial
complexity:

1. elements;

2. units;

3. nodes;

4. network.

The first level is represented by "elements"; elements comprise reservoirs, lag
functions, and connections. Elements can represent entire models, or individual
model components, intended to represent specific processes within the
hydrological cycle (e.g. soil dynamics).

The second level is represented by "units"; a unit is a component that connects
together multiple elements. This level enables lumped model configurations,
composed by multiple elements, creating the structure of a lumped configuration.

The third level is represented by "nodes"; a node contains several units that
operate in parallel. Nodes are typically used to distinguish the behavior of
distinct units within a catchment, which may represent separate landscape
sections (e.g. HRUs).

The fourth level is represented by the "network"; a network connects multiple
nodes, routing the fluxes from the upstream to downstream nodes. This
enables the representation of complex watersheds that are composed by several
subcatchments, creating a semi-distributed hydrological model.

Technical details on these components are provided in the :ref:`components`
page.
