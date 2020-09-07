.. note:: Last update 26/06/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _customize_components:

Expand SuperflexPy: modify the existing components
==================================================

.. _routing_node:

Adding the routing to a node
----------------------------

The nodes in SuperflexPy are designed to provide the possibility of simulating
the routing process that may happen in a catchment. The routing is a delay
in the fluxes that comes from their propagation within the catchment (internal
routing) and in the river network (external routing).

The default implementation of the node (:code:`Node` class in
:code:`superflexpy.framework.node`) does not provide the routing functionality.
Although the methods :code:`_internal_routing` and :code:`external_routing`
exist and are integrate in the code, their implementation simply returns
the incoming fluxes without any transformation.

The modeller that wants to implement the routing, therefore, has to implement
a customized node that implements those two methods. The object-oriented
design of SuperflexPy simplifies this operation since the new node class will
inherit all the methods from the original class and has to overwrite only the
two that are responsible of the routing.

We propose here an implementation of the routing that uses a lag function that
has the shape of an isosceles triangle with base :code:`t_internal` and
:code:`t_external`, for internal and external routing respectively. The
implementation is similar to the case of the :ref:`build_lag`.

The first step to do in the implementation is to import the :code:`Node`
component from SuperflexPy and implement the class :code:`RoutedNode` with the
following code

.. literalinclude:: customize_components_code.py
   :language: python
   :lines: 1, 4, 5
   :linenos:

We then need to implement the methods :code:`_internal_routing` and
:code:`external_routing`. Both the methods receive, as input, a list of fluxes
and return, as output, the same list of fluxes with the delay applied.

.. literalinclude:: customize_components_code.py
   :language: python
   :lines: 13-31
   :linenos:

Since, in this simple example, the two routing mechanisms are handled using the
same lag function, the methods take advantage of the method :code:`_route`
(line 7 and 17) to handle the routing.

The method is implemented with the following code

.. literalinclude:: customize_components_code.py
   :language: python
   :lines: 33-73
   :linenos:

Note that all the code in this block is highly similar to the one implemented
in :code:`RoutedNode` and that, for the implementation of the routing, the only
two methods that are strictly necessary are :code:`_internal_routing` and
:code:`external_routing` while all the others are only "support methods" to
these two, needed only to make the code more organized and easier to maintain.