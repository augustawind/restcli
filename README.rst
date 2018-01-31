=======
restcli
=======

**restcli** is a library and commandline utility for API testing. It reads
requests from a YAML file and supports scripting and variable interpolation.

.. contents::

See `Usage <docs/usage.rst>`_ for usage information.

See the `Overview <docs/overview.rst>`_ for a bird's eye view of main concepts.

See the `Tutorial <docs/tutorial.rst>`_ for an in-depth tutorial.


Installation
============

With ``pip``:

.. code-block:: sh

    $ pip install -r requirements.txt
    $ pip install .

With ``setup.py``:

.. code-block:: sh

    $ python setup.py install

With ``setup.py`` but allow edits to the files under ``restcli/`` and reflect
those changes without having to reinstall ``restcli``:

.. code-block:: sh

    $ python setup.py develop

If you have ``invoke``, you can use it for running the tests and installation.
If not, you can install it with ``pip install invoke``.

.. code-block:: sh

    $ invoke test     # Run the tests
    $ invoke install  # Install it
    $ invoke build    # Run the whole build workflow


Docker
------

Assuming Docker is installed, **restcli** can run inside a container.

.. code-block:: console

    $ docker build -t restcli .

Then run it with:

.. code-block:: console

    $ docker run -it restcli [OPTIONS] ARGS


License
=======

This software is distributed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_. See `LICENSE <LICENSE>`_
for more information.
