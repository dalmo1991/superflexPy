.. note:: Last update 06/10/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _case_studies:

Case studies
============

This page describes the model configurations used in publications.

.. _thur_case_study:

Dal Molin et al., 2020, HESS
----------------------------

This section describes the implementation of the semi-distributed hydrological
model M02 presented in the article:

   Dal Molin, M., Schirmer, M., Zappa, M., and Fenicia, F.: **Understanding**
   **dominant controls on streamflow spatial variability to set up a**
   **semi-distributed hydrological model: the case study of the Thur**
   **catchment**, Hydrol. Earth Syst. Sci., 24, 1319–1345,
   https://doi.org/10.5194/hess-24-1319-2020, 2020.

In this application, the Thur catchment has been divided in 10 subcatchments
and 2 hydrological response units (HRUs). Please refer to the article for the
details; here we only show the SuperflexPy code needed to reproduce the model
from the publication.

Model structure
...............

The two HRUs are represented using the same model structure, shown in the
figure.

.. image:: pics/case_studies/model_structure_thur.png
   :align: center

This model structure is similar to :ref:`hymod`; its implementation using
SuperflexPy is presented next

.. image:: pics/case_studies/ThurHESS2020.png
   :align: center

Note that the temperature is treated as an input. This choice is not forced by
the framework but is convenient in this particular case, where it is the first
element that needs it. Since the temperature is node-specific, an alternative
solution would have been to design the snow reservoir such that the temperature
is one of its state variables. This solution would have been preferable if the
snow reservoir was not at the beginning of the structure: inputs are assigned to
the element in the first layer of the unit and have then to "flow" through all
the elements until they reach the element where they are needed; this would
require all the elements upstream to be able to handle (i.e. to input and
output) that input, which is not common in the case of the temperature.

The division of the Thur catchment in units (HRUs) and nodes (subcatchments) is
represented in the figure

.. image:: pics/case_studies/ThurSchemeNodes.png
   :align: center

Defining the elements
.....................

All the elements already exists; therefore they just need to be imported.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 5-6, 10, 11
   :linenos:

Next, all elements must be initialized, defining the initial state and the
parameter values.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 13-15, 17-96
   :linenos:

Defining the HRUs structure
...........................

Once all elements are initialized, we can connect them and create the two units
that represent the HRUs.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 98-124
   :linenos:

Defining the catchments
.......................

Now that the units (HRUs) are initialized, we need to assign them to the nodes
(catchments).

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 126-194
   :linenos:

Note that all the nodes incorporate the information about their :code:`area`,
which is used by the network to calculate their contribution to the outflow
(larger the area, bigger the contribution).

There is no requirement for a node to contain all units. I a unit is not present
in a node (e.g. unconsolidated in Mosnang, line 50) it can be simply omitted.

Defining the network
....................

The last step consists in creating the network that connects all the nodes
previously initialized.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 196-221
   :linenos:

Running the model
.................

Now that all the components have been initialized, we can run the model.

The first step is to assign the input fluxes to the single nodes (catchments).
For this we assume that the data is available as a Pandas DataFrame and that the
columns are named :code:`P_name_of_the_catchment`,
:code:`T_name_of_the_catchment`, and :code:`PET_name_of_the_catchment`.

The inputs can be set using a :code:`for` loop

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 253-258
   :linenos:

Finally, we set the model time step. This can be done directly at the network
level which automatically sets it to all components.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 260
   :linenos:

We can now run the model.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 262
   :linenos: