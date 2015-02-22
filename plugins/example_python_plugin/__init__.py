# coding=utf-8
from . import command
from . import event

__author__ = 'pahaz'


def load(command_manager, event_manager, env):
    command_manager.add_command(command.PrintEnvCommand)
    command_manager.add_command(command.ErrorCommand)
    event_manager.add_event_listener('example', event.simple_event_listener)
