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
    return OrderedDict(loader.construct_pairs(node))

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

def dump(data, stream=None, safe=False, **kwargs):
    """Serialize an OrderedDict into YAML, preserving mapping order."""
    kwargs.setdefault('default_flow_style', False)
    Dumper = SafeCustomDumper if safe else CustomDumper
    return yaml.dump(data, stream, Dumper, **kwargs)


def load(stream, safe=False):
    """Deserialize an OrderedDict from YAML, preserving mapping order."""
    Loader = SafeCustomLoader if safe else CustomLoader
    return yaml.load(stream, Loader)
