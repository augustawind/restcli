restcli
=======

An API client library and CLI written in Python.
It's Postman for terminal lovers!

.. contents::

Overview
--------

**restcli** is a library and commandline utility for API testing. It reads
requests from a YAML file and supports scripting and variable interpolation.


Installation
------------

With ``pip``:

.. code-block:: sh

    $ pip install -r requirements.txt
    $ pip install .

With ``setup.py``:

.. code-block:: sh

    $ python setup.py install


Docker
~~~~~~

**restcli** can be run with Docker without additional dependencies.
Assuming Docker is installed, the Docker image can be built by running:

.. code-block:: sh

    $ docker build -t restcli .

Then run it with:

.. code-block:: sh

    $ docker run -it restcli


Configuring Your API
--------------------

**restcli** reads requests from YAML files called *Collections*. Collections
are objects composed of *Groups*, which are again objects composed of
*Requests*.

.. code-block:: yaml

    ---
    foo:
        new:
            method: post
            url: "{{ server }}/foo"
            headers: |
                Content-Type: application/json
                Accept: application/json
            body: |
                name: bar
                age: {{ foo_age }}
                is_cool: true
            script: |
                if response.status_code == 201:
                    env['foo_name'] = response.json()['name']

In this example, ``foo`` is a Group, and ``new`` is a Request in that Group.

Requests
~~~~~~~~

Here is the Request from the above example:

.. code-block:: yaml

    method: post
    url: "{{ server }}/foo"
    headers: |
        Content-Type: application/json
        Accept: application/json
    body: |
        name: bar
        age: {{ foo_age }}
        is_cool: true
    script: |
        if response.status_code == 201:
            env['foo_name'] = response.json()['name']

``headers``, ``body``, and ``scripts`` are optional. ``url``, ``headers``, and
``body`` all support Jinja2 templating, using an `Environment`_ as the context.

``headers`` and ``body`` are both strings, but must contain valid YAML markup.
This is in order to support variable interpolation of arbitrary types, such as
numbers or booleans. ``headers`` must contain a flat object of key-value pairs.
Only YAML bodies are supported at this time.

``script`` is a Python3 script that is executed after the request is performed,
and is provided the ``response`` (which is a `Response
<http://docs.python-requests.org/en/stable/api/#requests.Response>`_ instance
from the Python `requests <http://docs.python-requests.org/en/stable/>`_
library) as well as ``env``, which is the current Environment and can be
modified by the script.


Environment
~~~~~~~~~~~

The Environment is another YAML file which must contain an object where each
key-value pair represents a variable. These variables are available anywhere in
a Request where Jinja2 templates are supported, as well as in the ``scripts``
portion of a Request where they can be read from and modified.

Here is an example Environment for the above example Request:

.. code-block:: yaml

    server: http://quux.org
    foo_age: 15

After the Request is run (after its script is executed), the Environment could
then look like this:

.. code-block:: yaml

    server: http://quux.org
    foo_age: 15
    foo_name: bar


Usage
-----

.. code-block:: text

    Usage: restcli [OPTIONS] COMMAND [ARGS]...

    Options:
      -c, --collection PATH       [required]
      -e, --env PATH
      -s, --save / -S, --no-save
      --help                      Show this message and exit.

    Commands:
      repl
      run
      view

``restcli run``:

.. code-block:: text

    Usage: restcli run [OPTIONS] GROUP REQUEST [ENV]...

    Options:
      --help  Show this message and exit.

``restcli view``:

.. code-block:: text

    Usage: restcli view [OPTIONS] GROUP [REQUEST] [ATTR]

    Options:
      --help  Show this message and exit.

``restcli repl``:

.. code-block:: text

    Usage: restcli repl [OPTIONS]

    Options:
      --help  Show this message and exit.


Interactive Prompt
~~~~~~~~~~~~~~~~~~

The interactive prompt is a read-eval-print loop which supports the same API
as the commandline interface, but with a few additional commands for
convenience:

- ``help``: Display general help or help for a specific command.
- ``run``: Run an Request.
- ``view``: Inspect a Group, Request, or Request Attribute.
- ``env``: Print the currently loaded Environment.
- ``reload``: Reload the current Collection and/or Environment from disk.
- ``save``: Save the current Environment to disk.
- ``change_collection``: Change the current Collection file to something else.
- ``change_env``: Change the current Environment file to something else.

You may run ``help COMMAND`` on any command for more information about
arguments and usage of the given command.


License
-------

This software is distributed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_. See `LICENSE <LICENSE>`_
for more information.
