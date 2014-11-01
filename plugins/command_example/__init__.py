# coding=utf-8
from . import command1

__author__ = 'pahaz'


def event_listener(**kwargs):
    print("Woow simple-event EVENT!!")


def load(manager):
    manager.add_command(command1.SimpleCommand)
    manager.add_command(command1.ErrorCommand)
    manager.add_event_listener('simple-event', event_listener)
