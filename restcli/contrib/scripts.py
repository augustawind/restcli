def define(response, env, *args, **kwargs):

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
