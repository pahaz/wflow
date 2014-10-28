# coding=utf-8
from . import command1

__author__ = 'pahaz'


def load(manager):
    manager.add_command('simple1', command1.Simple)
    manager.add_command('simple2', command1.Error)
