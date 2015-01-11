import abc
import argparse
import inspect

import six


@six.add_metaclass(abc.ABCMeta)
class AbstractCommand(object):
    """Base class for command plugins.

    :param app: Application instance invoking the command.
    :paramtype app: cliff.app.App

    Run command logic:

            command = Command(app, app.options)
            command_parser = command.get_parser(full_name)
            parsed_args = command_parser.parse_args(sub_argv)
            result = command.run(parsed_args)

    """

    def __init__(self, app, app_parsed_options):
        self.app = app
        self.app_args = app_parsed_options

    @classmethod
    def is_hidden_for_command_list(cls):
        """Return True if command hided for users. Use for special command like
        git-receive-pack. (Not secured. You can use this command if want)
        """
        return False

    @classmethod
    def get_name(cls):
        """Return the command name. Use for command executing.
        """
        name = cls.__name__.lower()
        if name.endswith('command'):
            name = name[:-7]
        return name

    @classmethod
    def get_description(cls):
        """Return the command description.
        """
        return inspect.getdoc(cls) or ''

    def get_env(self):
        return self.app.env

    def trigger_event(self, event_name, **kwargs):
        if 'env' in kwargs:
            raise TypeError('You can`t override env')
        if 'cmd' in kwargs:
            raise TypeError('You con`t override cmd')

        cmd = self.get_name()
        env = self.get_env()
        return self.app.event_manager.trigger_event(event_name,
                                                    cmd=cmd,
                                                    env=env,
                                                    **kwargs)

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Override to do something useful.
        """

    def run(self, run_command, sub_argv):
        """Invoked by the application when the command is run.

        Developers implementing commands should override
        :meth:`take_action`.

        """
        cmd_parser = self.get_parser(run_command)
        parsed_args = cmd_parser.parse_args(sub_argv)
        self.take_action(parsed_args)
        return 0

    def get_parser(self, run_command):
        """Return an :class:`argparse.ArgumentParser`.

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

