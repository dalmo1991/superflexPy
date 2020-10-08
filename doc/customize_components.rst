.. note:: Last update 06/10/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _customize_components:

Expand SuperflexPy: modify existing components
==============================================

.. _routing_node:

Adding routing to a node
------------------------

Nodes in SuperflexPy have the possibility of adding additional lag to the fluxes
simulated by the units. This is done because, when using nodes to represent
catchment, it may be beneficial to be able to simulate routing process. The
routing is a delay in the fluxes as they propagate through the catchment
(internal routing) and through the river network (external routing).

The default implementation of the node (:code:`Node` class in
:code:`superflexpy.framework.node`) does not provide the routing functionality.
Although the methods :code:`_internal_routing` and :code:`external_routing`
exist and are integrated in the code, they simply return the incoming fluxes
without any transformation.

The modeller who wants to implement the routing, therefore, has to implement
a customized node that implements those two methods. The object-oriented
design of SuperflexPy simplifies this operation since the new node class will
inherit all the methods from the original class, and has to overwrite only the
two methods that are responsible for the routing.

We propose here an implementation of the routing that uses a lag function that
has the shape of an isosceles triangle with base :code:`t_internal` and
:code:`t_external`, for internal and external routing respectively. The
implementation is similar to the case of the :ref:`build_lag`.

The first step is to import the :code:`Node` component from SuperflexPy and
define the class :code:`RoutedNode` with the following code

.. literalinclude:: customize_components_code.py
   :language: python
   :lines: 1, 4, 5
   :linenos:

We then need to implement the methods :code:`_internal_routing` and
:code:`external_routing`. Both methods receive, as input, a list of fluxes
and return, as output, the same list of fluxes with the delay applied.

.. literalinclude:: customize_components_code.py
   :language: python
   :lines: 13-31
   :linenos:

In this simple example, the two routing mechanisms are handled using the same
lag function. Hence, the methods take advantage of the method :code:`_route`
(line 7 and 17) to simulate the routing.

The method is implemented with the following code

.. literalinclude:: customize_components_code.py
   :language: python
   :lines: 33-73
   :linenos:

Note that the code in this block is similar to the one implemented in
:ref:`build_lag`.  The methods in this last block are "support methods" used
only to make the code more organized and easier to maintain. A similar result
can be obtained moving the functionality of these methods into
:code:`_internal_routing` and :code:`external_routing`.
