.. note:: Last update 08/10/2020

Sharing model configurations
============================

The ultimate goal of SuperflexPy is to facilitate collaboration between research
groups and help compare and improve modelling solutions. To this end, users can
share model configurations that can be imported and run by other users. Note
that, models built with SuperflexPy are Python objects that, once initialized,
can be imported in other scripts.

A user who wants to share their model configuration with the community can
create a Python script (with a meaningful name) that initializes the model
(without running it) and put it in the folder
:code:`superflexpy/implementation/models/`. The contributed code will be
incorporated in the following release of SuperflexPy and, therefore, other users
will be able to import it.

The user will maintain authorship on the contributed code.

Practical example with M4
-------------------------

We provide an example of how to distribute the model :ref:`M4_example`.

First, we create the file :code:`m4_sf_2011.py` that contains the code to
initialize the model

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 1-29
   :linenos:

Then we incorporate it in the SuperflexPy repository (see :ref:`contribute`) in
the folder :code:`superflexpy/implementation/models/`.

Once the next release of SuperflexPy is available, another user will find this
implementation in the updated installed package and can import it for their own
application, as shown below.

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 31-37
   :linenos:

Sharing models privately
------------------------

Although we discourage this choice since we believe in the
`F.A.I.R. <https://www.go-fair.org/fair-principles/>`_ principles, model
configurations can be shared "privately" between research groups without waiting
for a new release of the framework.

This can be done exactly by creating a :code:`my_new_model.py` file that
initializes the model and sharing the file "privately" with other users.

The recipients of the new file will then save the file in their computer and use
local importing. Assuming that the script that the recipients use to run the
model is in the same folder as the file initializing the model (named
:code:`m4_sf_2011.py`), the recipients will use the model as follows

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 39, 32, 32-37
   :linenos:

Note the local import in line 1.

Dumping objects with Pickle
---------------------------

Python offers the module
`Pickle <https://docs.python.org/3/library/pickle.html>`_ to serialize objects
to binary files. We discourage this practice due to the lack of transparency in
the shared model.