.. note:: Last update 04/05/2021

Sharing model configurations
============================

A key goal of SuperflexPy is to facilitate collaboration between research
groups, and to help compare and improve modelling solutions. To this end, users
can share model configurations that can be imported and run by other users. Note
that models built with SuperflexPy are Python objects that, once initialized,
can be imported into other scripts.

A user who wishes to share their model configuration with the community can
create a Python script (with a descriptive name) that initializes the model
(without running it) and "upload" it to the GitHub repository in the folder
:code:`superflexpy/implementation/models/`. This "upload" requires the following steps: (1)
fork the `SuperflexPy <https://github.com/dalmo1991/superflexPy>`_
repository, (2) add the script to the local fork of the repository, and (3)
make a pull request to the original repository (see :ref:`contribute` for
further details). The contributed code will be checked by the repository maintainers. Assuming all checks
are passed the newly incorporated code will be incorporated in the following release of SuperflexPy
and thus made available to other SuperflexPy users.

The user will maintain authorship on the contributed code, which will be
released with the same :ref:`license` as SuperflexPy. It is good practice to
include unit tests to enable users to ensure the new code is operating as expected (see :ref:`tests`).

Practical example with M4
-------------------------

We illustrate of how to distribute SuperflexPy models to colleagues using as an
example the model :ref:`M4_example`.

First, we create the file :code:`m4_sf_2011.py` that contains the code to
initialize the model

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 1-29
   :linenos:

Then we incorporate the file :code:`m4_sf_2011.py` into the SuperflexPy repository in the folder
:code:`superflexpy/implementation/models/` following the steps illustrated
in the previous section (fork, change, and pull request).

Once the next release of SuperflexPy is available, the M4 model implementation
will be available in the updated installed package.
General users can then use this new model in their own application, by importing it as shown below.

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 31-37
   :linenos:

Sharing models "privately" with other users
-------------------------------------------

Model configurations can be shared "privately" between research groups without
waiting for a new release of the framework.

This can be done by creating a :code:`my_new_model.py` file that initializes the
model and then sharing the file "privately" with other users.

The recipients of the new file can then save it on their machines and use
local importing. Assuming that the script that the recipients use to run the
model is in the same folder as the file initializing the model, the new model can be used as follows

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 39, 32, 32-37
   :linenos:

Note the local import in line 1.

As we believe in the `F.A.I.R. <https://www.go-fair.org/fair-principles/>`_
principles, we encourage modelers to share their models with the whole
community, using the procedure detailed earlier.

Dumping objects with Pickle
---------------------------

Python offers the module
`Pickle <https://docs.python.org/3/library/pickle.html>`_ to serialize objects
to binary files.  This approach enables the distribution of binary files, but
has the disadvantage of lacking transparency in the model structure.
