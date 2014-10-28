import configparser
import os

__author__ = 'pahaz'
DEFAULT_SECTION = "DEFAULT"


def load_configs(base_path, check_paths=False):
    path_ini = base_path + '.ini'
    if not os.path.exists(path_ini) or not os.path.isfile(path_ini):
        raise RuntimeError('error: config file {0} not exists'
                           .format(path_ini))

    c = configparser.ConfigParser(delimiters=('=',))
    # http://stackoverflow.com/a/19359720/941020 hotfix for case sensitive
    # names
    c.optionxform = str

    # c.write(open(path_ini, 'w', encoding='utf-8'))
    with open(path_ini, 'r', encoding='utf-8') as f:
        c.read_file(f)

    config = dict(c.items(DEFAULT_SECTION))
    config_obj = type('config', (object,), config)
    config_obj.items = lambda: config.items()

    if check_paths:
        for k, v in config:
            if k.endswith("_PATH") and not os.path.exists(v):
                raise RuntimeError('error: path not exists {2} = {1} '
                                   'from config file {0}'
                                   .format(path_ini, v, k))

    return config_obj
