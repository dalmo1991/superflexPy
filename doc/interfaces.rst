.. note:: Last update 04/05/2021

Interfacing SuperflexPy with other frameworks
=============================================

SuperflexPy does not integrate tools for calibration or uncertainty analysis. In
this page we show an example on how a model built using SuperflexPy can be
interfaced with other tools to perform this task.

SuperflexPy + SPOTPY
--------------------

.. note:: This example is for illustration purposes only, and as such does not
          represent a specific recommendation of SPOTPY or of any specific
          calibration algorithm.

`SPOTPY <https://spotpy.readthedocs.io/en/latest/>`_ is a Python framework for
calibration, uncertainty, and sensitivity analysis.

A model can be interfaced with SPOTPY by defining a class that wraps the model
and implements the following methods:

- :code:`__init__`: initializes the class, defining some attributes;
- :code:`parameters`: returns the parameters considered in the analysis (note
  that they may not be all the parameters used by the SuperflexPy model but
  only the ones that we want to vary in the analysis);
- :code:`simulation`: returns the output of the simulation;
- :code:`evaluation`: returns the observed output;
- :code:`objectivefunction`: defines the objective function to use to evaluate
  the simulation results.

Method :code:`__init__`
.......................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 5, 7, 29-40
   :linenos:

The class :code:`spotpy_model` is initialized defining the SuperflexPy :code:`model` that is used.
The :code:`model`, which can be any SuperflexPy component (from element to
network), must be defined before; the :code:`spotpy_model` class sets only the :code:`inputs`
and the :code:`dt`.

Other variables necessary to initialize the class :code:`spotpy_model` are:

- :code:`parameters` and :code:`parameters_names`, which define the parameters
  considered in the calibration. The first variable is a list of :code:`spotpy.parameter`
  objects, the second variable is a list of the names of the SuperflexPy parameters;
- :code:`observations`, which is an array of observed output values;
- :code:`output_index`, which is the index of the output flux to be considered
  when evaluating the SuperflexPy simulation. This specification is necessary in
  the case of multiple output fluxes.

Method :code:`parameters`
.........................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 44-45
   :linenos:

The method :code:`parameters` generates a new parameter set using the SPOTPY functionalities.

Method :code:`simulation`
.........................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 49-59
   :linenos:

The method :code:`simulation` sets the parameters (lines 3-7), resets the states to their initial
value (line 8), runs the SuperflexPy model (line 9), and returns the output
flux for the evaluation of the objective function (line 11).

Method :code:`evaluation`
.........................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 63-64
   :linenos:

The method :code:`evaluation` returns the observed flux, used for the evaluation of the objective function.

Method :code:`objectivefunction`
................................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 68-73
   :linenos:

The method :code:`objectivefunction` defines the objective function used to measure the model fit to the observed data. In this
case, the Nash-Sutcliffe efficiency is used.

Example of use
..............

We now show how to employ the implementation above to calibrate a lumped model
composed of 2 reservoirs.

First, we initialize the SuperflexPy model, as follows
(see :ref:`demo` for more details on how to set-up a model).

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 1-4, 9-24
   :linenos:

Then, we initialize an instance of the :code:`spotpy_model` class

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 81-92
   :linenos:

The arrays :code:`P` and :code:`Q_obs` in lines 3 and 5 contain time series of precipitation (input)
and observed streamflow (output). In this example, lines 6-10 indicate the two parameters that we calibrate
(:code:`model_FR1_k` and :code:`model_FR2_k`) together with their range of
variability.

We can now call the SPOTPY method to calibrate the model. Here, the SCE algorithm option is used.

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 96-97
   :linenos:
