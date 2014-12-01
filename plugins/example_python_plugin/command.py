# coding=utf-8
import logging
from wshell.command_interface import AbstractCommand

__author__ = 'pahaz'


class PrintEnvCommand(AbstractCommand):
    """A simple command that prints a message."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        env = self.get_env()
        for k, v in env.items():
            print(":: {0}={1} ::".format(k, v))


class ErrorCommand(AbstractCommand):
    """Always raises an error"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug("*debug* causing error")
        self.log.info("*info* causing error")
        self.log.warning("*warning* causing error")
        self.log.error("*error* causing error")
        self.log.critical("*critical* causing error")
        raise RuntimeError("this is the expected exception")
