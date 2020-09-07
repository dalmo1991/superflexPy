.. note:: Last update 26/06/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _installation_label:

Installation
============

SuperflexPy has been developed and tested using Python 3 (version 3.7.4). It is
not compatible with Python 2.

SuperflexPy is available as Python package at PyPI repository, at the link
`https://pypi.org/project/superflexpy <https://pypi.org/project/superflexpy>`_

The simplest way to install SuperflexPy is using the package installer for
Python (pip) running the command

.. code-block:: bash

   pip install superflexpy

After the first installation, to upgrade to a new version run the command

.. code-block:: bash

   pip install --upgrade superflexpy

Dependencies
------------

SuperflexPy needs the following python packages to run

- `numpy <https://docs.scipy.org/doc/numpy/user/install.html>`_
- `numba <https://numba.pydata.org/numba-doc/dev/user/installing.html>`_

All the packages are available through pip.

The installation of numba is necessary only if the modeler decides to use the
numba optimized implementation of the numerical solvers. GPU acceleration (CUDA)
is not needed and, therefore, it is not supported.