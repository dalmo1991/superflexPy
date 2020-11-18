.. note:: Last update 18/11/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _installation_label:

Installation
============

SuperflexPy is implemented using Python 3 (version 3.7.3). It is not compatible
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

- `Numpy <https://docs.scipy.org/doc/numpy/user/install.html>`_
- `Numba <https://numba.pydata.org/numba-doc/dev/user/installing.html>`_

All the packages are available through pip and will be installed automatically
when installing SuperflexPy.

Note that Numba is required only if the modeler wishes to use the Numba
optimized implementation of the numerical solvers. GPU acceleration (CUDA) is
currently not supported but will be explored in future versions.