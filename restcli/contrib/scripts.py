def define(response, env, *args, **kwargs):

    def set_env(status, var, path, ignore_missing_index=False,
                ignore_missing_key=False):
        """Shortcut for checking the status code and setting an env var."""
        if response.status_code == status:
            value = response.json()

            for key in path:
                try:
                    value = value[key]
                except IndexError as exc:
                    if not ignore_missing_index:
                        raise exc
                except KeyError as exc:
                    if not ignore_missing_key:
                        raise exc
            env[var] = value

    return locals()
