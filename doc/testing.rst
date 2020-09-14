.. note:: Last update 11/09/2020

Automated testing
=================

For the first release of SuperflexPy, the testing is limited to the correctness
of the numerical results; this should spot major errors in the code and offer
some degree of validation of the model. Running the tests, implicitly checks
also the correct functionality of auxiliary methods (e.g. to set parameters and
states, to inspect the internals of the model, to set inputs and get outputs,
etc.).

Testing is done comparing numerical results of SuperflexPy with the one obtained
running `Superflex <https://doi.org/10.1029/2010WR010174>`_ for some specific
model configurations and sets of parameters and inputs.

Testing code is contained in the folder :code:`test/` and uses the module
:code:`unittest`. The folder contains :code:`reference_results/` (so far only
from Superflex) and :code:`unittest/` containing the scripts that run the tests.
Further development of the framework will possibly improve and change this
organization.

At this point, testing covers:

- Correct functionality of specific elements (reservoirs and lag functions) that
  are implemented in Superflex (e.g. :code:`01_FR.py`, :code:`02_UR.py`);
- Correct functionality of multiple elements in a unit (e.g.
  :code:`03_UR_FR.py`, :code:`04_UR_FR_SR.py`);
- Correct functionality of multiple units in a node (e.g. :code:`05_2HRUs.py`);
- Correct functionality of multiple nodes inside a network (e.g.
  :code:`06_3Cats_2HRUs.py`);
- Correct functionality of auxiliary methods (implicit testing, i.e. in case of
  malfunctioning errors propagate to the results).

Testing currently does not cover:

- Elements for witch numerical results are not available (e.g. some components
  of GR4J);
- Usage of the Explicit Euler solver;
- Corner cases (e.g. extreme values of parameters and states)

When creating new elements for SuperflexPy, some degree of testing should be
provided.

Automation
----------

Any push of new code to any branch will trigger automatic testing based on the
scripts contained in the folder :code:`test/unittest`.