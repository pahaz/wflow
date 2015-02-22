import os
import sys
import traceback

from wutil._six import string_types

from wutil.file import set_executable
from wutil.execute import execute

from .command_manager import CommandManager
from .event_manager import EventManager

__author__ = 'pahaz'


def is_python_plugin_module(path):
    py_init = os.path.join(path, '__init__.py')
    return os.path.exists(py_init)


def is_simple_plugin_module(path):
    hook = os.path.join(path, 'hooks')
    return os.path.exists(hook)


def make_event_listener(name, hook_script_path, venv_path, env):
    if not os.access(hook_script_path, os.X_OK):
        set_executable(hook_script_path)
    cwd = os.path.abspath(os.path.join(hook_script_path, '..', '..'))

    def event_listener(**kwargs):
        kwargs = {k: str(v) for k, v in kwargs.items()}
        kwargs.update(env.items())
        venv_activate_path = os.path.join(venv_path, 'bin', 'activate')
        out, _, _ = execute(
            hook_script_path,
            env=kwargs,
            init_env_script=venv_activate_path,
            cwd=cwd,

            stderr_to_stdout=False,
            is_collecting_to_buf_stdout=False,
            is_collecting_to_buf_stderr=False,
            stdout=sys.stdout.buffer,
            stderr=sys.stderr.buffer, )
        return out

    event_listener.__name__ = name
    return event_listener


def load_simple_module(path, venv_path, command_manager, event_manager, env):
    hook = os.path.join(path, 'hooks')
    for name in os.listdir(hook):
        path = os.path.join(hook, name)
        event_listener = make_event_listener(name, path, venv_path, env)
        event_manager.add_event_listener(name, event_listener)


def load_python_module(path, venv_path, command_manager, event_manager, env):
    path_dir, path_name = os.path.split(path)
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

    py_init = os.path.join(path, '__init__.py')
    if os.path.exists(py_init):
        plugin_module = __import__(path_name)
        if hasattr(plugin_module, 'load') and callable(plugin_module.load):
            plugin_module.load(command_manager, event_manager, env)


def make_managers_and_load_them_from_plugin_modules(plugins_path,
                                                    venv_path,
                                                    env):
    """Factory function which make managers and extends them from
    the plugins modules.
    :return: tuple(CommandManager(), EventManager())
    """
    if not isinstance(plugins_path, string_types):
        raise TypeError("Invalid plugins path.")
    if not os.path.exists(plugins_path):
        raise TypeError("Plugin path {0} not exists".format(plugins_path))
    command_manager = CommandManager()
    event_manager = EventManager()
    _venv_path = venv_path
    _env = env

    for dir_ in os.listdir(plugins_path):
        path = os.path.abspath(os.path.join(plugins_path, dir_))
        try:
            if is_python_plugin_module(path):
                load_python_module(path,
                                   _venv_path,
                                   command_manager,
                                   event_manager,
                                   _env)
            elif is_simple_plugin_module(path):
                load_simple_module(path,
                                   _venv_path,
                                   command_manager,
                                   event_manager,
                                   _env)
        except Exception as err:
            sys.stdout.write('Could not load {0} {1}\n'.format(path, err))
            traceback.print_exc(file=sys.stdout)

    return command_manager, event_manager