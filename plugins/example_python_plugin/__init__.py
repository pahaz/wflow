# coding=utf-8
from . import command
from . import event

__author__ = 'pahaz'


def load(manager):
    manager.add_command(command.PrintEnvCommand)
    manager.add_command(command.ErrorCommand)
    manager.add_event_listener('example', event.simple_event_listener)
