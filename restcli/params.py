from restcli.utils import AttrMap

REQUIRED_REQUEST_PARAMS = AttrMap(("method", str), ("url", str))
REQUEST_PARAMS = AttrMap(
    *REQUIRED_REQUEST_PARAMS.items(),
    ("query", str),
    ("headers", dict),
    ("body", str),
    ("script", str),
)
CONFIG_PARAMS = AttrMap(("defaults", dict), ("lib", list))
