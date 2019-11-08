def define(response, env, *args, **kwargs):

    from pprint import pformat

    class UnexpectedResponse(Exception):
        """An error raised when the response is not as expected.
        
        TODO: make this a first-class citizen available to all scripts.
        """

        def __init__(self, response, msg="unexpected response"):
            self.response = response
            self.msg = msg

        def __str__(self):
            return "%s: %s" % (self.msg, pformat(self.response, indent=2))

    def assert_status(expected_status, error_msg=None):
        """Raise an error if response status code is not `expected_status`."""
        if response.status_code != expected_status:
            raise UnexpectedResponse(
                response, "expected status code '%s'" % expected_status
            )

    def set_env(status, var, path):
        """Shortcut for checking the status code and setting an env var."""
        if response.status_code == status:
            value = response.json()

            try:
                for key in path:
                    value = value[key]
            except (IndexError, KeyError):
                return
            env[var] = value

    return locals()
