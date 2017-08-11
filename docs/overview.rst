.. _overview:

########
Overview
########

**restcli** is a terminal web API client written in Python. It draws inspiration
from `Postman`_ and `HTTPie`_, and offers some of the best features of both.

********
Features
********

* read requests from YAML files
* scripting
* parameterized requests using `Jinja2`_ templating
* expressive commandline syntax, inspired by `HTTPie`_
* first-class JSON support
* interactive prompt with autocomplete
* colored output

Roadmap
=======

Short-term
----------

Here's what we have in store for the foreseeable future.

* autocomplete Group and Request names in the command prompt
* support for other formats (plaintext, forms, file uploads)
* request plans: run requests back-to-back with one command
* import from/export to Postman JSON format

Long-term
---------

Here are some longer-term feature concepts that may or may not get implemented.

* full screen terminal UI via `python_prompt_toolkit`_
* in-app request editor (perhaps using `pyvim`_)

*************
Core Concepts
*************

In this section we'll get a bird's eye view of **restcli**\'s core concepts.
After reading this section, you should be ready for the `Tutorial <tutorial>`_.

.. _overview_collections:

Collections
===========

**restcli** understands your API through YAML files called *Collections*.
Collections are objects composed of *Groups*, which are again objects composed
of `Requests <overview_requests>`_. A Collection is essentially just a bunch of
Requests; Groups are purely organizational.

.. code-block:: yaml

    ---
    weapons:
        equip:
            # <<request>>
        info:
            # <<request>>
    potions:
        drink:
            # <<request>>

This Collection has two Groups. The first Group, ``weapons``, has two Requests,
``equip`` and ``info``. The second has Group is called "potions" and has one
Request called "drink". This is a good example of a well-organized Collection —
Groups were used to provide context, and even though we're using placeholders,
it's easy to infer the purpose of each Request.

.. _overview_requests:

Requests
========

A Request is a YAML object that describes a particular action against an API.
Requests are the bread and butter of **restcli**.

.. code-block:: yaml

    method: post
    url: "http://httpbin.org/post"
    headers:
        Content-Type: application/json
        Authorization: {{ password }}
    body: |
        name: bar
        age: {{ cool_number }}
        is_cool: true

At a glance, we can get a rough idea of what's going on. This Request
uses the POST ``method`` to send some data (``body``) to the ``url``
http://httpbin.org/post\, with the given Content-Type and Authorization
``headers``.

Take note of the stuff in between the double curly brackets: ``{{ password }}``,
``{{ cool_number }}``. These are template variables, which must be interpolated
with concrete values before executing the request, which brings us to our next
topic...

.. _overview_environments:

Environments
============

An Environment is a YAML object that defines values which are used to
interpolate template variables in a Collection. Environments can be be modified
with `Request scripts <tutorial_scripting>`_, which we cover in the `Tutorial
<tutorial>`_.

This Environment could be used with the Request we looked at in the `previous
section <overview_collections>`_:

.. code-block:: yaml

    password: sup3rs3cr3t
    cool_number: 25

Once the Environment is applied, the Request would look something like this:

.. code-block:: yaml

    method: post
    url: "http://httpbin.org/post"
    headers:
        Content-Type: application/json
        Authorization: sup3rs3cr3t
    body: |
        name: bar
        age: 25
        is_cool: true

**********
Next Steps
**********

The recommended way to continue learning is the `Tutorial
<tutorial>`_.

**Coming soon**: reference documentation.

.. _Postman: https://www.getpostman.com/postman
.. _HTTPie: https://httpie.org/
.. _Jinja2: http://jinja.pocoo.org/
.. _python_prompt_toolkit: https://github.com/jonathanslenders/python-prompt-toolkit
.. _pyvim: https://github.com/jonathanslenders/pyvim
