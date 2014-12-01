# coding=utf-8
from . import command


__author__ = 'pahaz'


def load(manager):
    manager.add_command(command.GitReceivePackCommand)
    manager.add_command(command.GitUploadPackCommand)
    # manager.add_event_listener('example', event.simple_event_listener)
