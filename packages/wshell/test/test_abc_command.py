from __future__ import print_function, generators, division
from ..test import BaseTestCase
from ..abc_command import AbstractCommand


__author__ = 'pahaz'


class TestCommandInterface(BaseTestCase):
    def test_empty_command(self):
        class Command(AbstractCommand):
            pass

        cm = self.make_command_manager()
        em = self.make_event_manager()
        env = self.make_env()
        with self.assertRaises(TypeError) as e:
            Command(cm, em, env)

        self.assertIn("Can't instantiate abstract class", str(e.exception))

    def test_get_name(self):
        Command = self.make_command_cls('Cmd')
        self.assertEqual(Command.get_name(), 'cmd')

        Command = self.make_command_cls('CmdCommand')
        self.assertEqual(Command.get_name(), 'cmd')

    def test_override_get_name(self):
        Command = self.make_command_cls('Cmd')

        class OtherCommand(Command):
            @classmethod
            def get_name(cls):
                return 'other command'

        self.assertEqual(OtherCommand.get_name(), 'other command')

    def test_get_description(self):
        DESCRIPTION = "Some docs"
        Command = self.make_command_cls('Cmd', DESCRIPTION)
        self.assertEqual(Command.get_description(), DESCRIPTION)

    def test_get_parser(self):
        DESCRIPTION = "Some docs"
        Command = self.make_command_cls('Cmd', DESCRIPTION)
        c = self.make_command(command_cls=Command)
        z = c.get_parser("somesome.py cmd")
        self.assertEqual(z.description, DESCRIPTION)

    def test_env(self):
        ENV = self.make_env()
        c = self.make_command(env=ENV)
        self.assertEqual(ENV, c.env)
