=======
restcli
=======

**restcli** is a library and commandline utility for API testing. It reads
requests from a YAML file and supports scripting and variable interpolation.

Documentation
=============

Command-line usage is documented here `Usage <docs/usage.rst>`_, or by running
**restcli** with no arguments (after `Installation`_):

.. code-block:: sh

    $ restcli

To start using **restcli**, you should become acquainted with its main concepts,
described in the `Overview <docs/overview.rst>`_, then head over to the
`Tutorial <docs/tutorial.rst>`_ for more in-depth documentation, accompanied by
a complete example.


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

Assuming Docker is installed, **restcli** can run inside a container. To build
the Docker container, run the following from the project root:

.. code-block:: console

    $ docker build -t restcli .

Then you can run commands from within the container:

.. code-block:: console

    $ docker run -it restcli -c foobar.yaml run foo bar
    $ docker run -it restcli --save -c api.yaml -e env.yaml env foo:bar


License
=======

This software is distributed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_. See /LICENSE`_
for more information.
