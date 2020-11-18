.. note:: Last update 18/11/2020

.. _tests:

Automated testing
=================

Current testing consists of validating the numerical results of SuperflexPy
against the original implementation of
`Superflex <https://doi.org/10.1029/2010WR010174>`_ for selected model
configurations and sets of parameters and inputs.

This testing strategy implicitly checks auxiliary methods (e.g. setting
parameters and states, retrieving the internal fluxes of the model, setting
inputs and getting outputs, etc.).

The testing code is contained in folder :code:`test/` and uses the Python module
:code:`unittest`. The folder contains :code:`reference_results/` (so far only
from Superflex) and :code:`unittest/` containing the scripts that run the tests.

Current testing covers:

- Correct functionality of specific elements (reservoirs and lag functions) that
  are implemented in Superflex (e.g. :code:`01_FR.py`, :code:`02_UR.py`);
- Correct functionality of multiple elements in a unit (e.g.
  :code:`03_UR_FR.py`, :code:`04_UR_FR_SR.py`);
- Correct functionality of multiple units in a node (e.g. :code:`05_2HRUs.py`);
- Correct functionality of multiple nodes inside a network (e.g.
  :code:`06_3Cats_2HRUs.py`);
- Correct functionality of auxiliary methods (implicit testing, i.e. in case of
  malfunctioning errors propagate to the results).

Current testing does not cover:

- Elements for which numerical results are not available (e.g. some components
  of GR4J);
- Usage of the Explicit Euler solver;
- Edge cases (e.g. extreme values of parameters and states)

Users contributing to SuperflexPy creating new elements should provide reference
results and the code that tests them (including input data and model parameter
values).

As the SuperflexPy framework continues to develop, additional facilities for
unit-testing and integrated-testing will be employed.

Automation
----------

Any push of new code to any branch on the github repository will trigger
automatic testing based on the scripts contained in the folder
:code:`test/unittest`.