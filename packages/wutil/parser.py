import configparser
import os

__author__ = 'pahaz'
DEFAULT_SECTION = "DEFAULT"


class Config(object):
    def __init__(self, dict_, suppress_attribute_error=False):
        self.__dict = dict_
        self.__suppress_attribute_error = suppress_attribute_error

    def __getattr__(self, item):
        value = self.__dict.get(item)
        if not self.__suppress_attribute_error and not value:
            raise AttributeError
        return value

    def items(self):
        return self.__dict.items()


def load_configs(exec_file, check_paths=False,
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
        return Config({}, suppress_attribute_error=suppress_attribute_error)

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
                   if not k.startswith('__')])

    config = Config(config, suppress_attribute_error=suppress_attribute_error)

    if check_paths:
        for k, v in config.items():
            if k.endswith("_PATH") and not os.path.exists(v):
                raise RuntimeError('error: path not exists {2} = {1} '
                                   'from config file {0}'
                                   .format(path_ini, v, k))

    return config
