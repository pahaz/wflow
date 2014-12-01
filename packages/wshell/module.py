import os
import sys

from wutil.file import set_executable
from wutil.execute import execute


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


def load_simple_module(path, manager, venv_path, env):
    hook = os.path.join(path, 'hooks')
    for name in os.listdir(hook):
        path = os.path.join(hook, name)
        event_listener = make_event_listener(name, path, venv_path, env)
        manager.add_event_listener(name, event_listener)


def load_python_module(path, manager):
    path_dir, path_name = os.path.split(path)
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

    py_init = os.path.join(path, '__init__.py')
    if os.path.exists(py_init):
        plugin_module = __import__(path_name)
        if hasattr(plugin_module, 'load') and callable(plugin_module.load):
            plugin_module.load(manager)
