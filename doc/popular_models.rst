.. TODO:
.. - Final check of correspondence with the paper

.. note:: Last update 01/09/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _popular_models:

Application: implementation of existing conceptual models
=========================================================

In this page we propose the implementation of existing conceptual hydrological
models. The translation of a model in SuperflexPy requires the following steps:

1. Design of a structure that reflects the original model but satisfy the
   requirements of SuperflexPy (e.g. does not contain mutual interaction
   between elements);
2. Extension of the framework, coding the required elements (as explained in
   the page :ref:`build_element`)
3. Construction of the model structure using the elements implemented at point 2

.. _M4_example:

M4 from Kavetski and Fenicia, WRR, 2011
---------------------------------------

M4 is a simple conceptual model presented, as part of a models comparison study,
in the article

    Kavetski, D., and F. Fenicia (2011), **Elements of a flexible approach for**
    **conceptual hydrological modeling: 2. Applicationand experimental**
    **insights**, WaterResour.Res.,47, W11511, doi:10.1029/2011WR010748.

Design of the structure
.......................

The structure of M4 is quite simple and can be implemented directly in
SuperflexPy without the need of using connection elements. The figure shows, on
the left, the structure as shown in the paper and, on the right, the SuperflexPy
implementation. as part of a models comparison study.

.. image:: pics/popular_models/M4.png
   :align: center

The upstream element, the unsaturated reservoir (UR), is designed to represent
runoff generation processes (e.g. separation between evaporation and runoff) and
it is controlled by the differential equation

.. math::
   & \frac{\textrm{d}S_{\textrm{UR}}}{\textrm{d}t} = P -
   E_{\textrm{P}} \left( \frac{\frac{S_{\textrm{UR}}}{S_{\textrm{max}}} \left(1+m\right)}{\frac{S_{\textrm{UR}}}{S_{\textrm{max}}} + m} \right) -
   P \left(\frac{S_{\textrm{UR}}}{S_{\textrm{max}}}\right)^\beta \\

The downstream element, the fast reservoir (FR), is designed to represent runoff
propagation processes (e.g. routing) and it is controlled by the differential
equation

.. math::
   & \frac{\textrm{d}S_{\textrm{FR}}}{\textrm{d}t} = P - kS_{\textrm{FR}}^\alpha \\

:math:`S_{\textrm{UR}}` and :math:`S_{\textrm{FR}}` are the states of the
reservoirs, :math:`P` is the input flux, :math:`E_{\textrm{P}}` is the potential
evapotranspiration, and :math:`S_{\textrm{max}}`, :math:`m`, :math:`\beta`,
:math:`k`, :math:`\alpha` are parameters of the model.

Elements creation
.................

We now report the code used to implement the elements designed in the
previous section. Instruction on how to use the framework to build new
elements can be found in the page :ref:`build_element`.

Note that for common applications the elements are already available (refer to
the page :ref:`elements_list`) and, therefore, the modeller does not need to
implement the code presented in this section.

Unsaturated reservoir
*********************

The element is a reservoir that can be implemented extending the
:code:`ODEsElement` class.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 581-679
   :linenos:

Fast reservoir
**************

The element is a reservoir that can be implemented extending the
:code:`ODEsElement` class.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 681-758
   :linenos:

Model initialization
....................

Now that all the elements needed have been implemented, we can put them
together to build the model structure. For details refer to :ref:`demo`.

The first step consists in initializing all the elements.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 761-776
   :linenos:

After that, the elements can be put together to create a :code:`Unit` that
reflects the structure presented in the figure.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 778-784
   :linenos:

GR4J
----

GR4J is a conceptual hydrological model originally introduced in the article

    Perrin, C., Michel, C., and Andréassian, V.: **Improvement of a**
    **parsimonious model for streamflow simulation**, Journal of Hydrology,
    279, 275-289, https://doi.org/10.1016/S0022-1694(03)00225-7, 2003.

The solution adopted here follows the "continuous state-space representation"
presented in

    Santos, L., Thirel, G., and Perrin, C.: **Continuous state-space**
    **representation of a bucket-type rainfall-runoff model: a case study**
    **with the GR4 model using state-space GR4 (version 1.0)**, Geosci. Model
    Dev., 11, 1591-1605, 10.5194/gmd-11-1591-2018, 2018.

Design of the structure
.......................

The figure shows, on the left, the model structure as proposed in Perrin et
al., 2003 and, on the right, the adaptation to SuperflexPy

.. image:: pics/popular_models/gr4j.png
   :align: center

In the original version, the potential evaporation and the precipitation
are "filtered" by an interception layer that sets the smallest of the two fluxes
to zero and the biggest to the difference between the two.

