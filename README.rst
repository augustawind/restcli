restcli
=======

An API client library and CLI written in Python.
It's Postman for terminal lovers!

-  `Overview`_
-  `Installation`_
    - `Docker`_
-  `File Format`_
-  `Usage`_
    - `Command Line Interface`_
    - `Interactive Prompt`_
-  `License`_


Overview
--------

restcli is a library and commandline utility for API testing. It reads requests
from a YAML file and supports scripting and variable interpolation.


Installation
------------

Using `pip`:

.. code-block:: sh

    $ pip install -r requirements.txt
    $ pip install .

Using `setup.py`:

.. code-block:: sh

    $ python setup.py install


Docker
~~~~~~

**restcli** can be run with Docker without additional dependencies.
Assuming Docker is installed, the Docker image can be built by running:

.. code-block:: sh

    $ docker build -t restcli .


Then run it with:

.. code-block:: sh

    $ docker run -it restcli


File Format
-----------

Requests are organized into Groups, which are like folders of Requests. The
file should contain an object mapping Group names to Groups. Each Group object
should contain an object mapping Request names to Requests.


Request Objects
~~~~~~~~~~~~~~~

Each Request object should have the following format (example):

.. code-block:: yaml

    method: post
    url: "{{ server_url }}/foobar"
    headers: |
        Content-Type: application/json
        Accept: application/json
    body: |
        name: foo
        age: {{ foo_age }}
        is_cool: true
    scripts:
        post_request:
            if response.status_code == 201:
                env['foobar_name'] = response.json()['name']


`headers`, `body`, and `scripts` are optional. `url`, `headers`, and `body` all
support Jinja2 templating, using the Environment as the context.

`headers` and `body` are both strings, but must contain valid YAML markup. This
is in order to support templating. `headers` must be a 1-dimensional object of
key-value string pairs. `body` can be any valid request body format. Only JSON
bodies are supported at this time.

`scripts` is an object mapping names to Python3 scripts that are executed in
specific contexts based on the name. Only the `post_request` script is
supported at this time. This is ran after the request was made, and is provided
the `request` object (from the Python `requests` library) as well as the `env`
Environment, which can be modified in the script.


Environment
~~~~~~~~~~~

The Environment is another YAML file which must be a flat, 1-dimensional object
of key-value pairs. The values can be any valid JSON type. These variables are
available anywhere in a Request where Jinja2 templates are supported, as well
as in the `scripts` portion of a Request where they can be read from and
modified.

Here is an example Environment for the above example Request:

.. code-block:: yaml

    server_url: http://quux.org
    foo_age: 15


Usage
-----


Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    Usage: restcli [OPTIONS] COMMAND [ARGS]...

    Options:
      -c, --collection PATH       [required]
      -e, --env PATH
      -s, --save / -S, --no-save
      --help                      Show this message and exit.

    Commands:
      repl
      run
      view

`restcli run`:

.. code-block:: text

    Usage: restcli run [OPTIONS] GROUP REQUEST [ENV]...

    Options:
      --help  Show this message and exit.

`restcli view`:

.. code-block:: text

    Usage: restcli view [OPTIONS] GROUP [REQUEST] [ATTR]

    Options:
      --help  Show this message and exit.

`restcli repl`:

.. code-block:: text

    Usage: restcli repl [OPTIONS]

    Options:
      --help  Show this message and exit.


Interactive Prompt
~~~~~~~~~~~~~~~~~~

The interactive prompt is a read-eval-print loop which supports the same API
as the commandline interface, but with a few additional commands for
convenience:

- `help`: Display general help or help for a specific command.
- `run`: Run an Request.
- `view`: Inspect a Group, Request, or Request Attribute.
- `env`: Print the currently loaded Environment.
- `reload`: Reload the current Collection and/or Environment from disk.
- `save`: Save the current Environment to disk.
- `change_collection`: Change the current Collection file to something else.
- `change_env`: Change the current Environment file to something else.

You may run `help COMMAND` on any command for more information about arguments
and usage of the given command.


License
-------

This software is distributed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0>`__. See LICENSE
for more information.
