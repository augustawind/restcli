from collections import OrderedDict

import yaml
from yaml.resolver import BaseResolver

__all__ = ["YamlLiteralStr", "load", "dump"]


# Custom Loaders and Dumpers


class CustomLoader(yaml.Loader):
    pass


class SafeCustomLoader(yaml.SafeLoader):
    pass


class CustomDumper(yaml.Dumper):
    pass


class SafeCustomDumper(yaml.SafeDumper):
    pass


def register_constructor(tag):
    def decorator(constructor):
        CustomLoader.add_constructor(tag, constructor)
        SafeCustomLoader.add_constructor(tag, constructor)

    return decorator


def register_representer(data_type):
    def decorator(representer):
        CustomDumper.add_representer(data_type, representer)
        SafeCustomDumper.add_representer(data_type, representer)

    return decorator


# OrderedDict support


@register_constructor(BaseResolver.DEFAULT_MAPPING_TAG)
def ordered_constructor(loader, node):
    loader.flatten_mapping(node)
    pairs = loader.construct_pairs(node)
    return OrderedDict(pairs)


@register_representer(OrderedDict)
def dict_representer(dumper, data):
    return dumper.represent_mapping(
        BaseResolver.DEFAULT_MAPPING_TAG, data.items()
    )


# String literal style support ("|")


class YamlLiteralStr(str):
    pass


@register_constructor(BaseResolver.DEFAULT_SCALAR_TAG)
def unicode_literal_constructor(loader: yaml.Loader, node: yaml.ScalarNode):
    scalar = loader.construct_scalar(node)
    if node.style == "|":
        return YamlLiteralStr(scalar)
    return scalar


@register_representer(YamlLiteralStr)
def unicode_literal_representer(dumper, data):
    return dumper.represent_scalar(
        BaseResolver.DEFAULT_SCALAR_TAG, data, style="|"
    )


# Dump and load functions


def dump(data, stream=None, safe=False, many=False, **kwargs):
    kwargs.setdefault("default_flow_style", False)
    Dumper = SafeCustomDumper if safe else CustomDumper
    if not many:
        return yaml.dump(data, stream, Dumper, **kwargs)
    return yaml.dump_all(data, stream, Dumper, **kwargs)


def load(stream, safe=False, many=False):
    Loader = SafeCustomLoader if safe else CustomLoader
    if many:
        return tuple(yaml.load_all(stream, Loader))
    else:
        return yaml.load(stream, Loader)
