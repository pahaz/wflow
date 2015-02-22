from copy import deepcopy
import os
import collections
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

__author__ = 'pahaz'
DEFAULT_SECTION = "DEFAULT"


def is_hashable_type(t):
    try:
        hash(t)
    except TypeError:
        return False
    return True


class Env(collections.Mapping):
    def __init__(self, dict_, raise_attribute_error=True):
        for k, v in dict_.items():
            if not is_hashable_type(v):
                raise TypeError('Env object does`t support unhashable value: '
                                '{0}'.format(v))
        self.__dict__['_secret'] = deepcopy(dict_)
        self.__dict__['_raise_attribute_error'] = raise_attribute_error

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            if self.__dict__['_raise_attribute_error']:
                raise AttributeError('{0} not in Env object'.format(key))
        return None

    def __setattr__(self, key, value):
        raise TypeError('Env object does not support setattr')

    def __delattr__(self, item):
        raise TypeError('Env object does not support delattr')

    def as_dict(self):
        return deepcopy(self.__dict__['_secret'])

    # Mapping

    def __getitem__(self, key):
        return self.__dict__['_secret'][key]

    def __iter__(self):
        return iter(self.__dict__['_secret'])

    def __len__(self):
        return len(self.__dict__['_secret'])


def load_env(ini_file,
             raise_open_error=True,
             raise_attribute_error=True):
    """
    Loading configuration form .ini file and override values
    from OS ENVIRONMENT

    :param ini_file: execution file (__file__)
    :param check_paths: if env key ends with _PATH do check path exists.
    :return: object with attributes
    """
    if not os.path.exists(ini_file) or not os.path.isfile(ini_file):
        if raise_open_error:
            raise RuntimeError('error: config file {0} not exists'
                               .format(ini_file))
        return Env({}, raise_attribute_error=raise_attribute_error)

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
    config = Env(config, raise_attribute_error=raise_attribute_error)
    return config


def check_paths(config):
    for k, v in config.items():
        if k.endswith("_PATH") and not os.path.exists(v):
            raise Exception('error: path not exists {0} = {1}'
                            .format(k, v))
