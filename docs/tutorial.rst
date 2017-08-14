.. _tutorial:

#########################
Tutorial: Modeling an API
#########################

.. note::
    If you haven't read through the `Overview <overview>`, go do that now!
    A basic familiarity with **restcli**'s core concepts is assumed.

Throughout this tutorial we will be modeling an API with **restcli**, gradually
adding to it as we learn new concepts, until we have a complete API client suite.
While the final result will be pasted at the end, I encourage you to follow
along and do it yourself as we go. This will give you many opportunities to
experiment and learn things you may not have learned otherwise!

.. _tutorial_debriefing:

**********
Debriefing
**********

You have been commissioned to build an API for the notorious secret society, the
Sons of Secrecy. You were told the following information, in hushed whispers:

#. New members can join by invite only.
#. Each member has a rank within the Society.
#. Your rank determines how many secrets you are told.
#. Only the highest ranking members, called Whisperers, have the ability to
   promote members through the ranks.

Your task is to create a membership service for the Whisperers to keep track of
and manage their underlings. Using the service, Whisperers must be able to:

#. Invite new members.
#. Promote or demote members' ranks.
#. Send "secrets" to members.

In addition, the service must be guarded by a secret key, and no requests
should go through if they do not contain the key.

Let's get started!

.. _tutorial_requests:

Requests
--------

We'll start by modelling the new member invitation service:

.. code-block:: yaml

    # secrecy.yaml
    ---
    memberships:
        invite:
            method: post
            url: "{{ server }}/memberships/invite"
            headers:
                Content-Type: application/json
                X-Secret-Key: '{{ secret_key }}'
            body: |
                name: {{ member_name }}
                age: {{ member_age }}
                can_keep_secrets: true


We made a new Collection and saved it as ``secrecy.yaml``. So far it has one
Group called ``memberships`` with one Request called ``invite``.

.. todo:: Move the following to the templating section:
As requested, we've also added an ``X-Secret-Key`` header which holds the secret
key. The key is implemented as a template variable so that each Whisperer can
have their own personal key.

.. _tutorial_request_parameters:

Request Parameters
~~~~~~~~~~~~~~~~~~

Let's zoom in a bit on Requests. While we're at it, we'll inspect our ``invite``
Request more closely as well.

``method`` (string, required)
    HTTP method to use. Case insensitive.

    We chose POST as our method for ``invite`` since POST is generally used for
    creating resources. Also, per `RFC 7231`_, the POST method should be used
    when the request is  non-`idempotent`_.

``url`` (string, required, templating)
    Fully qualified URL that will receive the request. Supports `templating`_.

    We chose to parameterize the ``scheme://host`` portion of the URL as
    ``{{ server }}``. As we'll see later, this makes it easy to change the host
    without a lot of labor, and makes it clear that the path portion of the URL,
    ``/memberships/invite``, is the real subject of this Request.

    We'll learn more about template variables later, but for now we know that
    invitations happen at ``/send_invite``.

``headers`` (object, ~templating)
    HTTP headers to add. Keys and values must all be strings. Values support
    `templating`_, but keys don't.

    We're using the standard ``Content-Type`` header as well as a custom,
    parameterized header called ``X-Secret-Key``. We'll inspect this further
    in the `templating`_ section.

``body`` (string, templating)
    The request body. It must be encoded as a string, to facilitate the full
    power of `Jinja2`_ `templating`_. You'll probably want to read the section
    on `block styles <appendix_block_styles>`_ at some point.

    The body string must contain valid YAML, which is converted to JSON before
    sending the request. Only JSON encoding is supported at this time.

    Our ``body`` parameter has 3 fields, ``name``, ``age``, and
    ``can_keep_secrets``. The first two are parameterized, but we just set the
    third to ``true`` since keeping secrets is pretty much required if you're
    gonna join the Sons of Secrecy.

``script`` (string)
    A Python script to be executed after the request finishes and a response is
    received. Scripts can be used to dynamically update the `Environment
    <tutorial_environment>`_ based on the response payload. We'll learn more
    about this later in `Scripting <tutorial_scripting>`_.

    Our ``invite`` Request doesn't have a script.


