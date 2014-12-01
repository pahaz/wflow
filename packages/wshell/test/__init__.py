import unittest
from wshell.command_interface import AbstractCommand
from wshell.manager import CommandManager

__author__ = 'pahaz'


class BaseTestCase(unittest.TestCase):
    def mock_command_manager_cls(self):
        CM = CommandManager
        return CM

    def mock_command_manager_instance(self, cls_args=tuple()):
        CM = self.mock_command_manager_cls()
        cm = CM(*cls_args)
        return cm

    def mock_command_cls(self, name='C', docs='No'):
        def take_action(self, args):
            pass

        z = type(name, (AbstractCommand, ), {
            'take_action': take_action,
            '__doc__': docs,
        })

        return z

    def mock_command_instance(self, cls_args=(None, None),
                              cls_name='C', cls_docs='No'):
        Cmd = self.mock_command_cls(cls_name, cls_docs)
        z = Cmd(*cls_args)
        return z


from .test_command_interface import TestCommandInterface
from .test_command_manager import TestCommandManager
from .test_event_manager import TestEventManager
