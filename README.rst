=============
✨ restcli ✨
=============

**restcli** is a terminal web API client written in Python. It draws
inspiration from `Postman`_ and `HTTPie`_, and offers some of the best features
of both.


Features
========

* save requests as YAML files
* scripting
* parameterized requests using `Jinja2`_ templating
* expressive commandline syntax, inspired by `HTTPie`_
* first-class JSON support
* interactive prompt with autocomplete
* colored output


Usage
=====

Command-line usage is documented in the `Usage manual <docs/usage.rst>`_.


Documentation
=============

* `Overview <docs/overview.rst>`_
* `Usage <docs/usage.rst>`_
* `Making Requests <docs/requests.rst>`_
* `Tutorial <docs/tutorial.rst>`_


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


Roadmap
=======


Short-term
----------

Here's what we have in store for the foreseeable future.

* autocomplete Group and Request names in the command prompt
* support for other formats (plaintext, forms, file uploads)
* convert to/from Postman collections


Long-term
---------

Here are some longer-term feature concepts that may or may not get implemented.

* full screen terminal UI via `python_prompt_toolkit`_
* in-app request editor (perhaps using `pyvim`_)


License
=======

This software is distributed under the `Apache License, Version 2.0`_.

.. _Postman: https://www.getpostman.com/postman
.. _HTTPie: https://httpie.org/
.. _Jinja2: http://jinja.pocoo.org/
.. _python_prompt_toolkit: https://github.com/jonathanslenders/python-prompt-toolkit
.. _pyvim: https://github.com/jonathanslenders/pyvim
.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
