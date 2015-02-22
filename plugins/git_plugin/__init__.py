# coding=utf-8
from . import command


__author__ = 'pahaz'


def load(command_manager, event_manager, env):
    command_manager.add_command(command.GitReceivePackCommand)
    command_manager.add_command(command.GitUploadPackCommand)
    # event_manager.add_event_listener('example', event.simple_event_listener)
