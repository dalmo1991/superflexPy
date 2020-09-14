.. note:: Last update 11/09/2020

Sharing model configurations
============================

The ultimate goal of SuperflexPy is to facilitate collaboration between research
groups and favor the comparison between existing modelling solutions. To this
end, users can share model configurations that can be imported and run by other
users.

The user that wants to share his model configuration with the community (from a
single element to a network) must create a Python script (with a meaningful
name) that initializes the model (without running it) and put it in the folder
:code:`superflexpy/implementation/models/`. The code will be incorporated in the
following release of SuperflexPy and, therefore, other users can simply import
it.

This is possible because, eventually, models built with SuperflexPy are Python
objects that can be imported in other scripts.

Practical example with M4
-------------------------

We provide here an example of how to distribute the model :ref:`M4_example`.

To do so, we have to create the file :code:`m4_sf_2011.py` and put it in the
folder :code:`superflexpy/implementation/models/`. The content of the file is:

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 1-29
   :linenos:

Once the new release of SuperflexPy is available, another user will find this
implementation in the installed package and can import it for another
application, as shown in the example.

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 31-37
   :linenos:

Sharing models privately
------------------------

Although we discourage this choice since we believe in the
`F.A.I.R. <https://www.go-fair.org/fair-principles/>`_ principles, model
configurations can be shared "privately" between research groups without waiting
for a new release of the framework (which, anyway, should be a quick process).

This can be done exactly as shown before, creating a :code:`.py` file that
initializes the model and share the file privately with other users.

The users will then save the file in their computer and use local importing.
Assuming that the script that runs the model is in the same folder of the file
initializing the model (called :code:`m4_sf_2011.py`), the user will use
the model as follows

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 39, 32, 32-37
   :linenos:

Dumping objects with Pickle
---------------------------

Python offers the module
`Pickle <https://docs.python.org/3/library/pickle.html>`_ to serialize objects
to binary files. We discourage this practice due to the lack of transparency in
the shared model.