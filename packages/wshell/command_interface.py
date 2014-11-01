import abc
import argparse
import inspect

import six


@six.add_metaclass(abc.ABCMeta)
class Command(object):
    """Base class for command plugins.

    :param app: Application instance invoking the command.
    :paramtype app: cliff.app.App
    """
    def __init__(self, app, app_args):
        self.app = app
        self.app_args = app_args
        return

    @classmethod
    def get_name(cls):
        """Return the command name. Use for command executing.
        """
        name = cls.__name__.lower()
        if name.endswith('command'):
            name = name[:-7]
        return name

    def get_description(self):
        """Return the command description.
        """
        return inspect.getdoc(self.__class__) or ''

    def get_parser(self, full_command_name):
        """Return an :class:`argparse.ArgumentParser`.
        :param full_command_name: full command name
        """
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=full_command_name,
        )
        return parser

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Override to do something useful.
        """

    # TODO: add hook interface!

    def run(self, parsed_args):
        """Invoked by the application when the command is run.

        Developers implementing commands should override
        :meth:`take_action`.

        Developers creating new command base classes (such as
        :class:`Lister` and :class:`ShowOne`) should override this
        method to wrap :meth:`take_action`.
        """
        self.take_action(parsed_args)
        return 0
