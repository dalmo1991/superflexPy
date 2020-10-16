.. note:: Last update 16/10/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _installation_label:

Installation
============

SuperflexPy is implemented using Python 3 (version 3.7.4). It is not compatible
with Python 2.

SuperflexPy is available as a Python package at
`PyPI repository <https://pypi.org/project/superflexpy>`_

The simplest way to install SuperflexPy is using the package installer for
Python (pip) running the command

.. code-block:: bash

   pip install superflexpy

To upgrade to a newer version (when available), run the following command

.. code-block:: bash

   pip install --upgrade superflexpy

Dependencies
------------

SuperflexPy requires the following Python packages

- `numpy <https://docs.scipy.org/doc/numpy/user/install.html>`_
- `numba <https://numba.pydata.org/numba-doc/dev/user/installing.html>`_

All the packages are available through pip and will be installed automatically
when installing SuperflexPy.

Note that numba is required only if the modeler wishes to use the numba
optimized implementation of the numerical solvers. Given the nature of the
model, GPU acceleration (CUDA) is not beneficial (in terms of performance) and,
therefore, it is not supported.