.. math::
   & \textrm{if } P > PE:  \\
   & \quad P_{\textrm{NET}} = P -PE \\
   & \quad E_{\textrm{NET}}=0 \\
   & \textrm{else}: \\
   & \quad P_{\textrm{NET}} = 0 \\
   & \quad E_{\textrm{NET}}=PE-P \\

This element is reproduced identically in the SuperflexPy implementation by the
"interception filter"

In the original model, the precipitation is split between a portion :math:`P_s`
that flows into the production store and the remaining part :math:`P_b` that
bypasses the reservoir. Since :math:`P_s` and :math:`P_b` are function of the
state of the reservoir

.. math::
   & P_s=P_{\textrm{NET}}\left(1-\left(\frac{S_{\textrm{UR}}}{x_1}\right)^{\alpha}\right) \\
   & P_b=P_{\textrm{NET}}\left(\frac{S_{\textrm{UR}}}{x_1}\right)^{\alpha} \\

when we implement this part of the model in SuperflexPy, these two fluxes
cannot be calculated before solving the reservoir. For this reason, in the
SuperflexPy implementation of GR4J, all the precipitation flows into an element
that incorporates the production store; this element takes care of dividing the
precipitation internally, while solving the differential equation

.. math::
   & \frac{\textrm{d}S_{\textrm{UR}}}{\textrm{d}t} =  P_{\textrm{NET}}\left(1-\left(\frac{S_{\textrm{UR}}}{x_1}\right)^{\alpha}\right)
     - E_{\textrm{NET}}\left(2\frac{S_{\textrm{UR}}}{x_1}-\left(\frac{S_{\textrm{UR}}}{x_1}\right)^\alpha\right)-
     \frac{x_1^{1-\beta}}{(\beta-1)} \nu^{\beta-1}S_{\textrm{UR}}^\beta \\

where the first term is the precipitation :math:`P_s`, the second term is the
actual evaporation, and the third term represent the output of the reservoir,
called "percolation".

Once the reservoir is solved (i.e. the values of :math:`S_{\textrm{UR}}` that
solve the differential equation are found), the element outputs the sum of
percolation and bypassing precipitation :math:`P_b`

