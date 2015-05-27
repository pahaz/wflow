from __future__ import unicode_literals, print_function, generators, division
import collections
import copy
import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from wutil.env import EnvStackLayer, is_hashable_type
from wutil.mixin import AttributeImmutableMixin


__author__ = 'pahaz'
DEFAULT_SECTION = "DEFAULT"


class EnvStack(collections.Mapping, AttributeImmutableMixin):
    def __init__(self, init_env_layer=None):
        self.__dict__['_stack'] = []
        if init_env_layer:
            self.push(init_env_layer)

    def _get_top(self):
        return self._stack[-1] if self.layers_count() else {}

    def push(self, layer):
        if not isinstance(layer, (EnvStackLayer, dict)):
            raise TypeError('Layer type must be `EnvStackLayer` or `dict`')
        if isinstance(layer, EnvStackLayer):
            layer = layer.as_dict()
        if isinstance(layer, dict):
            for k, v in layer.items():
                if not is_hashable_type(v):
                    raise TypeError('Layer object does`t support unhashable: '
                                    '{0}'.format(v))

        top = self._get_top()
        new_top = copy.deepcopy(top)
        new_top.update(layer)
        self._stack.append(new_top)

    def pop(self):
        self._stack.pop()

    def layers_count(self):
        return len(self._stack)

    def layer_copy(self, index):
        return copy.deepcopy(self._stack[index])

    def as_dict(self):
        top = self._get_top()
        return copy.deepcopy(top)

    # Mapping

    def __getitem__(self, key):
        top = self._get_top()
        return top[key]

    def __iter__(self):
        top = self._get_top()
        return iter(top)

    def __len__(self):
        top = self._get_top()
        return len(top)


def load_env_stack(ini_file, ignore_open_error=True):
    """
    Loading configuration form .ini file and override values
    from OS ENVIRONMENT

    :param ini_file: execution file (__file__)
    :param ignore_open_error: ignore open errors
    :return: object with attributes
    """
    if not os.path.exists(ini_file) or not os.path.isfile(ini_file):
        if ignore_open_error:
            raise RuntimeError('error: config file {0} not exists'
                               .format(ini_file))
        return EnvStack()

    c = configparser.ConfigParser(delimiters=('=',))
    # http://stackoverflow.com/a/19359720/941020
    # hotfix for case sensitive names
    c.optionxform = str

    # c.write(open(ini_file, 'w', encoding='utf-8'))
    with open(ini_file, 'r', encoding='utf-8') as f:
        c.read_file(f)

    config = c.items(DEFAULT_SECTION)

    # override configs from ENVIRONMENT
    # secure magic names `__`
    config = dict([(k, os.environ.get(k, v)) for k, v in config
                   if not k.startswith('__') and k.upper() == k])
    config = EnvStack(config)
    return config
