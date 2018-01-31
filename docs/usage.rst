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
      repl  Start an interactive prompt.
      run   Run a Request.
      view  View a Group, Request, or Request Parameter.

To display usage info for the different commands, supply the ``--help`` flag to
that particular command. Examples:

.. code-block:: console

    $ restcli run --help
    $ restcli view --help

Here's a breakdown of the available commands:

``run``
    Run a Request, writing the response to stdout.

``view``
    View the content of a Group, Request, or Request attribute.

``env``
    View or set Environment variables.

``repl``
    Start the `interactive prompt`_.


******************
Interactive Prompt
******************

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
