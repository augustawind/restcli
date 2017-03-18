from collections import OrderedDict

import yaml
from yaml.resolver import BaseResolver

__all__ = ['literal_str', 'load', 'dump']


# Custom Loaders and Dumpers

class CustomLoader(yaml.Loader): pass
class SafeCustomLoader(yaml.SafeLoader): pass

class CustomDumper(yaml.Dumper): pass
class SafeCustomDumper(yaml.SafeDumper): pass


# OrderedDict support

def ordered_constructor(loader, node):
    loader.flatten_mapping(node)
    pairs = loader.construct_pairs(node)
    return OrderedDict(pairs)

CustomLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG, ordered_constructor)
SafeCustomLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG, ordered_constructor)


def dict_representer(dumper, data):
    return dumper.represent_mapping(
        BaseResolver.DEFAULT_MAPPING_TAG, data.items())

CustomDumper.add_representer(OrderedDict, dict_representer)
SafeCustomDumper.add_representer(OrderedDict, dict_representer)


# String literal style support ("|")

class literal_str(str): pass

def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

CustomDumper.add_representer(literal_str, literal_unicode_representer)
SafeCustomDumper.add_representer(literal_str, literal_unicode_representer)


# Dump and load functions

def dump(data, stream=None, safe=False, many=False, **kwargs):
    kwargs.setdefault('default_flow_style', False)
    Dumper = SafeCustomDumper if safe else CustomDumper
    if not many:
        data = [data]
    return yaml.dump_all(data, stream, Dumper, **kwargs)


def load(stream, safe=False, many=False):
    Loader = SafeCustomLoader if safe else CustomLoader
    if many:
        return tuple(yaml.load_all(stream, Loader))
    else:
        return yaml.load(stream, Loader)
