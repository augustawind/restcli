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

The ``run`` command is documented on its own page, in :doc:`Making Requests
<requests>`.


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


************
Command: env
************

.. todo:: Write this section


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
