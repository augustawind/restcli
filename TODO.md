# TODO

## Short Term

- [ ] Write a terminal UI using `prompt_toolkit`.
- [ ] Create a test server that can be used to try out examples without
      using httpbin.
    - POST should create a new resource named after the URL's _path_, using
      the request body as its fields and URL params to set a special field
      called "params".
    - GET/PUT/PATCH/DELETE should operate on that resource.
- [ ] Add more examples (using scripts, etc.).
- [ ] Nested groups.
- [ ] Handle errors gracefully.
- [ ] Write more unit tests.

## Roadmap

- [ ] Implement localization using ugettext.
- [ ] Automate grabbing --help output and inserting it into README.
- [ ] Export Collections to/from Postman.
