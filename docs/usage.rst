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
      -c, --collection PATH       Collection file.  [required]
      -e, --env PATH              Environment file.
      -s, --save / -S, --no-save  Save Environment to disk after changes.
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
Command: repl
*************

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
