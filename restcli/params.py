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
VALID_URL_CHARS = (
    r'''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'''
    r'''0123456789-._~:/?#[]@!$&'()*+,;=`'''
)
