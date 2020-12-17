.. note:: Last update 18/11/2020

Sharing model configurations
============================

The ultimate goal of SuperflexPy is to facilitate collaboration between research
groups, and to help compare and improve modelling solutions. To this end, users
can share model configurations that can be imported and run by other users. Note
that, models built with SuperflexPy are Python objects that, once initialized,
can be imported in other scripts.

A user who wishes to share their model configuration with the community can
create a Python script (with a meaningful name) that initializes the model
(without running it) and "upload" it to the GitHub repository in the folder
:code:`superflexpy/implementation/models/`. This can be done as follows (1)
forking the `SuperflexPy <https://github.com/dalmo1991/superflexPy>`_
repository, (2) adding the script to the local fork of the repository, and (3)
making a pull request to the original repository (see :ref:`contribute` for
further details). The contributed code will be checked, and assuming all checks
are passed,incorporated in the following release of SuperflexPy and, therefore,
other users will be able to import it.

The user will maintain authorship on the contributed code, which will be
released with the same :ref:`license` of SuperflexPy. It is good practice to add
to the contributions also some tests (see :ref:`tests`) to assess the
correctness.

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

Then we incorporate it into the SuperflexPy repository in the folder
:code:`superflexpy/implementation/models/` following the procedure illustrated
in the previous section (fork, change, and pull request).

Once the next release of SuperflexPy is available, the M4 model implementation
will be available in the updated installed package and can be imported by
general users for their own application, as shown below.

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

The recipients of the new file can then save the file in their computer and use
local importing. Assuming that the script that the recipients use to run the
model is in the same folder as the file initializing the model, the recipients
will use the model as follows

.. literalinclude:: share_models_code.py
   :language: python
   :lines: 39, 32, 32-37
   :linenos:

Note the local import in line 1.

As we believe in the `F.A.I.R. <https://www.go-fair.org/fair-principles/>`_
principles, we encourage modelers to share their models with the whole
community.

Dumping objects with Pickle
---------------------------

Python offers the module
`Pickle <https://docs.python.org/3/library/pickle.html>`_ to serialize objects
to binary files.  This approach enables the distribution of binary files, but
has the disadvantage of lacking transparency in the model structure.