Templating
----------

**restcli** supports `Jinja2`_ templates in the ``url``, ``headers``, and
``body`` Request Parameters. This is used to parameterize Requests with the
help of `Environments <tutorial_environment>`_. Any template variables in these
parameters, denoted by double curly brackets, will be replaced with concrete
values from the given Environment before the request is executed.

During the `Debriefing`_, were told that the Whisperers can move members up the
ranks if they're deemed worthy. Well it just so happens that Wanda, a fledgling
member, has proven herself as a devout secret-keeper.

We'll start by adding another Request to our ``memberships`` Group:

.. code-block:: yaml

    # secrecy.yaml
    ---
    memberships:
        invite: ...

        edit_rank:
            method: patch
            url: '{{ server }}/memberships/{{ member_id }}'
            headers:
                Content-Type: application/json
                X-Secret-Key: '{{ secret_key }}'
            body: |
                title: '{{ titles[rank + 1] }}'
                rank: '{{ rank + 1 }}'


Whew, lots of variables! Let's whip up an Environment file for Wanda. This
strategy has the advantage that we can seamlessly move between different members
without making any changes to the Collection.

.. code-block:: yaml

    # wanda.env.yaml
    ---
    server: 'https://www.secrecy.org'
    secret_key: sup3rs3cr3t
    titles:
        - Loudmouth
        - Seeker
        - Keeper
        - Confidant
        - Spectre
    member_id: UGK882I59
    rank: 0
    #new_secrets:
    #    - secret basement room full of kittens
    #    - turtles all the way down

.. TODO: add `new_secrets` below, remove from above.

.. note::
    The ``env.yaml`` extension in ``wanda.env.yaml`` is just a convention to
    identify the file as an Environment. Any extension may be used.

Now we'll run the request:

.. code-block:: sh

    $ restcli -c secrecy.yaml -e wanda.yaml run memberships edit_rank

Here's what **restcli** does when we hit enter:

#. Load the Collection (``secrecy.yaml``) and locate the Request
   ``memberships.edit_rank``.
#. Load the Environment (``wanda.yaml``).
#. Use the Environment to execute the contents of the ``url``, ``headers``, and
   ``body`` parameters as `Jinja2 Template`_\s,.
#. Run the resulting HTTP request.

If we could view the finalized Request object before running it in #4, this is
what it would look like:

.. code-block:: yaml

    # secretmasons2.yaml

    method: post
    url: 'https://www.secrecy.org/memberships/12345/upgrade'
    headers:
        Content-Type: application/json
        X-Secret-Key: sup3rs3cr3t
    body: |
        rank: 1
        title: Seeker

Here's a piece-by-piece breakdown of what happened:

+ In the ``url`` section:
    + ``{{ server }}`` was replaced with the value of Environment.server,
      ``http://www.secrecy.org``.
    + `{{ member_id }}`` was replaced with the value of Environment.member_id,
      ``UGK882I59``.
+ In the ``headers`` section, ``{{ secret_key }}`` was replaced with the value
  of Environment.secret_key, ``sup3rs3cr3t``.
+ In the ``body`` section:
    + ``{{ rank }}`` was replaced with the value of Environment.rank,
      incremented by 1.
    + ``{{ title }}`` was replaced by an item of the Environment.titles
      list, by indexing it with the new rank value.

What we just learned should cover most use cases, but if you need more power or
just want to explore, there's much more to templating than what we just covered!
**restcli** supports the entire Jinja2 template language, so check out the official
`Template Designer Documentation`_ for the whole scoop.

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

    # secrecy.yaml
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

.. _RFC 7231: https://tools.ietf.org/html/rfc7231
.. _idempotent: https://en.wikipedia.org/wiki/Idempotence#Computer_science_meaning
.. _Jinja2: http://jinja.pocoo.org/
.. _Jinja2 Template: http://jinja.pocoo.org/docs/2.9/api/#jinja2.Template
.. _Template Designer Documentation: http://jinja.pocoo.org/docs/2.9/templates/
