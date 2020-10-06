.. TODO
.. - check if complete
.. - review

.. note:: Last update 26/06/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _elements_list:

List of currently implemented elements
======================================

This page contains all the elements implemented extending the classes provided
by SuperflexPy. The elements are divided in three categories

- Reservoir
- Lag elements
- Connections

The elements are listed in alphabetical order.

Reservoirs
----------

..
    Please use the following template

    Name of the element (Model)
    ***************************

    Code to import the element

    Governing equations
    ...................

    Inputs required
    ...............
    - Input 1
    - Input 2

    Main outputs
    ............

    Secondary outputs
    .................

Fast reservoir (inspired to HBV)
********************************

This is a reservoir, inspired do the family of HBV-like models, where the
output is a power function of the state. The name "fast" derives from its common
application to represent the fast response component in the model.

.. code-block:: python

   from superflexpy.implementation.elements.hbv import FastReservoir

Inputs
......

- Precipitation (:math:`P\ [LT^{-1}]`)

Main outputs
............

- Total outflow (:math:`Q\ [LT^{-1}]`)

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P - Q \\
   & Q=kS^{\alpha}

Interception filter (GR4J)
**************************

This reservoir is part of the GR4J model and it is used to simulate
interception. Further details are provided in the page :ref:`gr4j_example`.

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import InterceptionFilter

Inputs
......

- Potential evapotranspiration (:math:`E^{\textrm{in}}_{\textrm{POT}}\ [LT^{-1}]`)
- Precipitation (:math:`P^{\textrm{in}}\ [LT^{-1}]`)

Main outputs
............

- Net potential evapotranspiration (:math:`E^{\textrm{out}}_{\textrm{POT}}\ [LT^{-1}]`)
- Net precipitation (:math:`P^{\textrm{out}}\ [LT^{-1}]`)

Governing equations
...................

.. math::
   & \textrm{if } P^{\textrm{in}} > E^{\textrm{in}}_{\textrm{POT}}: \\
   & \quad P^{\textrm{out}} = P^{\textrm{in}} - E^{\textrm{in}}_{\textrm{POT}} \\
   & \quad E^{\textrm{out}}_{\textrm{POT}} = 0 \\ \\
   & \textrm{if } P^{\textrm{in}} < E^{\textrm{in}}_{\textrm{POT}}: \\
   & \quad P^{\textrm{out}} = 0 \\
   & \quad E^{\textrm{out}}_{\textrm{POT}} = E^{\textrm{in}}_{\textrm{POT}} - P^{\textrm{in}}

Linear reservoir (Hymod)
************************

This reservoir is part of the Hymod model and it is used to simulate channel
routing and lower zone. Further details are provided in the page :ref:`hymod`.

.. code-block:: python

   from superflexpy.implementation.elements.hymod import LinearReservoir

Inputs
......

- Precipitation (:math:`P\ [LT^{-1}]`)

Main outputs
............

- Total outflow (:math:`Q\ [LT^{-1}]`)

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P - Q \\
   & Q=kS

Production store (GR4J)
***********************

This reservoir is part of the GR4J model and it is used to simulate runoff
generation. Further details are provided in the page :ref:`gr4j_example`.

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import ProductionStore

Inputs
......

- Potential evapotranspiration (:math:`E_{\textrm{pot}}\ [LT^{-1}]`)
- Precipitation (:math:`P\ [LT^{-1}]`)

Main outputs
............

- Total outflow (:math:`P_{\textrm{r}}\ [LT^{-1}]`)

Secondary outputs
.................

- Actual evapotranspiration (:math:`E_{\textrm{act}}\ [LT^{-1}]`) :code:`get_aet()`

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P_{\textrm{s}}-E_{\textrm{act}}-Q_{\textrm{perc}} \\
   & P_{\textrm{s}}=P\left(1-\left(\frac{S}{x_1}\right)^\alpha\right) \\
   & E_{\textrm{act}}=E_{\textrm{pot}}\left(2\frac{S}{x_1}-\left(\frac{S}{x_1}\right)^\alpha\right) \\
   & Q_{\textrm{perc}} = \frac{x^{1-\beta}}{(\beta-1)}\nu^{\beta-1}S^{\beta} \\
   & P_{\textrm{r}}=P - P_{\textrm{s}} + Q_{\textrm{perc}}

Routing store (GR4J)
********************

This reservoir is part of the GR4J model and it is used to simulate routing.
Further details are provided in the page :ref:`gr4j_example`.

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import RoutingStore

