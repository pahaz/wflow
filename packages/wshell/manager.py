import os
import traceback
import sys

from six import string_types

from .module import is_python_plugin_module
from .module import load_python_module
from .module import is_simple_plugin_module
from .module import load_simple_module
from .command_manager import CommandManager
from .event_manager import EventManager


__author__ = 'pahaz'


class Manager(CommandManager, EventManager):
    def __init__(self, plugins_path, venv_path, env):
        if not isinstance(plugins_path, string_types):
            raise TypeError("Invalid plugins path.")
        if not os.path.exists(plugins_path):
            raise TypeError("Plugin path {0} not exists".format(plugins_path))

        CommandManager.__init__(self)
        EventManager.__init__(self)
        self._venv_path = venv_path
        self._env = env
        self._plugins_path = plugins_path
        self._load_commands()

    def get_env(self):
        return self._env

    def _load_commands(self):
        base_path = self._plugins_path
        for dir_ in os.listdir(base_path):
            path = os.path.abspath(os.path.join(base_path, dir_))
            try:
                if is_python_plugin_module(path):
                    load_python_module(path, self)
                elif is_simple_plugin_module(path):
                    load_simple_module(path, self,
                                       self._venv_path,
                                       self._env)
            except Exception as err:
                sys.stdout.write('Could not load {0} {1}\n'.format(path, err))
                traceback.print_exc(file=sys.stdout)
