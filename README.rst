=======
restcli
=======

An API client library and CLI written in Python.
It's Postman for terminal lovers!

.. contents::


Overview
========

**restcli** is a library and commandline utility for API testing. It reads
requests from a YAML file and supports scripting and variable interpolation.


Installation
============

With ``pip``:

.. code-block:: sh

    $ pip install -r requirements.txt
    $ pip install .

With ``setup.py``:

.. code-block:: sh

    $ python setup.py install

If you have ``invoke``, you can use it for running the tests and installation:

.. code-block:: sh

    $ invoke test  # Run the tests
    $ invoke install  # Install it
    $ invoke build  # Run the whole build workflow

If not, you can install it with ``pip``:

.. code-block:: sh

    $ pip install invoke


Docker
------

**restcli** can be run with Docker without additional dependencies.
Assuming Docker is installed, the Docker image can be built by running:

.. code-block:: sh

    $ docker build -t restcli .

Then run it with:

.. code-block:: sh

    $ docker run -it restcli [OPTIONS] ARGS


Configuring Your API
====================

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

See `Requests`_ for a more detailed explanation of the available
`Parameters <request_parameters>`_.


Meta
----

A Collection can also have a second YAML
`document <http://yaml.org/spec/1.2/spec.html#id2800132>`_ in the same file,
referred to as **Meta**. This document must appear *before* the Collection
document, and contains data which applies to the Collection as a whole.

.. code-block:: yaml

    ---
    defaults:
        headers:
            Content-Type: application/json
            Authorization: {{ username }}:{{ password }}
    lib:
        - restcli.contrib.scripts

    ---
    # Your Groups and Requests go down here...

.. _meta_parameters:

Meta Parameters
~~~~~~~~~~~~~~~

``defaults``
    Each item in ``defaults`` must be a valid `Request`_ attribute. These
    values will be used by any `Request`_ in the Collection which does not
    provide that attribute itself.

``lib``
    ``lib`` is an array of Python module paths. Each module here must contain a
    function with the signature ``define(request, env, *args, **kwargs)`` which
    returns a dict. That dict will be added to the execution environment of any
    script that gets executed after a `Request`_ is completed.

    For an example of a ``lib`` file, check out ``restcli.contrib.scripts``,
    which provides helpful utilities and shortcuts for you to use in your own
    Collections.

.. _request:
.. _requests:

Requests
--------

Let's dive deeper into Requests. Here is the one we looked at earlier:

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


Request Parameters
~~~~~~~~~~~~~~~~~~

``method`` (string, required)
    HTTP method to use in the request.

``url`` (string, required, templates)
    Fully qualified URL to send the request to. Supports `templating`_.

``headers`` (object, templates)
    HTTP headers. Keys and values must all be strings. Values support
    `templating`_, but keys don't.

``body`` (string, templates)
    The request body. Only JSON is supported at this time, and in order to
    support `templating`_, it must be encoded as a string. See
    `YAML block styles`_ for a brief explanation.

``script`` (string)
    A Python script to be executed after the request finishes and a response
    is received. You can modify the `Environment`_ here, or run tests. See
    `Scripting`_ for an overview of this feature. You may also want to read
    the section on `YAML block styles`_, since Python is whitespace-sensitive!


Templating
^^^^^^^^^^

**restcli** supports `Jinja2`_ templates in the ``url``, ``headers``, and
``body`` Request parameters as a way to parameterize Requests with
`Environment`_ files, explained below. Any template variables in these
parameters, denoted by double curly brackets, will be replaced with concrete
values from the `Environment`_ before the request is executed.

Let's pretend we're modelling an API for a super secretive, and possibly a
a little frightening, membership club. Members are invited in, and admins
can upgrade their memberships when they're deemed "worthy". And it just so
happens that Wanda, who's been very active in the club this year, has been
chosen for a membership upgrade.

We'll start with a Collection that looks like this:

.. code-block:: yaml

    # secret_club.yaml
    ---
    memberships:
        upgrade:
            method: post
            url: '{{ server }}/memberships/{{ member_id }}/upgrade'
            headers:
                Content-Type: application/json
                X-Secret-Key: '{{ secret_key }}'
            body: |
                vip_access: True
                rank: '{{ next_rank }}'
                privileges: '{{ priveleges }}'


Well how about that! We've got some template variables that need filling. Let's
create an `Environment`_ file to do just that:

.. code-block:: yaml

    # wanda.yaml
    ---
    server: 'https://secret-club.org'
    member_id: '12345'
    secret_key: 5up3r53cr37
    rank: Sultan of Secrets
    privileges:
        - penthouse access
        - cuddling kittens

Now we'll run the request:

.. code-block:: sh

    $ restcli -c secret_club.yaml -e wanda.yaml run memberships upgrade

When we hit enter, **restcli** loads ``secret_club.yaml`` and ``wanda.yaml``
into memory and calls ``jinja2.Template#render()`` on each parameter
that supports templating, using the ``wanda.yaml`` `Environment`_ as the
rendering context. This is what the Request looks like just before being sent
out:

.. code-block:: yaml

    # secret_club2.yaml
    ---
    memberships:
        upgrade:
            method: post
            url: 'https://secret-club.org/memberships/12345/upgrade'
            headers:
                Content-Type: application/json
                X-Secret-Key: 5up3r53cr37
            body: |
                vip_access: True
                rank: Sultan of Secrets
                privileges:
                    - penthouse access
                    - cuddling kittens

Have fun cuddling those kittens Wanda!

We just covered the common case, but there's much more to templating, including
conditionals and control structures. **restcli** supports the entire
`Jinja2 template language`_, so click the link to learn more.


Scripting
^^^^^^^^^

The ``script`` Request parameter is evaluated as a Python script which is
executed after the request is performed and a response is received. The Python
version is always the same as **restcli**'s. Run the following command to get
the current Python version along with other information (TODO):

.. code-block:: sh

    $ restcli info

Scripts are provided with an execution environment containing the following
variables:

``response``
    A `Response object`_ from the Python `requests library`_, which contains
    the status code, response headers, response body, and a lot more. Check
    out the `Response API <response_object>`_ for a detailed list.

``env``
    A Python ``dict`` which contains the entire hierarchy of the current
    Collection. It is mutable, and any changes made here will be persisted
    into the current Environment. If ``autosave`` is enabled, the changes
    will be saved to disk as well.


YAML Block Styles
^^^^^^^^^^^^^^^^^

Writing multiline strings for the ``body`` and ``script`` Request parameters
without using readability is easy with YAML's `block styles`_. I recommend
using `literal style`_ since it preserves whitespace and is the most readable.
Adding to the example above:

.. code-block:: yaml

    body: |
        name: bar
        age: {{ foo_age }}
        attributes:
            fire_spinning: 32
            basket_weaving: 11

The vertical bar (``|``) denotes the start of a literal block, so newlines are
 preserved, as well as any *additional* indentation. In this example, the
result is that the value of ``body`` is 5 lines of text, with the last two
lines indented 4 spaces.

Note that it is impossible to escape characters within a literal block, so if
that's something you need you may have to try a different


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

.. _Jinja2: <http://jinja2.pocoo.org/docs/2.9/>
.. _Jinja2 template language: <http://jinja.pocoo.org/docs/2.9/templates/>
.. _response object: <http://docs.python-requests.org/en/stable/api/#requests.Response>
.. _requests library: <http://docs.python-requests.org/en/stable/>
.. _block styles: <http://www.yaml.org/spec/1.2/spec.html#id2793604>
.. _literal style: <http://www.yaml.org/spec/1.2/spec.html#id2793604>
