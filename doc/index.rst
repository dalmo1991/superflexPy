.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. image:: pics/logo_transparent_2.png
   :align: center

===========
SuperflexPy
===========

SuperflexPy is an open-source Python framework for constructing conceptual
hydrological models for lumped and semi-distributed applications.

SuperflexPy builds on our 10-years-experience with the development and
application of `Superflex <https://doi.org/10.1029/2010WR010174>`_. The
new framework offers a brand new implementation of Superflex, allowing to build
completely customized, spatially-distributed hydrological models.

Thanks to its object-oriented architecture, SuperflexPy can be easily
extended to satisfy your own modelling requirements, including the creation of
new elements with customized internal structure, just in a few lines of Python
code.

Constructing a hydrological model is straightforward with SuperflexPy, with a
user experience similar to any other Python framework:

- inputs and outputs are handled directly by the modeler using common Python
  libraries (e.g. Numpy or Pandas for reading from text files) without the need
  of customized input files and long pre- and post-processing to adapt the data
  to the model;

- the elements of the framework are declared and initialized through a Python
  script;

- all the elements of the framework are objects with built-in functionalities
  for handling parameters and states, routing the fluxes, and solving common
  structures present in conceptual models (e.g. reservoirs, lag functions,
  etc.);

- the numerical implementation is separated from the conceptual model, allowing
  for testing different numerical methods for solving differential equations;

- the framework can be run at multiple level of complexity, from a single bucket
  to an entire river network;

- the framework can be easily interfaced with other Python modules for
  calibration and uncertainty analysis.

Team
----

SuperflexPy is actively developed at `Eawag <https://www.eawag.ch>`_,
by researchers in the `Hydrological modelling group
<https://www.eawag.ch/en/department/siam/main-focus/hydrological-modelling/>`_,
with the support of external collaborators.

The core team consists of:

- `Marco Dal Molin <https://www.eawag.ch/~dalmolma>`_ (implementation and design)

- `Dr. Fabrizio Fenicia <https://www.eawag.ch/en/aboutus/portrait/organisation/staff/profile/fabrizio-fenicia/show/>`_
  (design and supervision)

- `Prof. Dmitri Kavetski <https://www.adelaide.edu.au/directory/dmitri.kavetski>`_
  (design and supervision)

Stay in touch
-------------

If you wish to receive e-mails about future developments of the framework,
please subscribe to our mailing list `clicking here
<https://forms.gle/utLbF6KWqvqS7LHZ7>`_.

.. note:: Before starting to use SuperflexPy you should have a general knowledge
          of Python and Numpy. Other Python libraries may be needed for pre- and
          postprocessing of the data.

.. toctree::
   :maxdepth: 1
   :hidden:

   installation
   contribute
   introduction
   components
   numerical_solver
   demo
   elements_list
   build_element
   customize_components
   popular_models
   case_studies
   sfpy_in_literature
   share_models
   interfaces
   examples
   testing
   license
   reference
   changelog