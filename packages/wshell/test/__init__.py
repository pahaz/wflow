from __future__ import unicode_literals, print_function, generators, division
import unittest

from wshell.abc_command import AbstractCommand
from wshell.command_manager import CommandManager
from wshell.event_manager import EventManager
from wutil.env_stack import EnvStack


__author__ = 'pahaz'


class BaseTestCase(unittest.TestCase):
    def make_command_cls(self, name='C', docs='No', take_action=None):
        def empty_action(self, args):
            pass

        z = type(name, (AbstractCommand, ), {
            'take_action': take_action if take_action else empty_action,
            '__doc__': docs,
        })

        return z

    def make_command(self,
                     event_manager=None,
                     command_manager=None,
                     env=None,
                     command_cls=None):
        if not command_cls:
            command_cls = self.make_command_cls()
        if not event_manager:
            event_manager = self.make_event_manager()
        if not command_manager:
            command_manager = self.make_command_manager()
        if not env:
            env = self.make_env()
        z = command_cls(command_manager, event_manager, env)
        return z

    def make_event_manager(self):
        return EventManager()

    def make_command_manager(self, event_manager=None):
        if not event_manager:
            event_manager = self.make_event_manager()
        return CommandManager(event_manager)

    def make_env(self, init=None):
        return EnvStack(init)