After this, the flux is divided between two lag functions (called "unit
hydrograph", abbreviated UH): 90% of the flux goes to UH1 while the 10% goes
to UH2. In this part of the structure there is a strict correspondence
between the elements of GR4J and their SuperflexPy implementation.

The output of UH1 represents the input of the routing store, a reservoir that
is controlled by the differential equation

.. math::
   & \frac{\textrm{d}S_{\textrm{RR}}}{\textrm{d}t}=Q_{\textrm{UH1}} -
   \frac{x_3^{1-\gamma}}{(\gamma-1)}S_{\textrm{RR}}^\gamma-
   \frac{x_2}{x_3^\omega}S_{\textrm{RR}}^\omega\\

where the second term is the output of the reservoir and the last is a
gain/loss term (called :math:`Q_{\textrm{RF}}`).

The gain/loss term :math:`Q_{\textrm{RF}}`, which is a function of the state
:math:`S_{\textrm{RR}}` of the reservoir, is subtracted also to the output of
UH2: in SuperflexPy, this operation cannot be done together with the solution of
the routing store but it is done afterwards. For this reason, the SuperflexPy
implementation of GR4J has an additional element (called "flux aggregator") that
collects (through a junction element) the output of the routing store, the
gain/loss term, and the output of UH2 and computes the outflow of the model
using the equation

.. math::
   & Q = Q_{\textrm{RR}} + \max(0;Q_{\textrm{UH2}} - Q_{\textrm{RF}}) \\

Elements creation
.................

We now report the code used to implement the elements designed in the
previous section. Instruction on how to use the framework to build new
elements can be found in the page :ref:`build_element`.

Note that for common applications the elements are already available (refer to
the page :ref:`elements_list`) and, therefore, the modeller does not need to
implement the code presented in this section.

Interception
************

The interception filter can be implemented extending the class
:code:`BaseElement`

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 11-26
   :linenos:

Production store
****************

The production store is controlled by a differential equation and, therefore,
it can be constructed extending the class :code:`ODEsElement`

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 29-130
   :linenos:

Unit hydrographs
****************

The unit hydrographs are an extension of the :code:`LagElement` and they can
be implemented with the following code

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 236-264
   :linenos:

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 267-298
   :linenos:

Routing store
*************

The routing store is an :code:`ODEsElement`

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 133-215
   :linenos:

Flux aggregator
***************

The flux aggregator can be implemented extending a :code:`BaseElement`

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 218-233
   :linenos:

Model initialization
....................

Now that all the elements needed have been implemented, we can put them
together to build the model structure. For details refer to :ref:`demo`.

The first step consists in initializing all the elements.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 300-338
   :linenos:

After that, the elements can be put together to create a :code:`Unit` that
reflects the structure presented in the figure.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 340-347
   :linenos:

.. _hymod:

HYMOD
-----

HYMOD is a conceptual hydrological model presented in the Ph.D. thesis

   Boyle, D. P. (2001). **Multicriteria calibration of hydrologic models**,
   The University of Arizona. `Link <http://hdl.handle.net/10150/290657>`_

The solution proposed here follows the model structure presented in

   Wagener, T., Boyle, D. P., Lees, M. J., Wheater, H. S., Gupta, H. V.,
   and Sorooshian, S.: **A framework for development and application of**
   **hydrological models**, Hydrol. Earth Syst. Sci., 5, 13–26,
   https://doi.org/10.5194/hess-5-13-2001, 2001.

Design of the structure
.......................

.. image:: pics/popular_models/hymod.png
   :align: center

The structure of HYMOD is composed by three blocks of reservoirs that are
designed to represent three mechanism that control the streamflow at the
catchment scale: upper zone (soil dynamics), channel routing (surface runoff),
and lower zone (subsurface flow).

As it can be seen in the figure, the original structure of HYMOD already
satisfy the design constrains of SuperflexPy and therefore it can be
implemented simply translating the single elements individually, without
the need of workarounds, as done in the case of GR4J.

The first element (upper zone) is a reservoirs intended to represent soil
dynamics that simulates streamflow generation processes and evaporation. It is
controlled by the differential equation

.. math::
   & \frac{\textrm{d}S_{\textrm{UR}}}{\textrm{d}t} = P - E -
   P \left(1 - \left(1-\frac{S_{\textrm{UR}}}{S_{\textrm{max}}}\right)^\beta\right) \\

where the first term represent the precipitation input, the second the
actual evaporation (which is equal to the potential evaporation as long as
there is sufficient storage in the reservoir) and the third the outflow of the
reservoir.

The outflow of the reservoir is then split between the channel routing and the
lower zone; these are all represented by some linear reservoirs that are
controlled by the differential equation

.. math::
   & \frac{\textrm{d}S}{\textrm{d}t} = P - kS \\

where the first term is the input of the reservoir (the outflow of the
upstream element, in this case) and the second term represent the outflow of
the reservoir.

Channel routing and lower zone differentiate one from the other by two
factors: the number of reservoirs used (3 in the first case and 1 in the
second) and by the value of the parameter :math:`k`, which controls the outflow
rate, that is bigger for the channel routing.

The output of these two branches of the model are collected together by a
junction, which sums them to generate the output of the model.

Comparing the two panels in the figure, the only difference is due to the
presence of the two transparent element that are needed to fill the gaps that,
otherwise, will be present in the structure.

Elements creation
.................

We now report the code used to implement the elements designed in the
previous section. Instruction on how to use the framework to build new
elements can be found in the page :ref:`build_element`.

Note that for common applications the elements are already available (refer to
the page :ref:`elements_list`) and, therefore, the modeller does not need to
implement the code presented in this section.

Upper zone
**********

The code used to simulate the upper zone present a change in the equation used
to calculate the actual evaporation. In the original version (Wagener et al.,
2001) the equation is "described" in the text

   *The actual evapotranspiration is equal to the potential value if*
   *sufficient soil moisture is available; otherwise it is equal to the*
   *available soil moisture content.*

which translates to the equation

.. math::
   & \textrm{if } S > 0:  \\
   & \quad E = PE \\
   & \textrm{else}: \\
   & \quad E=0 \\

Unfortunately this solution is not smooth and this can cause some computational
problems. For this reason, it has been decided to use the following equation to
calculate the potential evaporation

.. math::
   & E=PE\left( \frac{\frac{S_{\textrm{UR}}}{S_{\textrm{max}}}(1+\theta)}{\frac{S_{\textrm{UR}}}{S_{\textrm{max}}}+\theta} \right)\\

The upper zone reservoir can be implemented extending the :code:`ODEsElement`
class.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 352-450
   :linenos:

Channel routing and lower zone
******************************

All the elements belonging to the channel routing and to the lower zone are
reservoirs that can be implemented extending the :code:`ODEsElement` class.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 453-530
   :linenos:

Model initialization
....................

Now that all the elements needed have been implemented, we can put them
together to build the model structure. For details refer to :ref:`demo`.

The first step consists in initializing all the elements.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 533-570
   :linenos:

After that, the elements can be put together to create a :code:`Unit` that
reflects the structure presented in the figure.

.. literalinclude:: popular_models_code.py
   :language: python
   :lines: 572-578
   :linenos:
