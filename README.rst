=======
restcli
=======

An API client library and CLI written in Python.
It's Postman for terminal lovers!

.. contents::


Usage
=====

.. code-block:: console

    Usage: restcli [OPTIONS] COMMAND [ARGS]...

    Options:
      -v, --version               Show the version and exit.
      -c, --collection PATH       Collection file.  [required]
      -e, --env PATH              Environment file.
      -s, --save / -S, --no-save  Save Environment to disk after changes.
      --help                      Show this message and exit.

    Commands:
      env   View or set Environment variables.
      repl  Start an interactive prompt.
      run   Run a Request.
      view  View a Group, Request, or Request Parameter.


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


Overview
========

We'll start with a bird's eye view of some core concepts in **restcli**, and
then move into the tutorial.


Collections
-----------

**restcli** understands your API through YAML files called *Collections*.
Collections are objects composed of *Groups*, which are again objects composed
of `Requests`_. A Collection is essentially just a bunch of Requests --
Groups are purely organizational.

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

.. _environment:

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

If you don't fully understand it yet, that's quite alright! We'll get lots
of practice in the tutorial. Let's begin.


Tutorial: An API in Secrecy
===========================

Now that we have a basic understanding of **restcli**, let's get our hands
dirty and put these concepts to use!

As we move forward we're going to model an API for a super secretive,
vaguely intimidating, private membership club called "The Secretmasons". New
members must be invited to get in, and admins can upgrade their membership
status when they're deemed "worthy". The higher your rank in the club, the
more secrets you are told. By the end we'll have a flexible and powerful
toolbox that will make club management so easy, a gopher tortoise could do it.
Let's get started!


.. _request:
.. _requests:

Requests
--------

Requests are the building blocks of **restcli**, so let's dive right in! We'll
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
    want to read the section on `block styles`_ at some point.

    Our ``body`` parameter has 3 fields, ``name``, ``age``, and ``can_keep_secrets``.
    The first two are parameterized, but we just set the third to ``true``
    since The Secretmasons won't let anyone in who can't keep secrets anyway.

``script`` (string)
    A Python script to be executed after the request finishes and a response
    is received. Scripts can be used to dynamically update the `Environment`_
    based on the response content. We'll learn more about this later in
    `Scripting`_.

    Our ``invite`` Request doesn't have a script yet.


Templating
----------

**restcli** supports `Jinja2`_ templates in the ``url``, ``headers``, and
``body`` parameters to parameterize Requests with the help of `Environment`_
files. Any template variables in these parameters, denoted by double curly
brackets, will be replaced with concrete values from the `Environment`_ before
the request is executed.

