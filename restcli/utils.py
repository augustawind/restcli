from collections import OrderedDict

import yaml
from yaml.resolver import BaseResolver


def dump_ordered(data, stream=None, Dumper=yaml.Dumper, **kwargs):
    """Serialize an OrderedDict into YAML, preserving mapping order."""
    class OrderedDumper(Dumper):
        pass
    def dict_representer(dumper, data):
        return dumper.represent_mapping(
            BaseResolver.DEFAULT_MAPPING_TAG, data.items())
    OrderedDumper.add_representer(OrderedDict, dict_representer)
    kwargs.setdefault('default_flow_style', False)
    return yaml.dump(data, stream, OrderedDumper, **kwargs)


def load_ordered(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """Deserialize an OrderedDict from YAML, preserving mapping order."""
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return yaml.load(stream, OrderedLoader)
