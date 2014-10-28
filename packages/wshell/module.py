import os
import sys

__author__ = 'pahaz'


def is_python_plugin_module(path):
    py_init = os.path.join(path, '__init__.py')
    return os.path.exists(py_init)


def is_simple_plugin_module(path):
    # TODO: do this!
    return False
    # run = os.path.join(path, 'run')
    # hooks = os.path.join(path, 'hooks')
    # is_shell_command = os.path.exists(run) and os.access(path, os.X_OK)
    # is_hooks_dir = os.path.exists(hooks) and os.path.isdir(hooks)
    # return is_shell_command or is_hooks_dir


def load_simple_module(path, manager):
    # TODO: do this!
    raise NotImplementedError


def load_python_module(path, manager):
    path_dir, path_name = os.path.split(path)
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

    py_init = os.path.join(path, '__init__.py')
    if os.path.exists(py_init):
        plugin_module = __import__(path_name)
        if hasattr(plugin_module, 'load') and callable(plugin_module.load):
            plugin_module.load(manager)
