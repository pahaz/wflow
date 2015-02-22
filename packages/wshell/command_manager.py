from wutil._six import string_types
from .abc_command import AbstractCommand

__author__ = 'pahaz'


class CommandManager(object):
    """
    Command manager.

    Interface:
     - add_command(command_class)
     - find_command(argv)

    Plugin example:

        # simple_plugin/__init__.py

        import logging
        from wshell.abc_command import AbstractCommand


        class SimpleCommand(AbstractCommand):
            "A simple command that prints a message."

            log = logging.getLogger(__name__)

            def take_action(self, parsed_args):
                self.log.info('sending greeting')
                self.log.debug('debugging')
                self.app.stdout.write('hi!\n')


        def load(command_manager, event_manager, env):
            command_manager.add_command(SimpleCommand)

    """
    def __init__(self):
        self._commands = {}

    def add_command(self, command_class):
        if not issubclass(command_class, AbstractCommand):
            raise TypeError('`command_class` is not a Command subclass')

        name = command_class.get_name()
        self._commands[name] = command_class

    def find_command(self, argv):
        """Given an argument list, find a command and
        return the processor and any remaining arguments.
        """
        if isinstance(argv, string_types):
            raise TypeError('`argv` is not support string type')

        search_args = argv[:]
        name = ''
        while search_args:
            if search_args[0].startswith('-'):
                raise ValueError('Invalid command {0}'.format(search_args[0]))
            next_val = search_args.pop(0)
            name = '%s %s' % (name, next_val) if name else next_val
            command = self._commands.get(name)
            if command:
                return command, name, search_args
        else:
            raise ValueError('Unknown command {0}'.format(argv))

    def __iter__(self):
        return iter(self.items())

    def items(self):
        return self._commands.items()
