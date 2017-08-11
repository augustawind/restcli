.. _overview:

========
Overview
========

**restcli** is a terminal web API client written in Python. It draws inspiration
from `Postman`_ and `HTTPie`_, and offers some of the best features of both.

Features
========

* read requests from YAML files
* scripting
* parameterized requests using `Jinja2`_ templating
* expressive commandline syntax, inspired by `HTTPie`_
* first-class JSON support
* interactive prompt with autocomplete
* colored output

Roadmap
-------

Here's what we have in store for the foreseeable future.

* autocomplete Group and Request names in the command prompt
* support for other formats (plaintext, forms, file uploads)
* request plans: run requests back-to-back with one command
* import from/export to Postman JSON format

Ideas
-----

Here are some feature concepts that may or may not get implemented.

* full screen terminal UI via `python_prompt_toolkit`_
* in-app request editor (perhaps using `pyvim`_)

Core Concepts
=============

In this section we'll get a bird's eye view of **restcli**\'s core concepts.
After reading this section, you should be ready for the `Tutorial <tutorial>`_.

Collections
-----------

**restcli** understands your API through YAML files called Collections. A
Collection is a bunch of Requests organized into named Groups. They look like
this:

.. code-block:: yaml

    group1:
        request1:
            # ...
        request2:
            # ...
    group2:
        # ...

On the commandline, Requests are accessed by specifying the Group name followed
by the Request name, like so:

.. code-block:: console

    restcli run GROUP REQUEST

Groups are purely organizational, so let's look at Requests.

Requests
--------

Requests contain the information **restcli** needs to interact with your API.
They look like this:

.. code-block:: yaml

    method: post
    url: "http://httpbin.org/post"
    headers:
        Content-Type: application/json
        Accept: application/json
    body: |
        name: {{ name }}
        age: 24

When this Request is executed, a POST request will be made to
http://httpbin.org/post with the specified Content-Type and Accept headers
and a JSON payload containing an object with two keys, "name" and "age".

Notice the double curly brackets inside the "body" field: ``name: {{ name }}``.
This is a template variable. Template variables are given concrete values by
*Environments*.

Environments
------------

Environments are YAML files that define values for use in templating. They
look like this:

.. code-block:: yaml

    key1: value1
    key2: value2
    key3: value3

Keys must be strings, but values can be any type, including objects and arrays.
Here's an example Environment:

.. code-block:: yaml

    name: Linus Torvalds

Applying this Environment to the example Request "body" from the previous
section would yield the following result:

.. code-block:: yaml

    body: |
        name: Linus Torvalds
        age: 24

Next Steps
----------

Coming soon...


.. _Postman: https://www.getpostman.com/postman
.. _HTTPie: https://httpie.org/
.. _Jinja2: http://jinja.pocoo.org/
.. _python_prompt_toolkit: https://github.com/jonathanslenders/python-prompt-toolkit
.. _pyvim: https://github.com/jonathanslenders/pyvim