Remember how we said that admins in The Secretmasons can promote members (if
they're "worthy")? Well it just so happens that Wanda, who's been very active
in the club this year, has been chosen for this prestigious honor, so let's
get to work!

We'll start by adding another Request to our ``memberships`` Group:

.. code-block:: yaml

    # secretmasons.yaml
    ---
    memberships:
        invite: ...

        upgrade:
            method: post
            url: '{{ server }}/memberships/{{ member_id }}/upgrade'
            headers:
                Content-Type: application/json
                X-Secret-Key: '{{ secret_key }}'
            body: |
                vip_access: true
                rank: '{{ next_rank }}'
                secrets_granted: '{{ new_secrets }}'


Whew, lots of variables! Let's get this under control and whip up a good old
fashioned `Environment`_ file:

.. code-block:: yaml

    # wanda.yaml
    ---
    server: 'https://secretmasons.org'
    member_id: '12345'
    secret_key: 5up3r53cr37
    rank: Sultan of Secrets
    new_secrets:
        - secret basement room full of kittens
        - turtles all the way down

Now we'll run the request:

.. code-block:: sh

    $ restcli -c secretmasons.yaml -e wanda.yaml run memberships upgrade

Here's what **restcli** does when we hit enter:

+ Load the Collection (``secretmasons.yaml``) and find the desired Request.
+ Load the Environment (``wanda.yaml``).
+ Create a `Jinja2 Template`_ from each of the ``url``, ``headers``, and
  ``body`` parameters, respectively.
+ `Render each template`_, using the Environment as the `template context`_.
+ TODO: reqmod

Before we send the request, though, let's see what it would look like at this
stage:

.. code-block:: yaml

    # secretmasons2.yaml
    ---
    memberships:
        upgrade:
            method: post
            url: 'https://secretmasons.org/memberships/12345/upgrade'
            headers:
                Content-Type: application/json
                X-Secret-Key: 5up3r53cr37
            body: |
                vip_access: true
                rank: Sultan of Secrets
                secrets_granted:
                    - secret basement room full of kittens
                    - turtles all the way down

Have fun cuddling all those kittens, Wanda!

What we just learned should cover the most common use cases, but if you need more
power or just want to play around, there's much more to templating than what
was covered here! **restcli** supports the entire Jinja2 template language, so
check out `Jinja2 Template Designer Documentation`_ for the whole scoop.


Scripting
---------

As previously mentioned, each Request has an optional ``script`` parameter
which takes a Python script. These scripts are evaluated *after* a Request is
performed, once the response is received.

.. note::
    Your scripts will run on the same Python interpreter **restcli** is running
    on. To get version info, use the ``--version`` flag:

    .. code-block:: sh

        $ restcli --version

Under the hood, scripts are executed with the Python builtin ``exec()``, which
is called with a code object containing the script as well as a ``globals``
dict containing the following variables:

``response``
    A `Response object`_ from the Python `requests library`_, which contains
    the status code, response headers, response body, and a lot more. Check
    out the `Response API <response_object>`_ for a detailed list.

``env``
    A Python dict which contains the entire hierarchy of the current
    Collection. It is mutable, and editing its contents may result in one or
    both of the following effects:

    A. If running in interactive mode, any changes made will persist in the
       active Environment until the session ends.
    B. If ``autosave`` is enabled, the changes will be saved to disk.

lib definitions
    Any functions or variables imported in ``lib`` in the `Config document`_
    will be available in your scripts as well. We'll tackle the
    `Config document`_ in the next section.

.. note::
    Since Python is whitespace sensitive, you'll probably want to read the
    section on `block styles`_, too.


.. _Config document:

The Config Document
-------------------

So far our Collections have been composed of a single YAML document.
**restcli** supports an optional second document per Collection as well, called
the Config Document.

.. note::
    If you're not sure what "document" means in YAML, here's a quick primer:

    Essentially, documents allow you to have more than one YAML "file"
    (document) in the same file. Notice that ``---`` that appears at the top
    of each example we've looked at? That's how you tell YAML where your
    document begins.

    Technically, the spec has more rules than that for documents but PyYAML,
    the library **restcli** uses, isn't that strict. Here's the spec
    anyway if you're interested: http://yaml.org/spec/1.2/spec.html#id2800132

If present, the Config Document must appear *before* the Requests document.
Breaking it down, a Collection must either:

- contain exactly one document, the Requests document, or
- contain exactly two documents; the Config Document and the Requests document,
  in that order.

Let's add a Config Document to our Secretmasons Collection. We'll take a look
and then jump into explanations after:

.. code-block:: yaml

    # secretmasons.yaml
    ---
    defaults:
        headers:
            Content-Type: application/json
            X-Secret-Key: '{{ secret_key }}'
    lib:
        - restcli.contrib.scripts

    ---
    memberships:
        invite: ...

        upgrade: ...


Config Parameters
~~~~~~~~~~~~~~~~~

The Config Document is used for global configuration in general, so the
parameters defined here don't have much in common.

``defaults`` (object)
    Default values to use for each Request parameter when not specified in the
    Request. ``defaults`` has the same structure as a `Request`_, so each
    parameters defined here must also be valid as a Request parameter.


``lib`` (array)
    ``lib`` is an array of Python module paths. Each module here must contain a
    function with the signature ``define(request, env, *args, **kwargs)`` which
    returns a dict. That dict will be added to the execution environment of any
    script that gets executed after a `Request`_ is completed.

    **restcli** ships with a pre-baked ``lib`` module at
    ``restcli.contrib.scripts``. It provides some useful utility functions
    to use in your scripts. It can also be used as a learning tool.


Appendix
========

A. YAML Block Styles
--------------------

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


B. Interactive Prompt
---------------------

The interactive prompt is a read-eval-print loop which supports the same API
as the commandline interface, but with a few additional commands for
convenience. Here's the full usage text for the REPL:

.. code-block:: console

    Usage: [OPTIONS] COMMAND [ARGS]...

    Options:
      -v, --version               Show the version and exit.
      -c, --collection PATH       Collection file.  [required]
      -e, --env PATH              Environment file.
      -s, --save / -S, --no-save  Save Environment to disk after changes.
      --help                      Show this message and exit.

    Commands:
      change_collection  Change to and load a new Collection file.
      change_env         Change to and load a new Environment file.
      env                View or set Environment variables.
      reload             Reload Collection or Environment from disk.
      run                Run a Request.
      save               Save the current Environment to disk.
      view               View a Group, Request, or Request Parameter.


C. License
----------

This software is distributed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_. See `LICENSE <LICENSE>`_
for more information.

.. _idempotent: <https://en.wikipedia.org/wiki/Idempotence>
.. _Jinja2: <http://jinja2.pocoo.org/docs/2.9/>
.. _Jinja2 Template Designer Documentation: <http://jinja.pocoo.org/docs/2.9/templates/>
.. _Jinja2 Template: <http://jinja.pocoo.org/docs/2.9/api/#jinja2.Template>
.. _template context: <http://jinja.pocoo.org/docs/2.9/api/#the-context>
.. _Render each template: <http://jinja.pocoo.org/docs/2.9/api/#jinja2.Template.render>
.. _response object: <http://docs.python-requests.org/en/stable/api/#requests.Response>
.. _requests library: <http://docs.python-requests.org/en/stable/>
.. _block styles: <http://www.yaml.org/spec/1.2/spec.html#id2793604>
.. _literal style: <http://www.yaml.org/spec/1.2/spec.html#id2793604>
