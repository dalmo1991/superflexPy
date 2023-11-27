.. note:: Last update 04/05/2021

.. _tests:

Automated testing
=================

Current testing of SuperflexPy consists of validating its numerical results
against the original implementation of
`Superflex <https://doi.org/10.1029/2010WR010174>`_. This testing is done for
selected model configurations and selected sets of parameters and inputs.

This testing strategy implicitly checks auxiliary methods, including setting
parameters and states, retrieving the internal fluxes of the model, setting
inputs and getting outputs, etc..

The testing code is contained in folder :code:`test` and uses the Python module
:code:`unittest`. The folder contains :code:`reference_results`
and :code:`unittest` containing the scripts that run the tests.

Current testing covers:

- Specific elements (reservoirs and lag functions) that
  are implemented in Superflex (e.g. :code:`01_FR.py`, :code:`02_UR.py`);
- Multiple elements in a unit (e.g.
  :code:`03_UR_FR.py`, :code:`04_UR_FR_SR.py`);
- Multiple units in a node (e.g. :code:`05_2HRUs.py`);
- Multiple nodes inside a network (e.g.
  :code:`06_3Cats_2HRUs.py`);
- Auxiliary methods, which are tested implicitly, i.e. assuming that
  errors in the auxiliary methods propagate to the results.

Current testing does not cover:

- Elements for which numerical results are not available (e.g. some components
  of GR4J);
- Usage of the Explicit Euler solver;
- Edge cases (e.g. extreme values of parameters and states)

Users contributing SuperflexPy extensions should provide reference
results and the code that tests them (including input data and model parameter
values).

As the SuperflexPy framework continues to develop, additional facilities for
unit-testing and integrated-testing will be employed.

Automation
----------

Any push of new code to any branch on the github repository will trigger
automatic testing based on the scripts contained in the folder
:code:`test/unittest`.
