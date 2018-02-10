#####
Usage
#####

**restcli** is invoked from the command-line. To display usage info, supply the 
``--help`` flag:

.. code-block:: console

    $ restcli --help

    Usage: restcli [OPTIONS] COMMAND [ARGS]...

    Options:
      -v, --version               Show the version and exit.
      -c, --collection PATH       Collection file.
      -e, --env PATH              Environment file.
      -s, --save / -S, --no-save  Save Environment to disk after changes.
      -q, --quiet / -Q, --loud    Suppress HTTP output.
      --help                      Show this message and exit.

    Commands:
      env   View or set Environment variables.
      exec  Run multiple Requests from a file.
      repl  Start an interactive prompt.
      run   Run a Request.
      view  View a Group, Request, or Request Parameter.

The available commands are:

`Command: run`_
    Run a Request.

`Command: exec`_
    Run multiple Requests from a file.

`Command: view`_
    Inspect the contents of a Group, Request, or Request attribute.

`Command: env`_
    View or set Environment variables.

`Command: repl`_
    Start the interactive prompt.

To display usage info for the different commands, supply the ``--help`` flag to
that particular command.


************
Command: run
************

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
        :linenos:

        $ restcli run actions get -n X-Foo:quux
        $ # OR
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

The following examples assume we're running Requests from the example
Collection.

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


*************
Command: exec
*************

.. code-block:: console

    $ restcli exec --help

    Usage: restcli exec [OPTIONS] FILE

      Run multiple Requests from a file.

      If '-' is given, stdin will be used. Lines beginning with '#' are ignored.
      Each line in the file should specify args for a single "run" invocation:

          [OPTIONS] GROUP REQUEST [MODIFIERS]...

    Options:
      --help  Show this message and exit.

The ``exec`` command loops through the given file, calling ``run`` with the
arguments provided on each line. For example, for the following file:

.. code-block:: text

    # requests.txt
    accounts create -o password:abc123
    accounts update password==abc123 -o name:foobar

These two invocations are equivalent:

.. code-block:: console

    $ restcli exec requests.txt

.. code-block:: console

    $ restcli run accounts create -o password:abc123
    $ restcli run update password==abc123 -o name:foobar


*************
Command: view
*************

.. code-block:: console

    $ restcli view --help

    Usage: restcli view [OPTIONS] GROUP [REQUEST] [PARAM]

      View a Group, Request, or Request Parameter.

    Options:
      --help  Show this message and exit.

The ``view`` command selects part of a Collection and outputs it as JSON.
It has three forms, described here with examples:

**Group view**
    Select an entire Group, e.g.:

    .. code-block:: console

        $ restcli view chordata

    .. code-block:: javascript

        {
          "mammalia": {
            "headers": {
              ...
            },
            "body": ...,
            ...
          },
          "amphibia": {
            ...
          },
          ...
        }

**Request view**
    Select a particular Request within a Group, e.g.:

    .. code-block:: console

        $ restcli view chordata mammalia

    .. code-block:: json

        {
          "url": "{{ server }}/chordata/mammalia"
          "method": "get",
          "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
          }
        }

**Request Attribute view**
    Select a single Attribute of a Request, e.g.:

    .. code-block:: console

        $ restcli view chordata mammalia url

    .. code-block:: json

        "{{ server }}/chordata/mammalia"

The output of ``view`` is just plain JSON, which makes it convenient for
scripts that need to programmatically analyze Collections in some way.

.. todo:: Provide a no-color/no-formatting flag for this and ``run``.


*************
Command: repl
*************

.. code-block:: console

    Usage: [OPTIONS] COMMAND [ARGS]...

    Options:
      -v, --version               Show the version and exit.
      -c, --collection PATH       Collection file.
      -e, --env PATH              Environment file.
      -s, --save / -S, --no-save  Save Environment to disk after changes.
      -q, --quiet / -Q, --loud    Suppress HTTP output.
      --help                      Show this message and exit.

    Commands:
      change_collection  Change to and load a new Collection file.
      change_env         Change to and load a new Environment file.
      env                View or set Environment variables.
      exec               Run multiple Requests from a file.
      reload             Reload Collection and Environment from disk.
      run                Run a Request.
      save               Save the current Environment to disk.
      view               View a Group, Request, or Request Parameter.

The ``repl`` command starts an interactive prompt which allows you to issue
commands in a read-eval-print loop. It supports the same set of commands as the
regular commandline interface and adds a few repl-specific commands as well.
