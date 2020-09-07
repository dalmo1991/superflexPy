.. TODO
.. - check if complete
.. - review

.. note:: Last update 26/06/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _elements_list:

Elements list
=============

This page contains all the elements implemented as part of SuperflexPy. The
elements are divided in three categories

- Reservoir
- Lag functions
- Connectors

We will now list all the elements in alphabetical order.

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

Fast reservoir (HBV)
********************

.. code-block:: python

   from superflexpy.implementation.elements.hbv import FastReservoir

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P - Q \\
   & Q=kS^{\alpha}

Inputs required
...............

- Precipitation

Main outputs
............

- Total outflow

Interception filter (GR4J)
**************************

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import InterceptionFilter

Governing equations
...................

.. math::
   & \textrm{if } P^{\textrm{in}} > E^{\textrm{in}}_{\textrm{POT}}: \\
   & \quad P^{\textrm{out}} = P^{\textrm{in}} - E^{\textrm{in}}_{\textrm{POT}} \\
   & \quad E^{\textrm{out}}_{\textrm{POT}} = 0 \\ \\
   & \textrm{if } P^{\textrm{in}} < E^{\textrm{in}}_{\textrm{POT}}: \\
   & \quad P^{\textrm{out}} = 0 \\
   & \quad E^{\textrm{out}}_{\textrm{POT}} = E^{\textrm{in}}_{\textrm{POT}} - P^{\textrm{in}}

Inputs required
...............

- Potential evapotranspiration
- Precipitation

Main outputs
............

- Net potential evapotranspiration
- Net precipitation

Linear reservoir (Hymod)
************************

.. code-block:: python

   from superflexpy.implementation.elements.hymod import LinearReservoir

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P - Q \\
   & Q=kS

Inputs required
...............

- Precipitation

Main outputs
............

- Total outflow

Production store (GR4J)
***********************

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import ProductionStore

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P_{\textrm{s}}-E_{\textrm{act}}-Perc \\
   & P_{\textrm{s}}=P\left(1-\left(\frac{S}{x_1}\right)^\alpha\right) \\
   & E_{\textrm{act}}=E_{\textrm{pot}}\left(2\frac{S}{x_1}-\left(\frac{S}{x_1}\right)^\alpha\right) \\
   & Perc = \frac{x^{1-\beta}}{(\beta-1)\textrm{d}t}\nu^{\beta-1}S^{\beta} \\
   & P_{\textrm{r}}=P - P_{\textrm{s}} + Perc

Inputs required
...............

- Potential evapotranspiration
- Precipitation

Main outputs
............

- Total outflow (:math:`P_{\textrm{r}}`)

Secondary outputs
.................

- Actual evapotranspiration (:math:`E_{\textrm{act}}`)

Routing store (GR4J)
********************

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import RoutingStore

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P-Q-F \\
   & Q=\frac{x_3^{1-\gamma}}{(\gamma-1)\textrm{d}t}S^{\gamma} \\
   & F = \frac{x_2}{x_3^{\omega}}S^{\omega}

Inputs required
...............
- Precipitation

Main outputs
............
- Outflow (:math:`Q`)
- Loss term (:math:`F`)

Snow reservoir (Thur model HESS)
********************************

.. code-block:: python

   from superflexpy.implementation.elements.thur_model_hess import SnowReservoir

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=Sn-M \\
   & Sn=P\quad\textrm{if } T\leq T_0;\quad\textrm{else } 0 \\
   & M = M_{\textrm{pot}}\left(1-\exp\left(-\frac{S}{m}\right)\right) \\
   & M_{\textrm{pot}}=kT\quad\textrm{if } T\geq T_0;\quad\textrm{else } 0 \\

Inputs required
...............

- Precipitation (total, the separation between snow and rain is done
  internally)
- Temperature

Main outputs
............

- Melt + rainfall input

Unsaturated reservoir (HBV)
***************************

.. code-block:: python

   from superflexpy.implementation.elements.hbv import UnsaturatedReservoir

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P - E_{\textrm{act}} - Q \\
   & E_{\textrm{act}}=C_{\textrm{e}}E_{\textrm{pot}}\left(\frac{\left(\frac{S}{S_{\textrm{max}}}\right)(1+m)}{\frac{S}{S_{\textrm{max}}}+m}\right) \\
   & Q=P\left(\frac{S}{S_{\textrm{max}}}\right)^{\beta}

Inputs required
...............

- Precipitation
- Potential evapotranspiration

Main outputs
............

- Total outflow

Secondary outputs
.................

- Actual evapotranspiration

