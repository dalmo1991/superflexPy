.. note:: Last update 13/10/2020

Interfacing SuperflexPy with other frameworks
=============================================

SuperflexPy does not integrate tools for calibration or uncertainty analysis. In
this page we show an example on how a model built with SuperflexPy can be
interfaced with other tools to perform this task.

SuperflexPy + SPOTPY
--------------------

.. attention:: This example does not represent a recommendation towards the use
               of SPOTPY or of the specific calibration algorithm proposed.

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

:code:`__init__`
................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 5, 7, 29-40
   :linenos:

The class is initialized defining the SuperflexPy :code:`model` that is used.
The :code:`model`, that can be any SuperflexPy component (from reservoir to
network), must be initialized before; this class sets only the :code:`inputs` and the :code:`dt`.

Other variables necessary to initialize the class are:

- :code:`parameters` and :code:`parameters_names` that define the parameters
  considered in the calibration; the first is a list of :code:`spotpy.parameter`
  objects, the second is a list of the names of the SuperflexPy parameters;
- :code:`observations` that is an array of observed output values;
- :code:`output_index` that is the index of the output flux to be considered
  when evaluating the SuperflexPy simulation (this is particularly important in
  the case of multiple output fluxes, e.g. chemistry)

:code:`parameters`
..................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 44-45
   :linenos:

The method generates a new parameter set using SPOTPY functionalities.

:code:`simulation`
..................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 49-59
   :linenos:

The method sets the parameters (lines 3-7), resets the states to their initial
value (line 8), runs the SuperflexPy model (line 9), and returns the the output
flux for the evaluation (line 11).

:code:`evaluation`
..................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 63-64
   :linenos:

The method returns the observed flux, used to evaluate the model.

:code:`objectivefunction`
.........................

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 68-73
   :linenos:

The method defines the objective function used to evaluate the model; in this
case, Nash-Sutcliffe efficiency.

Example of use
..............

We show now how to exploit the implementation above to calibrate a lumped model
composed by 2 reservoirs.

First, we initialize the SuperflexPy model. This is done with the following code
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

:code:`P` and :code:`Q_obs` in lines 3 and 5 are arrays of precipitation (input)
and observed streamflow. In this example, we calibrate only 2 parameters
(:code:`model_FR1_k` and :code:`model_FR2_k`) out of the 4 that the SuperflexPy
model has.

Now we can perform the calibration

.. literalinclude:: interfaces_code.py
   :language: python
   :lines: 96-97
   :linenos:
