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
*Requests*:

.. code-block:: yaml

    ---
    foo:
        new:
            method: post
            url: "{{ server }}/foo"
            headers:
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

Meta
~~~~

A Collection can also have a second YAML
`document <http://yaml.org/spec/1.2/spec.html#id2800132>`_ in the same file,
referred to as **Meta**. This document must appear *above* the Collection
document, and contains data which applies to the Collection as a whole.

.. code-block:: yaml

    ---
    defaults:
        headers:
            Content-Type: application/json
            Authorization: {{ username }}:{{ password }}
    lib:
        - restcli.contrib.scripts

Each item in ``defaults`` must be a valid `Request`_ attribute. These values
will be used by any `Request`_ in the Collection which does not provide that
attribute itself.

``lib`` is an array of Python module paths. Each module here must contain a
function with the signature ``define(request, env, *args, **kwargs)`` which
returns a dict. That dict will be added to the execution environment of
any script that gets executed (in the ``script`` field of a Request).

For an example of a ``lib`` file, check out ``restcli.contrib.scripts``, which
provides helpful utilities and shortcuts, and can be included in your own
Collections by adding ``restcli.contrib.scripts`` to the ``lib``.

Requests
~~~~~~~~

Here is the Request from the above example:

.. code-block:: yaml

    method: post
    url: "{{ server }}/foo"
    headers:
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

``body`` is a strings, but must contain valid YAML markup. This is in order to
support variable interpolation of arbitrary types, such as numbers or booleans.

``headers`` must be a flat object of key-value pairs. The values of ``headers``
can contain Jinja2 templates.

``script`` is a Python3 script that is executed after the request is performed,
and is provided the ``response`` (which is a `Response
<http://docs.python-requests.org/en/stable/api/#requests.Response>`_ instance
from the Python `requests library
<http://docs.python-requests.org/en/stable/>`_) as well as ``env``, which is
the current Environment and can be modified by the script.


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
      -c, --collection PATH       Collection file.  [required]
      -e, --env PATH              Environment file.
      -s, --save / -S, --no-save  Save Environment to disk after changes.
      --help                      Show this message and exit.

    Commands:
      repl
      run
      view

``restcli run``:

.. code-block:: text

    Usage: restcli run [OPTIONS] GROUP REQUEST [ENV]...

      Run a Request.

    Options:
      -o, --override TEXT  Add "key:val" pairs that shadow the Environment.
      --help               Show this message and exit.

``restcli view``:

.. code-block:: text

    Usage: restcli view [OPTIONS] GROUP [REQUEST] [ATTR]

      View a Group, Request, or Request Attribute.

    Options:
      --help  Show this message and exit.

``restcli repl``:

.. code-block:: text

    Usage: restcli repl [OPTIONS]

      Start an interactive command prompt.

    Options:
      --help  Show this message and exit.


Interactive Prompt
~~~~~~~~~~~~~~~~~~

NOTE: Some of this will be changing soon, so don't rely on stability here.

The interactive prompt is a read-eval-print loop which supports the same API
as the commandline interface, but with a few additional commands for
convenience:

- ``help``: Display general help or help for a specific command.
- ``run``: Run an Request.
- ``view``: Inspect a Group, Request, or Request Attribute.
- ``env``: View or change the currently loaded Environment.
- ``reload``: Reload the current Collection and/or Environment from disk.
- ``save``: Save the current Environment to disk.
- ``change_collection``: Change the current Collection file to something else.
- ``change_env``: Change the current Environment file to something else.

You may run ``help COMMAND`` on any command for more information about
arguments and usage of the given command.

Software License
----------------

This software is distributed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_. See `LICENSE <LICENSE>`_
for more information.
