RESTCLI
=======

An API client library and CLI written in Python.
It's Postman for terminal lovers!

-  Overview_
-  Installation_
-  File_Format_
-  Commandline_Interface_
-  License_


.. _Overview:

Overview
~~~~~~~~

restcli is a library and commandline utility for API testing. It reads requests
from a YAML file and supports scripting and environment variables.

.. _Installation:

Docker Installation
~~~~~~~~~~~~~~~~~~~

**restcli** can be run from docker without additional dependencies.
Assuming docker is installed, the docker image can be built
by running:

.. code-block:: sh

    $ docker build -t restcli .


Then run it with:

.. code-block:: sh

    $ docker run -it restcli repl

.. _File_Format:

File Format
~~~~~~~~~~~

Requests are organized into Groups, which are like folders of Requests. The file
should contain an object mapping Group names to Groups. Each Group object should
contain an object mapping Request names to Requests.

Request Objects
_______________

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

`headers` and `body` are both strings, but must contain valid YAML markup.
This is in order to support templating. `headers` must be a 1-dimensional object
of key-value string pairs. `body` can be any valid request body format.
Only JSON bodies are supported at this time.

`scripts` is an object mapping names to Python3 scripts that are executed in
specific contexts based on the name. Only the `post_request` script is supported
at this time. This is ran after the request was made, and is provided the
`request` object (from the Python `requests` library) as well as the `env`
Environment, which can be modified in the script.

Environment
___________

The Environment is another YAML file which must be a flat, 1-dimensional object
of key-value pairs. The values can be any valid JSON type. These variables are
available anywhere in a Request where Jinja2 templates are supported, as well
as in the `scripts` portion of a Request where they can be read from and
modified.

Here is an example Environment for the above example Request:

.. code-block:: yaml
    server_url: http://quux.org
    foo_age: 15

.. _Commandline_Interface:

Commandline Interface
~~~~~~~~~~~~~~~~~~~~~

The commandline interface is an interactive prompt which provides commands for
interacting with the restcli library. The following commands are supported:

- `help`: Display general help or help for a specific command.
- `run`: Run an Request in a Group.
- `view`: Inspect a Group, Request, or Request Attribute.
- `env`: Print the currently loaded Environment.
- `reload`: Reload the initial Groups file and Environment file from disk.
- `save`: Save the current Environment to disk.

You may run `help COMMAND` on any command for more information about arguments
and usage of the given command.

There are also plans for a regular commandline utility as well.

.. _License:

License
~~~~~~~

This app is distributed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0>`__, see LICENSE
for more information.
