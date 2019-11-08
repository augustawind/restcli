***************
Making Requests
***************

.. code-block:: console

    $ restcli run --help

    Usage: restcli run [OPTIONS] GROUP REQUEST [MODIFIERS]...

      Run a Request.

    Options:
      -o, --override-env TEXT  Override Environment variables.
      --help                   Show this message and exit.


The ``run`` command runs Requests from a Collection, optionally within an
Environment. It roughly executes the following steps:

#. Find the given Request in the given Collection.
#. If ``defaults`` are given in a Config Document, use it to fill in missing
   parameters in the Request.
#. If an Environment is given, apply any overrides to it.
#. Render the Request with Jinja2, using the Environment if given.
#. Apply any modifiers to the Request.
#. Execute the Request.
#. If the Request has a ``script``, execute it.
#. If ``save`` is true, write any Environment changes to disk.


Examples:

.. code-block:: console

    $ restcli -s -c food.yaml -e env.yaml run recipes add -o !foo

    $ restcli -c api.yaml run users list-all Authorization:abc123


Environment overrides
~~~~~~~~~~~~~~~~~~~~~

When running a Request, the Environment can be overrided on-the-fly with the
``-o`` option. It supports two types of arguments:

``KEY:VALUE``
    Set the key ``KEY`` to the value ``VALUE``.

``!KEY``
    Delete the key ``KEY``.

The ``-o`` option must be specified once for each argument. For example, the
following ``run`` invocation will temporarily set the key ``name`` to the value
``donut`` and delete the key ``foo``:

.. code-block:: console

    $ restcli -c food.yaml -e env.yaml run recipes add \
              -o name:donut \
              -o !foo


Request modifiers
~~~~~~~~~~~~~~~~~

In addition to Environment overrides, the Request itself can be modified
on-the-fly using a special modifier syntax. In cases where an Environment
override changes the same Request parameter, modifiers always take precedence.
They must appear later than other options.

Each modifier has a `mode <Modifier modes>`_ and a `parameter
<Modifier operations>`_. The *operation* describes the thing to be modified,
and the *mode* describes the way in which it's modified.

Generally, each modifier is written as a commandline flag, specifying the
*mode*, followed by an argument, specifying the *operation*. In the following
example modifier, its *mode* specified as ``-n`` (**assign**) and its
*operation* specified as ``foo:bar``::
    
    -n foo:bar

Modifiers may omit the *mode* flag as well, in which case *mode* will default
to **assign**. Thus, the following modifiers are equivalent::

    -a foo:bar -n baz=quux
    -a foo:bar baz=quux

Syntax
......

The general syntax of modifiers is described here:

.. productionlist::
   modifiers: (`mod_append` | `mod_assign` | `mod_delete`)*
   mod_assign: "-n" `operation` | `operation`
   mod_append: "-a" `operation`
   mod_delete: "-d" `operation`
   operation: "'" `op` "'" | '"' `op` '"'
   operation: `op_header` | `op_query` | `op_body_str` | `op_body_nostr`
   op_header: <ASCII text> ":" [<ASCII text>]
   op_query: <Unicode text> "==" [<Unicode text>]
   op_body_str: <Unicode text> "=" [<Unicode text>]
   op_body_nostr: <Unicode text> ":=" [<Unicode text>]


Modifier modes
..............

There are three modifier modes:

**assign**
    Assign the specified value to the specified Request parameter, replacing it
    if it already exists. This is the default. If no *mode* is specified for a
    given *modifier*, its *mode* will default to **assign**.

    If a header ``X-Foo`` were set to ``bar``, the following would change it
    to ``quux``:

    .. code-block:: console

        $ restcli run actions get -n X-Foo:quux

    Since **assign** is the default mode, you can omit the ``-n``:

    .. code-block:: console

        $ restcli run actions get X-Foo:quux

