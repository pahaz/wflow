from __future__ import unicode_literals, print_function, generators, division
import abc
import argparse
import inspect
import logging

from wutil._six import add_metaclass


@add_metaclass(abc.ABCMeta)
class AbstractCommand(object):
    """ Base class for command plugins.

    Run command logic:

        command = Command(event_manager, env)
        command_parser = command.get_parser(full_name)
        parsed_args = command_parser.parse_args(sub_argv)
        result = command.run(parsed_args)

    Example of How-to write custom command class and use it:

        class PrintEnvCommand(AbstractCommand):
            '''A simple command that prints a environments.'''
            log = logging.getLogger(__name__)

            def take_action(self, parsed_args):
                env = self.env
                for k, v in env.items():
                    print("{0}={1}\n\n".format(k, v))

        event_manager = EventManager()
        command_manager = CommandManager(event_manager)
        env = EnvStack()
        cmd = PrintEnvCommand(command_manager, event_manager, env)
        cmd.get_name() == "printenv"
        cmd.env == env
        cmd.run('wflow printenv', [])

    """
    log = logging.getLogger(__name__)

    def __init__(self, command_manager, event_manager, env):
        """
        :param command_manager: Command manager class
        :type command_manager: wshell.command_manager.CommandManager
        :param event_manager: Event manager class
        :type event_manager: wshell.event_manager.EventManager
        :param env: EnvStack class
        :type env: wutil.env.EnvStack
        """
        from wshell.command_manager import CommandManager
        from wshell.event_manager import EventManager
        from wutil.env_stack import EnvStack

        if not isinstance(command_manager, CommandManager):
            raise TypeError('Invalid command_manager type. '
                            'CommandManager required')
        if not isinstance(event_manager, EventManager):
            raise TypeError('Invalid event_manager type. '
                            'EventManager required')
        if not isinstance(env, EnvStack):
            raise TypeError('Invalid env type. EnvStack required')

        self._command_manager = command_manager
        self._event_manager = event_manager
        self._env = env


    # ABSTRACT API FOR COMMANDS

    @property
    def name(self):
        return self.get_name()

    @property
    def env(self):
        return self._env

    def run_command(self, argv):
        return_code, error = self.command_manager.run_command(argv, self.env)
        return return_code

    def trigger_event(self, event_name, env_stack, env_extra_layer=None):
        return self._event_manager.trigger_event(
            event_name, env_stack, env_extra_layer
        )

    def write_message_for_user(self, message):
        self.log.warning("----> " + message)

    # PUBLIC STATIC API FOR COMMANDS

    @classmethod
    def is_hidden_for_command_list(cls):
        """ Return True if command hided for users. Use for special command
        like git-receive-pack. (Not secured. You can use this command if want)
        """
        return False

    @classmethod
    def get_name(cls):
        """ Return the command name. Use for command executing.
        """
        name = cls.__name__.lower()
        if name.endswith('command'):
            name = name[:-7]
        return name

    @classmethod
    def get_description(cls):
        """ Return the command description.
        """
        return inspect.getdoc(cls) or ''

    # GENERAL

    def get_parser(self, run_command):
        """ Return an :class:`argparse.ArgumentParser`.

        :param run_command: Executed command string. If command run in
        interactive mode run_command == self.get_name(). If command run
        in packet mode run_command == "wflow {0}".format(self.get_name())
        if packet program name 'wflow'.

        """
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=run_command,
        )
        return parser

    def run(self, command, sub_argv):
        """ Invoked by the application when the command is run.

        Developers implementing commands should override
        :meth:`take_action`.

        """
        cmd_parser = self.get_parser(command)
        parsed_args = cmd_parser.parse_args(sub_argv)
        self.take_action(parsed_args)
        return 0

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """ Override to do something useful.
        """

    def __repr__(self):
        return "<{0} command>".format(self.name)
