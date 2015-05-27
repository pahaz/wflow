from __future__ import unicode_literals, print_function, generators, division
import logging
import threading
import collections

from wshell.event_manager import EventManager
from wutil._six import string_types, text_type, binary_type
from .abc_command import AbstractCommand
from wutil.env_stack import EnvStack

__author__ = 'pahaz'


class CommandManager(object):
    """
    Command manager.

    Interface:
     - add_command(command_class)
     - find_command(argv)
     - run_command(argv, env_stack)

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
    ERROR_RETURN_CODE = 1
    COMMAND_NOT_FOUND_RETURN_CODE = 2

    log = logging.getLogger(__name__)

    def __init__(self, event_manager):
        if not isinstance(event_manager, EventManager):
            raise TypeError('Invalid event_manager type. '
                            'EventManager required')

        self._commands = {}
        self._lock = threading.Lock()
        self._event_manager = event_manager

    def add_command(self, command):
        if not issubclass(command, AbstractCommand):
            raise TypeError('Invalid command type. '
                            'instance of AbstractCommand required')

        name = command.get_name()
        self.log.debug('add command {0}'.format(name))

        with self._lock:
            if name in self._commands:
                error_msg = 'add command error: command with name {0} ' \
                            'already registered'.format(name)
                self.log.debug(error_msg)
                raise ValueError(error_msg)
            self._commands[name] = command

    def find_command(self, argv):
        """Given an argument list, find a command and
        return the processor and any remaining arguments.
        """
        if isinstance(argv, string_types + (text_type, binary_type)):
            raise TypeError('Invalid argv type. Str or Bytes is not supported')
        if not isinstance(argv, collections.Sequence):
            raise TypeError('Invalid argv type. Is not sequence type')

        search_args = argv[:]
        name = ''
        with self._lock:
            while search_args:
                if search_args[0].startswith('-'):
                    raise ValueError('Invalid command ' + str(search_args[0]))
                next_val = search_args.pop(0)
                name = '%s %s' % (name, next_val) if name else next_val
                command = self._commands.get(name)
                if command:
                    return command, name, search_args

        raise ValueError('Unknown command {0}'.format(argv))

    def run_command(self, argv, env_stack, env_extra_layer=None):
        if isinstance(argv, string_types + (text_type, binary_type)):
            raise TypeError('Invalid argv type. Str or Bytes is not supported')
        if not isinstance(argv, collections.Sequence):
            raise TypeError('Invalid argv type. Is not sequence type')
        if not isinstance(env_stack, EnvStack):
            raise TypeError('Invalid env type. EnvStack instance required')

        argv_string = ' '.join(argv)
        self.log.info("running command '{0}'".format(argv_string))

        if env_extra_layer:
            try:
                env_stack.push(env_extra_layer)
            except TypeError as e:
                self.log.debug('push env_extra_layer error')
                raise TypeError('Invalid env extra layer. ' + str(e))

        try:
            command_factory, command_name, command_argv = \
                self.find_command(argv)
        except ValueError as e:
            self.log.error("finding command '{0}' error: {1} ({2})"
                           .format(argv_string, e, type(e).__name__))
            return self.COMMAND_NOT_FOUND_RETURN_CODE, e

        command = command_factory(
            self, self._event_manager, env_stack
        )

        return_code, error = None, None

        # pre run
        self._trigger_pre_run_command_event(command_name, argv, env_stack)
        try:
            # run
            return_code = command.run(command.get_name(), command_argv)
        except Exception as e:
            return_code, error = self.ERROR_RETURN_CODE, e
            error_msg = "running command '{0}' error: " \
                        "{1} ({2})".format(command_name, e, type(e).__name__)
            self.log.error(error_msg)
            self.log.debug(error_msg, exc_info=True)
        finally:
            # post run
            self._trigger_post_run_command_event(
                command_name, argv, return_code, error, env_stack
            )
        return return_code, error

    def __iter__(self):
        return iter(self.items())

    def items(self):
        return self._commands.items()

    def _trigger_pre_run_command_event(self, command_name, argv, env_stack):
        pre_run_event_name = 'pre-run-command'
        event_result_list = self._event_manager.trigger_event(
            pre_run_event_name, env_stack,
            {'command_name': command_name, 'command_argv': tuple(argv)}
        )
        return event_result_list

    def _trigger_post_run_command_event(self, command_name, argv,
                                        runned_command_return_code,
                                        runned_command_error, env_stack):
        post_run_event_name = 'post-run-command'
        event_result_list = self._event_manager.trigger_event(
            post_run_event_name, env_stack,
            {'command_name': command_name, 'command_argv': tuple(argv),
             'return_code': runned_command_return_code,
             'error': runned_command_error}
        )
        return event_result_list
