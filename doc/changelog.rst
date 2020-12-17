.. note:: Last update 18/11/2020

Change log
==========

Version 1.2.0
-------------

Major changes to existing components
....................................

- The abbreviation of "differential equation" changes, in the code, from
  :code:`dif_eq` to :code:`diff_eq`. This change regards variables names, both
  in the methods arguments and implementation.

- The class :code:`FastReservoir` has been changed to :code:`PowerReservoir`. No
  changes in the functionality of the class.

Minor changes
.............

- Testing improved.

Version 1.1.0
-------------

Major changes to existing components
....................................

- Form this version, SuperflexPy is released under license LGPL. For details,
  read :ref:`license`

Minor changes to existing components
....................................

- Bug fix on the solution of the differential equations of the reservoirs. The
  calculation of the maximum storage was not correct.

Version 1.0.0
-------------

Version 1.0.0 represents the first mature release of SuperflexPy. Many aspects
have changed since earlier 0.x releases both in terms of code organization
and conceptualization of the framework. **Models built with versions 0.x are**
**not compatible with this version and with the following releases**.

Major changes to existing components
....................................

- New numerical solver structure for elements controlled by ordinary
  differential equations (ODEs). A new component, the
  :code:`NumericaApproximator` is introduced; its task it to get the fluxes from
  the elements and construct an approximation of the ODEs. In the previous
  release of the framework the approximation was hard coded in the element
  implementation.

- :code:`ODEsElement` have now to implement the methods :code:`_fluxes` and
  :code:`_fluxes_python` instead of :code:`_differential_equation`

- Added the possibility for nodes and units to have local states and parameters.
  To this end, some internal functionalities for finding the element given the
  :code:`id` have been changed to account for the presence of states and
  parameters at a level higher then the elements.

Minor changes to existing components
....................................

- Added implicit or explicit check at initialization of units, nodes, and
  network that the components that they contain are of the right type (e.g. a
  node must contain units)

- Some minor changes to the :code:`RootFinder` to accommodate the new numerical
  implementation.

- Added Numba implementation of GR4J elements

New code
........

- Added :code:`hymod` elements