Upper zone (Hymod)
******************

.. code-block:: python

   from superflexpy.implementation.elements.hymod import UpperZone

Governing equations
...................

.. math::
   & \frac{\textrm{d}S}{\textrm{d}{t}}=P - E_{\textrm{act}} - Q \\
   & E_{\textrm{act}}=E_{\textrm{pot}}\left(\frac{\left(\frac{S}{S_{\textrm{max}}}\right)(1+m)}{\frac{S}{S_{\textrm{max}}}+m}\right) \\
   & Q=P\left(1-\left(1-\frac{S}{S_{\textrm{max}}}\right)^{\beta}\right)

Inputs required
...............

- Precipitation
- Potential evapotranspiration

Main outputs
............

- Total outflow

Secondary outputs
.................

- Actual evapotranspiration


Lag functions
-------------

All the lag functions implemented in SuperflexPy are designed to take an
arbitrary number of input fluxes and to apply a transformation to it based on
a weight array that defines the shape of the lag function. It is only this that
differentiate different lag functions.

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

.. code-block:: python

   from superflexpy.implementation.elements.thur_model_hess import HalfTriangularLag

Equation used for the lag
.........................

The area of the lag is calculated with the following expression

.. math::

   &A_{\textrm{lag}}(t) = 0 & \quad \textrm{for } t \leq 0\\
   &A_{\textrm{lag}}(t) = \left(\frac{t}{t_{\textrm{lag}}}\right)^2 & \quad \textrm{for } 0< t \leq t_{\textrm{lag}}\\
   &A_{\textrm{lag}}(t) = 1 & \quad \textrm{for } t > t_{\textrm{lag}}

The weight array is then calculated as the difference between the value of
:math:`A_{\textrm{lag}}` at two adjacent points.

.. math::

   w(t_{\textrm{j}}) = A_{\textrm{lag}}(t_{\textrm{j}}) - A_{\textrm{lag}}(t_{\textrm{j-1}})

Unit hydrograph 1 (GR4J)
************************

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import UnitHydrograph1

Equation used for the lag
.........................

The area of the lag is calculated with the following expression

.. math::

   &A_{\textrm{lag}}(t) = 0 & \quad \textrm{for } t \leq 0\\
   &A_{\textrm{lag}}(t) = \left(\frac{t}{t_{\textrm{lag}}}\right)^\frac{5}{2} & \quad \textrm{for } 0< t \leq t_{\textrm{lag}}\\
   &A_{\textrm{lag}}(t) = 1 & \quad \textrm{for } t > t_{\textrm{lag}}

The weight array is then calculated as the difference between the value of
:math:`A_{\textrm{lag}}` at two adjacent points.

.. math::

   w(t_{\textrm{j}}) = A_{\textrm{lag}}(t_{\textrm{j}}) - A_{\textrm{lag}}(t_{\textrm{j-1}})

Unit hydrograph 2 (GR4J)
************************

.. code-block:: python

   from superflexpy.implementation.elements.gr4j import UnitHydrograph2

Equation used for the lag
.........................

The area of the lag is calculated with the following expression

.. math::

   &A_{\textrm{lag}}(t) = 0 & \quad \textrm{for } t \leq 0\\
   &A_{\textrm{lag}}(t) = \frac{1}{2}\left(\frac{2t}{t_{\textrm{lag}}}\right)^\frac{5}{2} & \quad \textrm{for } 0< t \leq \frac{t_{\textrm{lag}}}{2}\\
   &A_{\textrm{lag}}(t) = 1 - \frac{1}{2}\left(2-\frac{2t}{t_{\textrm{lag}}}\right)^\frac{5}{2} & \quad \textrm{for } \frac{t_{\textrm{lag}}}{2}< t \leq t_{\textrm{lag}}\\
   &A_{\textrm{lag}}(t) = 1 & \quad \textrm{for } t > t_{\textrm{lag}}

The weight array is then calculated as the difference between the value of
:math:`A_{\textrm{lag}}` at two adjacent points.

.. math::

   w(t_{\textrm{j}}) = A_{\textrm{lag}}(t_{\textrm{j}}) - A_{\textrm{lag}}(t_{\textrm{j-1}})

Connectors
----------

SuperflexPy implements, by default four different connectors:

- splitter
- junction
- linker
- transparent element

All of them are designed to operate with an infinite number of fluxes and,
when possible, with infinite upstream or downstream elements.

Apart from those, there are also some connectors that have been implemented as
part of a specific configuration, to achieve a particular design.

.. flux aggregator of GR4J