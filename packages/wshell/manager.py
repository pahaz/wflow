import logging
import os

from cliff.commandmanager import EntryPointWrapper
from six import string_types

from .module import is_python_plugin_module
from .module import load_python_module
from .module import is_simple_plugin_module
from .module import load_simple_module


__author__ = 'pahaz'


class CommandManager(object):
    """
    Command manager.

    Interface:
     - add_command(name, command_class)
     - find_command(argv)

    Plugin example:

        # simple_plugin/__init__.py

        import logging
        from wshell.command import Command


        class Simple(Command):
            "A simple command that prints a message."

            log = logging.getLogger(__name__)

            def take_action(self, parsed_args):
                self.log.info('sending greeting')
                self.log.debug('debugging')
                self.app.stdout.write('hi!\n')


        def load(manager):
            manager.add_command('simple', Simple)

    """
    log = logging.getLogger("manager")

    def __init__(self, plugins_path):
        if not isinstance(plugins_path, string_types):
            raise TypeError("Invalid plugins path.")
        if not os.path.exists(plugins_path):
            raise TypeError("Plugin path {0} not exists".format(plugins_path))

        self._plugins_path = plugins_path
        self._commands = {}
        self._load_commands()

    def __iter__(self):
        return iter(self._commands.items())

    def _load_commands(self):
        base_path = self._plugins_path
        for dir_ in os.listdir(base_path):
            path = os.path.abspath(os.path.join(base_path, dir_))
            if is_python_plugin_module(path):
                load_python_module(path, self)
            elif is_simple_plugin_module(path):
                load_simple_module(path, self)

    def add_command(self, name, command_class):
        self._commands[name] = EntryPointWrapper(name, command_class)

    def find_command(self, argv):
        """Given an argument list, find a command and
        return the processor and any remaining arguments.
        """
        search_args = argv[:]
        name = ''
        while search_args:
            if search_args[0].startswith('-'):
                raise ValueError('Invalid command {0}'.format(search_args[0]))
            next_val = search_args.pop(0)
            name = '%s %s' % (name, next_val) if name else next_val
            command_wrapper = self._commands.get(name)
            if command_wrapper:
                command_class = command_wrapper.load()
                return command_class, name, search_args
        else:
            raise ValueError('Unknown command {0}'.format(argv))
