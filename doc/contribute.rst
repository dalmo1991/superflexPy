.. note:: Last update 18/11/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _contribute:

Software organization and contribution
======================================

.. image:: pics/contribute/schematic_with_logo.png
   :align: center

The SuperflexPy framework comprises the following components:

- **Source code**: Latest version of all the code necessary to use the
  framework. It should be accessed only by an advanced user who wants to
  understand the internal functioning, install manually the latest version, or
  extend the framework.
- **Packaged release**: Latest stable version of the framework available for
  users to install and use.
- **Documentation**: Detailed explanation of the framework.
- **Examples**: Introduction to SuperflexPy for a new user, providing working
  models and showcasing potential applications.
- **Scientific references**: Peer-reviewed publication that presents the
  framework in a scientific context, including a broad comparison with other
  existing solutions.

The source code, documentation, and examples are part of the official repository
of SuperflexPy that is hosted on
`GitHub <https://github.com/dalmo1991/superflexPy>`_. A user who wants to read
the source code or modify any aspect of SuperflexPy (source code, documentation,
and examples) can do it using GitHub.

New releases of the software are available from the official Python Package
Index (PyPI) where SuperflexPy has a
`dedicated page <https://pypi.org/project/superflexpy/>`_.

Documentation builds automatically from the
`source folder <https://github.com/dalmo1991/superflexPy/tree/master/doc>`_ on
GitHub and is published online in
`Read the Docs <https://superflexpy.readthedocs.io/>`_.

Examples are made available on GitHub as Jupyter notebooks. These examples can
be visualized statically or run in a sandbox environment (see :ref:`examples`
for further details).

The scientific publication introducing SuperflexPy is currently in preparation
and it will be linked here once available.

Contributions
-------------

Contributions to the framework can be made in the following ways:

- Submit issues on bugs, desired features, etc.
- Solve open issues.
- Extend the documentation with new demos and use cases.
- Extend or modify the framework.
- Use and advertize the framework in your publication.

`This page <https://www.dataschool.io/how-to-contribute-on-github/>`_
illustrates the typical workflow that should be followed when contributing to a
GitHub project. In summary, it consists of the following steps:

1. Fork the SuperflexPy repository to the user GitHub account;
2. Clone the fork in the user computer;
3. Modify the code, commit the changes, and push them to the GitHub fork of
   SuperflexPy;
4. Make a pull request on GitHub to the SuperflexPy repository.

Branching scheme of the GitHub repository
.........................................

Updates to SuperflexPy are made directly in the branch :code:`master`, which
represents the most up-to-date branch. The branch :code:`release` is used only
for staging of new software releases and, therefore, code should not be pushed
directly to it.

When an update of the code is merged from :code:`master` to the branch
:code:`release`, a new version of the package is automatically released on PyPI.
Remember to update the version number in the :code:`setup.py` file to avoid
conflicts in the process.

Developers are free to create new branches but pull requests must be directed to
:code:`master` and not to :code:`release`.

Documentation and examples are generated from the content of the :code:`master`
branch.
