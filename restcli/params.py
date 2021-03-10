from restcli.utils import AttrMap

REQUIRED_REQUEST_PARAMS = AttrMap(
    ("method", str),
    ("url", str),
)
REQUEST_PARAMS = AttrMap(
    ("query", str),
    ("headers", dict),
    ("body", str),
    ("script", str),
    *REQUIRED_REQUEST_PARAMS.items(),
)
CONFIG_PARAMS = AttrMap(
    ("defaults", dict),
    ("lib", list),
)
