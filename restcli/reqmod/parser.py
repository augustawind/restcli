from restcli.reqmod.mods import parse_mod
from restcli.reqmod.updater import UPDATERS, Updates


def parse(lexemes):
    """Parse a sequence of Lexemes.

    Args:
        lexemes: An iterable of Lexeme objects.

    Returns:
        An Updates object that can be used to update Requests.
    """
    updates = Updates()

    for lexeme in lexemes:
        # Parse Mod
        mod = parse_mod(lexeme.value)

        # Create Updater
        updater_cls = UPDATERS[lexeme.action]
        updater = updater_cls(mod.param, mod.key, mod.value)
        updates.append(updater)

    return updates


examples = [
    # Set a header (:)
    '''Authorization:'JWT abc123\'''',
    # Delete a header (-d)
    '''-d Authorization:''',
    # Set a JSON param (string only) (=)
    '''description="A test Device."''',
    # Append (-a) to a url parameter (==)
    '''-a _annotate==,counts''',
    # Set a nested (.) JSON field (non-string) (:=)
    '''.location.postal_code:=33705''',
    # Set a nested (. / []) JSON field (string) (=)
    '''.conditions[0].variable=ambient_light''',
    # Delete (-d) a nested (.) JSON field
    '''-d .location.addr2''',
]