Inputs
......

- Precipitation (:math:`P\ [LT^{-1}]`)

Main outputs
............

- Outflow (:math:`Q\ [LT^{-1}]`)
- Loss term (:math:`F\ [LT^{-1}]`)

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P-Q-F \\
   & Q=\frac{x_3^{1-\gamma}}{(\gamma-1)}S^{\gamma} \\
   & F = \frac{x_2}{x_3^{\omega}}S^{\omega}

Snow reservoir (Thur model HESS)
********************************

This reservoir is part of the model used in for the Thur catchment and it is
used to simulate snow processes. Further details are provided in the page
:ref:`thur_case_study`.

.. code-block:: python

   from superflexpy.implementation.elements.thur_model_hess import SnowReservoir

Inputs
......

- Precipitation (:math:`P\ [LT^{-1}]`)
- Temperature (:math:`T\ [°C]`)

Main outputs
............

- Sum of snow melt and rainfall input (:math:`=P-P_{\textrm{snow}}+M\ [LT^{-1}]`)

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P_{\textrm{snow}}-M \\
   & P_{\textrm{snow}}=P\quad\textrm{if } T\leq T_0;\quad\textrm{else } 0 \\
   & M = M_{\textrm{pot}}\left(1-\exp\left(-\frac{S}{m}\right)\right) \\
   & M_{\textrm{pot}}=kT\quad\textrm{if } T\geq T_0;\quad\textrm{else } 0 \\

Unsaturated reservoir (inspired to HBV)
***************************************

This is a reservoir, inspired do the family of HBV-like models, where the
output is a smoothed threshold function of the state. The name "unsaturated"
derives from its common application to represent soil dynamics.

.. code-block:: python

   from superflexpy.implementation.elements.hbv import UnsaturatedReservoir

Inputs
......

- Precipitation (:math:`P\ [LT^{-1}]`)
- Potential evapotranspiration (:math:`E_{\textrm{pot}}\ [LT^{-1}]`)

Main outputs
............

- Total outflow (:math:`Q\ [LT^{-1}]`)

Secondary outputs
.................

- Actual evapotranspiration (:math:`E_{\textrm{act}}`) :code:`get_AET()`

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P - E_{\textrm{act}} - Q \\
   & \overline{S} = \frac{S}{S_{\textrm{max}}} \\
   & E_{\textrm{act}}=C_{\textrm{e}}E_{\textrm{pot}}\left(\frac{\overline{S}(1+m)}{\overline{S}+m}\right) \\
   & Q=P\left(\overline{S}\right)^{\beta}

Upper zone (Hymod)
******************

This reservoir is part of the Hymod model and it is used to simulate th upper
zone. Further details are provided in the page :ref:`hymod`.

.. code-block:: python

   from superflexpy.implementation.elements.hymod import UpperZone

Inputs
......

- Precipitation (:math:`P\ [LT^{-1}]`)
- Potential evapotranspiration (:math:`E_{\textrm{pot}}\ [LT^{-1}]`)

Main outputs
............

- Total outflow (:math:`Q\ [LT^{-1}]`)

Secondary outputs
.................

- Actual evapotranspiration (:math:`E_{\textrm{act}}\ [LT^{-1}]`) :code:`get_AET()`

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P - E_{\textrm{act}} - Q \\
   & \overline{S} = \frac{S}{S_{\textrm{max}}} \\
   & E_{\textrm{act}}=E_{\textrm{pot}}\left(\frac{\overline{S}(1+m)}{\overline{S}+m}\right) \\
   & Q=P\left(1-\left(1-\overline{S}\right)^{\beta}\right)

Lag elements
------------

All the lag elements implemented in SuperflexPy are designed to take an
arbitrary number of input fluxes and to apply a convolution to them based on a
weight array, which defines the shape of the lag function.

Different lag elements differ only in the choice of the weight array.

.. image:: pics/elements_list/lag.png
   :align: center

One method to define the weight array is to define first the area underneath
the lag function as a function of the time coordinate and of the total length
of the lag :math:`t_{\textrm{lag}}`. The weights can, then, be calculated by
difference between the values of the area as the various time steps. This is
shown in the figure where the weight :math:`W_i` is calculated as the difference
of the areas :math:`A_i` and :math:`A_{i-1}`.

..
    Please use the following template

    Name of the element (Model)
    ***************************

    Import

    Equation used for the lag
    .........................

    Import path
    ...........

Half triangular lag (Thur model HESS)
*************************************

