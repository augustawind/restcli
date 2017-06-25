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


Overview: The Two Pillars of restcli
====================================

We'll start with a bird's eye view of some core concepts in **restcli**, and
then move into the tutorial.


Collections
-----------

**restcli** understands your API through YAML files called *Collections*.
*Collections are objects composed of *Groups*, which are again objects composed
*of `*Requests*`_. A Collection is essentially just a bunch of Requests --
*Groups are purely organizational.

.. code-block:: yaml

    ---
    foo:
        bar:
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

This Collection has one Group called ``foo``, and the Group ``foo`` has one
Request called ``bar``. We'll explore `Requests`_ and their
`Parameters <request_parameters>`_ in greater depth later, but take note of
the stuff in between the double curly brackets: ``{{ server }}``,
``age: {{ foo_age }}``. These are `template variables <templating>`_, which
is how you parameterize your Requests in **restcli**. In order for this
Request to execute successfully, these template variables must be given
concrete values, which brings us to...


Environments
------------

*Environments* are also YAML files, but they are about as simple as it gets.
An Environment is an object which defines values to be used with the
`template variables <templating>`_ we just learned about. Environments can also
be modified programmatically, which we'll learn about later in `Scripting`_.

Here's an example Environment that compliments the Collection we just looked
at:

.. code-block:: yaml

    server: http://quux.org
    foo_age: 15


Tutorial: Secret Club API
=========================

Now that we have some core concepts under our belts, I think we're ready to
put our knowledge to use!

As a learning exercise, we're going to model an API for a super secretive,
vaguely intimidating, private membership club called "The Secretmasons". New
members must be invited to get in, and admins can upgrade their membership
status when they're deemed "worthy". The higher your rank in the club, the
more secrets you are told. Let's get started!

.. _request:
.. _requests:

Requests
--------

Requests are the building blocks of **restcli**, so let's dive deep! We'll
start by modelling The Secretmasons' Invitation API. How else did you think
people got invited?

.. code-block:: yaml

    # secretmasons.yaml
    ---
    memberships:
        invite:
            method: post
            url: "{{ server }}/send_invite"
            headers:
                Content-Type: application/json
                X-Secret-Key: '{{ secret_key }}'
            body: |
                name: {{ member_name }}
                age: {{ member_age }}
                can_keep_secrets: true


We made a new Collection and saved it as ``secretmasons.yaml``. So far it has
one Group called ``memberships`` which contains one Request called ``invite``.
Now we'll figure out what this ``invite`` Request is really about.


Request Parameters
~~~~~~~~~~~~~~~~~~

Requests are objects with parameters which tell **restcli** how to talk to
your API.

``method`` (string, required)
    HTTP method to use in the request. Case insensitive.

    We chose ``POST`` for this time since we are creating a resource and it's
    not `idempotent`_.

``url`` (string, required, templates)
    Fully qualified URL to send the request to. Supports `templating`_.

    We'll worry about parameters later, but for now we know that invitations
    happen at ``/send_invite``.

``headers`` (object, templates)
    HTTP headers. Keys and values must all be strings. Values support
    `templating`_, but keys don't.

    We're using the standard ``Content-Type`` header as well as a custom,
    parameterized header called ``X-Secret-Key``.


``body`` (string, templates)
    The request body. Only JSON is supported at this time, and in order to
    support `templating`_, it must be encoded as a string. You'll probably
    want to read the section on `YAML block styles`_ at some point.

    Our ``body`` parameter has 3 fields, ``name``, ``age``, and ``can_keep_secrets``.
    The first two are parameterized, but we just set the third to ``true``
    since The Secretmasons won't let anyone in who can't keep secrets anyway.


``script`` (string)
    A Python script to be executed after the request finishes and a response
    is received. You can modify the `Environment`_ here, or run tests. We'll
    learn more about this later in `Scripting`_.




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

In addition, any functions or variables defined in the ``lib`` section
of the `Config`_ document will be available in your scripts as well. This
feature is covered in greater detail when we look at `Config`_.

Since Python is whitespace sensitive, you'll probably want to read the section
on `YAML block styles`_, too.


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


Config
----

A Collection can also have a second YAML
`document <http://yaml.org/spec/1.2/spec.html#id2800132>`_ in the same file,
referred to as **Config**. This document must appear *before* the Collection
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


Config Parameters
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

.. _idempotent: <https://en.wikipedia.org/wiki/Idempotence>
.. _Jinja2: <http://jinja2.pocoo.org/docs/2.9/>
.. _Jinja2 template language: <http://jinja.pocoo.org/docs/2.9/templates/>
.. _response object: <http://docs.python-requests.org/en/stable/api/#requests.Response>
.. _requests library: <http://docs.python-requests.org/en/stable/>
.. _block styles: <http://www.yaml.org/spec/1.2/spec.html#id2793604>
.. _literal style: <http://www.yaml.org/spec/1.2/spec.html#id2793604>
