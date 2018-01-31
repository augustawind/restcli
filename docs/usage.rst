.. _usage:

#####
Usage
#####

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