This lag element implements the element present in the case study
:ref:`thur_case_study`.

.. code-block:: python

   from superflexpy.implementation.elements.thur_model_hess import HalfTriangularLag

Equation used for calculating the weight array
..............................................

The area of the lag is calculated with the following expression

.. math::

   &A_{\textrm{lag}}(t) = 0 & \quad \textrm{for } t \leq 0\\
   &A_{\textrm{lag}}(t) = \left(\frac{t}{t_{\textrm{lag}}}\right)^2 & \quad \textrm{for } 0< t \leq t_{\textrm{lag}}\\
   &A_{\textrm{lag}}(t) = 1 & \quad \textrm{for } t > t_{\textrm{lag}}

The weight array is then calculated as the difference between the value of
:math:`A_{\textrm{lag}}` at two adjacent points.

.. math::

   w(t_{\textrm{i}}) = A_{\textrm{lag}}(t_{\textrm{i}}) - A_{\textrm{lag}}(t_{\textrm{i-1}})

Unit hydrograph 1 (GR4J)
************************

This lag element implements the unit hydrograph of :ref:`gr4j_example`.

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import UnitHydrograph1

Equation used for calculating the weight array
..............................................

The area of the lag is calculated with the following expression

.. math::

   &A_{\textrm{lag}}(t) = 0 & \quad \textrm{for } t \leq 0\\
   &A_{\textrm{lag}}(t) = \left(\frac{t}{t_{\textrm{lag}}}\right)^\frac{5}{2} & \quad \textrm{for } 0< t \leq t_{\textrm{lag}}\\
   &A_{\textrm{lag}}(t) = 1 & \quad \textrm{for } t > t_{\textrm{lag}}

The weight array is then calculated as the difference between the value of
:math:`A_{\textrm{lag}}` at two adjacent points.

.. math::

   w(t_{\textrm{i}}) = A_{\textrm{lag}}(t_{\textrm{i}}) - A_{\textrm{lag}}(t_{\textrm{i-1}})

Unit hydrograph 2 (GR4J)
************************

This lag element implements the unit hydrograph of :ref:`gr4j_example`.

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import UnitHydrograph2

Equation used for calculating the weight array
..............................................

The area of the lag is calculated with the following expression

.. math::

   &A_{\textrm{lag}}(t) = 0 & \quad \textrm{for } t \leq 0\\
   &A_{\textrm{lag}}(t) = \frac{1}{2}\left(\frac{2t}{t_{\textrm{lag}}}\right)^\frac{5}{2} & \quad \textrm{for } 0< t \leq \frac{t_{\textrm{lag}}}{2}\\
   &A_{\textrm{lag}}(t) = 1 - \frac{1}{2}\left(2-\frac{2t}{t_{\textrm{lag}}}\right)^\frac{5}{2} & \quad \textrm{for } \frac{t_{\textrm{lag}}}{2}< t \leq t_{\textrm{lag}}\\
   &A_{\textrm{lag}}(t) = 1 & \quad \textrm{for } t > t_{\textrm{lag}}

The weight array is then calculated as the difference between the value of
:math:`A_{\textrm{lag}}` at two adjacent points.

.. math::

   w(t_{\textrm{i}}) = A_{\textrm{lag}}(t_{\textrm{i}}) - A_{\textrm{lag}}(t_{\textrm{i-1}})

Connections
-----------

SuperflexPy implements four connection elements:

- splitter
- junction
- linker
- transparent element

All of them are designed to operate with an infinite number of fluxes and,
when possible, with infinite upstream or downstream elements.

Apart from those, there are also some connectors that have been implemented as
part of a specific configuration, to achieve a particular design. Such elements
are listed in this section.

Flux aggregator (GR4J)
**********************

This element is part of the GR4J model and it is used to aggregate the fluxes to
calculate the output of the unit. Further details are provided in the page
:ref:`gr4j_example`.

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import FluxAggregator

Inputs
......

- Outflow routing store (:math:`Q_{\textrm{RR}}\ [LT^{-1}]`)
- Exchange flux (:math:`Q_{\textrm{RF}}\ [LT^{-1}]`)
- Outflow UH2 (:math:`Q_{\textrm{UH2}}\ [LT^{-1}]`)

Main outputs
............

- Outflow (:math:`Q\ [LT^{-1}]`)

Governing equations
...................

.. math::
   & Q = Q_{\textrm{RR}} + \max(0;Q_{\textrm{UH2}} - Q_{\textrm{RF}}) \\