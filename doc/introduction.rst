.. note:: Last update 03/05/2021

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. tip:: If interested in reading more about SuperflexPy, please check our
         `publication <https://doi.org/10.5194/gmd-14-7047-2021>`_ and the page
         :ref:`sfpy_lit`

Principles of SuperflexPy
=========================

Hydrological models are widely used in environmental science and engineering for
process understanding and prediction.

Models can differ depending on how the processes are represented (conceptual
vs. physical based models), and how the physical domain is discretized (from
simple lumped configurations to detailed fully-distributed models).

At the catchment scale, conceptual models are the most widely used class of
models, due to their ability to capture hydrological dynamics in a parsimonious
and computationally fast way.

Conceptual models
-----------------

Conceptual models describe hydrological dynamics directly at the scale of
interest. For example, in catchment-scale applications, they are based on
relationships between catchment storage and outflow. Such models are usually
relatively simple and cheap to run; their simplicity allows extensive
explorations of many different process representations, uncertainty
quantification using Monte Carlo methods, and so forth.

Many conceptual models have been proposed over the last 40 years. These models
have in common that they are composed by general elements such as reservoirs,
lag functions, and connections. That said, existing models do differ from each
other in a multitude of major and minor aspects, which complicates model
comparison and selection.

Model differences may appear on several levels:

- **conceptualization**: different models may represent a different set of
  hydrological processes;

- **mathematical model**: the same process (e.g. a flux) may be represented by
  different equations;

- **numerical model**: the same equation may be solved using different numerical
  techniques.

Several flexible modeling frameworks have been proposed in the last decade to
facilitate the implementation and comparison of the diverse set of hydrological
models.

Flexible modelling frameworks
-----------------------------

A flexible modeling framework can be seen as a language for building conceptual
hydrological models, which allows to build a (potentially complex) model from
simpler low-level components.

The main objective of a flexible modeling framework is to facilitate the process
of model building and comparison, giving modelers the possibility to adjust the
model structure to help achieve their application objectives.

Although several flexible modeling frameworks have been proposed in the last
decade, there are still some notable challenges. For example:

- implementation constraints can limit the originally envisaged flexibility of
  the framework;

- the choice of numerical model can be fixed;

- the spatial organization can be limited to lumped configurations;

- the ease of use can be limited by a complex software design.

These challenges can impact on usability, practicality and performance, and
ultimately limit the types of modeling problems that can be tackled. The
SuperflexPy framework is designed to address many of these challenges, providing
a framework suitable for a wide range of research and operational applications.

Spatial organization
--------------------

Hydrologists are increasingly interested in modeling
large catchments where spatial heterogeneity
becomes important. The following categories of spatial model organization can be
distinguished:

- **lumped configuration**, where the entire physical domain is considered
  uniform;

- **semi-distributed configuration**, where the physical domain is subdivided
  into (usually coarse) areal fractions that are assumed to have the same hydrological response
  and operate in parallel (usually without connectivity between them);

- **fully-distributed configuration**, where the physical domain is subdivided
  into a (usually fine) grid. This configuration typically includes flux
  exchanges between neighboring grid cells.

The lumped approach yields the simplest models, with a low number of parameters
and often sufficiently good predictions. However, the obvious limitation is that
if the catchment properties vary substantially in space, the lumped model will
not capture these variations. Nor can a lumped model produce spatially distributed
streamflow predictions.

The fully-distributed approach typically yields models with a large number of
parameters and high computational demands, usually related to the resolution of
the grid that is used.

The semi-distributed approach is intermediate between the other two approaches
in terms of spatial complexity and number of parameters. A typical example is
the discretisation of the catchment into Hydrological Response Units (HRUs),
defined as catchment areas assumed to behave in a hydrologically "similar" way.
The definition of HRUs represents a modelling choice and depends on the process
understanding available in the catchment of interest.

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

The first level is represented by "elements", which comprise reservoirs, lag
functions, and connections. Elements can represent entire models or individual
model components, and are intended to represent specific processes within the
hydrological cycle (e.g. soil dynamics).

The second level is represented by "units", which connect together multiple
elements. This level can be used to build lumped models or to represent HRUs
within a spatially distributed model.

The third level is represented by "nodes", where each node contains several
units that operate in parallel. Nodes can be used to distinguish the behavior of
distinct units within a catchment, e.g., when building a (semi)-distributed
model where the units are used to represent HRUs (defined according to soil,
vegetation, topography, etc).

The fourth level is represented by the "network", which connects multiple nodes
and routes the fluxes from upstream to downstream nodes. This level enables the
representation of large watersheds and river networks that comprise several
subcatchments with substantial flow routing delays. A SuperflexPy model
configuration can contain only a single network.

Technical details on these components are provided in the :ref:`components`
page.
