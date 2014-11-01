import unittest
from wshell.command_interface import Command
from wshell.test import BaseTestCase


__author__ = 'pahaz'


class TestCommandInterface(BaseTestCase):
    def test_empty_command(self):
        class Cmd(Command):
            pass

        with self.assertRaises(TypeError) as cm:
            c = Cmd(None, None)

        # print(dir(cm.exception), cm.exception.args)
        self.assertIn("Can't instantiate abstract class", str(cm.exception))

    def test_get_name(self):
        Cmd = self.mock_command_cls('Cmd')
        self.assertEqual(Cmd.get_name(), 'cmd')
        Cmd = self.mock_command_cls('CmdCommand')
        self.assertEqual(Cmd.get_name(), 'cmd')
        c = Cmd(None, None)
        self.assertEqual(c.get_name(), 'cmd')
        
        class SuperCmd(Cmd):
            @classmethod
            def get_name(cls):
                return 'su cmd'

        self.assertEqual(SuperCmd.get_name(), 'su cmd')
        c = SuperCmd(None, None)
        self.assertEqual(c.get_name(), 'su cmd')

    def test_get_description(self):
        docs = "Some docs"
        Cmd = self.mock_command_cls('Cmd', docs)
        c = Cmd(None, None)
        self.assertEqual(c.get_description(), docs)

    def test_get_parser(self):
        docs = "Some docs"
        Cmd = self.mock_command_cls('Cmd', docs)
        c = Cmd(None, None)

        z = c.get_parser("somesome.py cmd")
        self.assertEquals(z.description, docs)

if __name__ == "__main__":
    unittest.main()