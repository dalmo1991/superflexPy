.. note:: Last update 04/09/2020

Change log
==========

Version 1.0.0
-------------

Version 1.0.0 represents the first mature release of SuperflexPy. Many things
have changed since previous 0.* releases both in terms of code organization
and conceptualization of the framework. For this reason, models built with
versions 0.* are not compatible.

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

- Added numba implementation to GR4J elements

New code
........

- Added :code:`hymod` elements