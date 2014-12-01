import configparser
from copy import deepcopy
import os

__author__ = 'pahaz'
DEFAULT_SECTION = "DEFAULT"


class Env(object):
    def __init__(self, dict_, suppress_attribute_error=False):
        self.__dict__['_secret'] = deepcopy(dict_)
        self.__dict__['_suppress_attribute_error'] = suppress_attribute_error

    def __getattr__(self, key):
        value = self.__dict__['_secret'].get(key)
        if not self.__dict__['_suppress_attribute_error'] and not value:
            raise AttributeError('{0} not in Env object'.format(key))
        return value

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __setattr__(self, key, value):
        raise TypeError('Env object does not support setattr')

    def __delattr__(self, item):
        raise TypeError('Env object does not support delattr')

    def items(self):
        return self.__dict__['_secret'].items()

    def as_dict(self):
        return deepcopy(self.__dict__['_secret'])


def load_env_for_file(exec_file, check_paths=False,
                      suppress_open_error=False,
                      suppress_attribute_error=False):
    """
    Loading configuration form file `executable_file`.ini and override values
    from OS ENVIRONMENT

    :param exec_file: execution file (__file__)
    :param check_paths: if env key ends with _PATH do check path exists.
    :return: object with attributes
    """
    path_ini = exec_file + '.ini'
    if not os.path.exists(path_ini) or not os.path.isfile(path_ini):
        if not suppress_open_error:
            raise RuntimeError('error: config file {0} not exists'
                               .format(path_ini))
        return Env({}, suppress_attribute_error=suppress_attribute_error)

    c = configparser.ConfigParser(delimiters=('=',))
    # http://stackoverflow.com/a/19359720/941020
    # hotfix for case sensitive names
    c.optionxform = str

    # c.write(open(path_ini, 'w', encoding='utf-8'))
    with open(path_ini, 'r', encoding='utf-8') as f:
        c.read_file(f)

    config = c.items(DEFAULT_SECTION)

    # override configs from ENVIRONMENT
    # secure magic names `__`
    config = dict([(k, os.environ.get(k, v)) for k, v in config
                   if not k.startswith('__') and k.upper() == k])

    config = Env(config, suppress_attribute_error=suppress_attribute_error)

    if check_paths:
        for k, v in config.items():
            if k.endswith("_PATH") and not os.path.exists(v):
                raise RuntimeError('error: path not exists {2} = {1} '
                                   'from config file {0}'
                                   .format(path_ini, v, k))

    return config