**append**
    Append the specified value to the specified Request parameter. This
    behavior differs depending the type of the Request parameter.

    If its a *string*, concenate the incoming value to it as a string.
        If a string field ``nickname`` were set to ``"foobar"``, the
        following would change it to ``"foobar:quux"``.

        .. code-block:: console
            :linenos:

            $ restcli run actions post -a nickname=':quux'

    If its a *number*, add the incoming value to it as a number.
        If a json field ``age`` were set to ``27``, the following would
        change it to ``33``.

        .. code-block:: console
            :linenos:

            $ restcli run actions post -a age:=6

    If its an *array*, concatenate the incoming value to it as an array.
        If a json field ``colors`` were set to ``["red", "yellow"]``, the
        following would change it to ``["red", "yellow", "blue"]``.

        .. code-block:: console
            :linenos:

            $ restcli run actions post -a colors:='["blue"]'

    Other types are not currently supported.

    .. todo:: Add validation for other types.

**delete**
    Delete the specified Request parameter. This ignores the value completely.

    If a url parameter ``pageNumber`` were set to anything, the following would
    remove it from the url query completely.

    .. code-block:: console
        :linenos:

        $ restcli run actions get -d pageNumber==

.. todo:: Rename ``append`` mode to ``add`` and maybe ``assign`` to ``set`` or
          ``replace``.

.. table:: Table of modifier modes

    =========  =========  ================
    Mode       Flag       Usage
    =========  =========  ================
    assign     ``-n``     ``-n OPERATION``
    append     ``-a``     ``-a OPERATION``
    delete     ``-d``     ``-d OPERATION``
    =========  =========  ================


Modifier operations
...................

Operations

**header**
    Operators on a header key-value pair. The *key* and *value* must be valid
    ASCII. Delimited by ``:``.
**url param**
    A URL query parameter. Delimited by ``==``.
**string field**
    A JSON object key-value pair. The *value* will be interpreted as a string.
    Delimited by ``=``.
**json field**
    A JSON object key-value pair. The *value* will be interpreted as a string.
    Delimited by ``:=``.


.. table:: Table of modifier operations

    ============  =========  ====================  =======================
    Operation     Delimiter  Usage                 Examples
    ============  =========  ====================  =======================
    header        ``:``      - ``KEY : VALUE``     - ``Authorization:abc``
                             - ``KEY :``           - ``Authorization:``
    url param     ``==``     - ``KEY == VALUE``    - ``locale==en_US``
                             - ``KEY ==``          - ``locale==``
    string field  ``=``      - ``KEY = VALUE``     - ``username=foobar``
                             - ``KEY =``           - ``username=``
    json field    ``:=``     - ``KEY := VALUE``    - ``age:=15``
                             - ``KEY :=``          - ``age:=``
    ============  =========  ====================  =======================

Examples
........

To follow along with the examples, grab the `simple example project`_ from the
**restcli** source. Then from the example directory, export some environment
variables to use the example project's Collection and Environment files:

.. code-block:: console

    $ export RESTCLI_COLLECTION="simple.collection.yaml"
    $ export RESTCLI_ENV="simple.env.yaml"

To check your work after each **restcli run** invocation, just inspect the
response. All the Requests in this Collection will respond with a JSON blob
containing the information about your HTTP request, like this:

.. code-block:: console

    $ restcli run actions get

.. code-block:: javascript

    // HTTP response

    {
        "args": {
            "fooParam": "10"
        },
        "headers": {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
            "Host": "httpbin.org",
            "User-Agent": "HTTPie/0.9.9",
            "X-Foo": "foo+bar+baz"
        },
        "origin": "75.76.62.109",
        "url": "https://httpbin.org/get?fooParam=10"
    }

**Example 1**

Delete the header ``"Accept"``.

.. code-block:: bash

   $ run actions get -d Accept:

**Example 2**

Append the string ``"420"`` to the body value ``"nickname"``.

.. code-block:: bash

   $ run actions post -a time=420

**Example 3**

Assign the array ``'["red", "yellow", "blue"]'`` to the body value
``"colors"``.

.. code-block:: bash

   $ run actions post -n colors:='["red", "yellow", "blue"]'


.. _simple example project: https://github.com/dustinrohde/restcli/tree/master/examples/simple
