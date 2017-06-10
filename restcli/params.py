from restcli.utils import AttrMap

REQUIRED_REQUEST_ATTRS = AttrMap(
    ('method', str),
    ('url', str),
)
REQUEST_ATTRS = AttrMap(
    ('headers', dict),
    ('body', str),
    ('script', str),
    *REQUIRED_REQUEST_ATTRS.items(),
)
META_ATTRS = AttrMap(
    ('defaults', dict),
    ('lib', list),
)
