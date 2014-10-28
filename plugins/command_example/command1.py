# coding=utf-8
import logging
from wshell.command import Command

__author__ = 'pahaz'


class Simple(Command):
    """A simple command that prints a message."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        self.app.stdout.write('hi!\n')


class Error(Command):
    """Always raises an error"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('causing error')
        raise RuntimeError('this is the expected exception')

