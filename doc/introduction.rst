.. TODO (review 26 Jun 2020):
.. - Add link to paper

.. note:: Last update 06/10/2020

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
vs. physical based models) or on how the physical domain gets discretized (from
lumped configurations to detailed grid-based models).

At the catchment scale, conceptual models are the most widely used class of
models due to their ability to capture hydrological dynamics in a parsimonious
and computationally fast way.

Conceptual models
-----------------

Conceptual models describe hydrological dynamics directly
at the catchment scale, providing relationship between the storage of the
catchment and the outflow. Such models are usually relatively simple and cheap
to run; their simplicity allows to use conceptual models to explore the
processes directly at the catchment scale.

Many conceptual models have been proposed in the last 40 years. These models
have in common that they are composed by general elements such as reservoirs,
lag functions, and connections. That said, these models differ one from the
other, making model selection and comparison complicated.

Differences may appear on several levels:

- **conceptualization**: different models may decide to represent different
  processes;

- **mathematical model**: the same process (e.g. a flux) may be represented by
  different equations;

- **numerical model**: the same equation may be solved with different numerical
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
proposed, there are still some challenges that need to be taken:

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

- **lumped configuration**, when all the physical domain is considered uniform;

- **semi-distributed configuration**, when the physical domain is subdivided in
  areal fractions that have the same hydrological response and operate in
  parallel (without connectivity between them).

- **grid-based configuration**, when the physical domain is subdivided with a
  (usually) uniform grid;

The lumped approach is the simplest, with a limited number of parameters and
usually fairly good predictions. However, the obvious limitation is that if the
catchment properties vary substantially in space, the lumped model will not
capture these variations. Nor can a lumped model produce distributed streamflow
predictions.

The grid-based approach divides the catchment with a grid and the underlying
assumption, that each pixel has its own hydrological behavior, may be relaxed
aggregating different areas. This configuration produces models with high
computational demand and a large number of parameters.

The semi-distributed approach, which is in between the other two in terms of
spatial complexity and number of parameters, tries to find a subdivision of the
catchment that is driven by process understanding; this results is a
subdivision in irregular areas that are supposed to have the same hydrological
behavior (often referred to as Hydrological Response Units, HRUs).

SuperflexPy
-----------

SuperflexPy is a new flexible framework for building conceptual hydrological
models with different levels of spatial complexity, from lumped to
semi-distributed. It is designed to overcome several limitations of existing
flexible frameworks.

SuperflexPy contains the functionalities to build conceptual models, ranging
from lumped to distributed.

In order to balance ease of use and flexibility, SuperflexPy is internally
organized in four different levels, which correspond to different degrees of
spatial complexity:

- elements;

- units;

- nodes;

- network.

The lower level is represented by "elements"; they can be, for example,
reservoirs, lag functions, or connections. They can represent entire models, or
individual model components, intended to represent specific processes within the
hydrological cycle (e.g. soil dynamics).

The second level is represented by "units"; a unit is a component that connects
together multiple elements. This level enables lumped model configurations,
composed by multiple elements, creating the structure of a lumped configuration.

The third level is represented by "nodes"; a node contains several units that
operate in parallel. Nodes are typically used to distinguish the behavior of
distinct units within a catchment, which may represent separate landscape
sections (e.g. Hydrological Response Units).

The fourth level is represented by the "network"; a network connects multiple
nodes, routing the fluxes from the upstream to downstream nodes. This
enables the representation of complex watersheds that are composed by several
subcatchments, creating a semi-distributed hydrological model.

Technical details on these components are provided in the :ref:`components`
page.
