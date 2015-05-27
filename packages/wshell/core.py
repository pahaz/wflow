from __future__ import unicode_literals, print_function, generators, division
import argparse
import os
import random
import shlex
import logging
import string
import sys
import time

from .interactive import InteractiveMode
from .command.complete import CompleteCommand
from .command.help import HelpCommand, HelpAction
from wshell.module import load_managers_from_plugins
from wutil.env_keys import PLATFORM_PLUGINS_PATH_KEY, PLATFORM_VENV_PATH_KEY, \
    PLATFORM_USERNAME_KEY
from wutil.env_keys import PLATFORM_DATA_PATH_KEY
from wutil.env_stack import load_env_stack
from wshell.event_manager import EventManager
from wshell.command_manager import CommandManager
from wutil.fs import read_content

__author__ = 'pahaz'


class Core(object):
    """ Core class.
    """
    INITIALIZE_ERROR_RETURN_CODE = 3

    LOG__CONSOLE_LOG_LEVEL = 0
    LOG__CONSOLE_MESSAGE_FORMAT = '%(message)s'

    LOG__LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'

    NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    DESCRIPTION = "Core class"
    VERSION = "0.0"

    log = logging.getLogger(NAME)
    LOG_LEVELS = {
        -1: logging.ERROR,
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }

    def __init__(self, config_file):
        """
        :param command_manager: Command manager class
        :type command_manager: wshell.command_manager.CommandManager
        :param event_manager: Event manager class
        :type event_manager: wshell.event_manager.EventManager
        :param env: EnvStack class
        :type env: wutil.env.EnvStack
        """

        session_id = _make_log_session_id()
        self.log_file = log_file = "/tmp/{0}.log".format(session_id)

        self.configure_logging(log_file)

        self.log.warning('::: SESSION {0} :::'.format(session_id))

        env = load_env_stack(config_file)
        platform_plugins_path = env[PLATFORM_PLUGINS_PATH_KEY]
        platform_data_path = env[PLATFORM_DATA_PATH_KEY]
        platform_venv_path = env[PLATFORM_VENV_PATH_KEY]
        platform_username = env[PLATFORM_USERNAME_KEY]

        event_manager = EventManager()
        command_manager = CommandManager(event_manager)

        load_managers_from_plugins(
            platform_plugins_path,
            platform_venv_path,
            command_manager,
            event_manager,
            env
        )

        self.command_manager = command_manager
        self.command_manager.add_command(HelpCommand)
        self.command_manager.add_command(CompleteCommand)

        self.event_manager = event_manager

        self.env = env

        self.parser = self.build_option_parser()
        self._login_shell_command_support_fix_parser()
        self.interactive_mode = False

    def build_option_parser(self, argparse_kwargs=None):
        description, version = self.DESCRIPTION, self.VERSION
        argparse_kwargs = argparse_kwargs or {}
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            **argparse_kwargs
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
        )
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="show this help message and exit",
        )
        return parser

    def configure_logging(self, log_file):
        """ Create logging handlers for any log output.
        """
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        # Set up logging to a file
        if log_file:
            file_handler = logging.FileHandler(filename=log_file)
            formatter = logging.Formatter(self.LOG__LOG_FILE_MESSAGE_FORMAT)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Always send higher-level messages to the console via stderr
        console = logging.StreamHandler()
        console_level = self.LOG_LEVELS.get(self.LOG__CONSOLE_LOG_LEVEL)
        console.setLevel(console_level)
        formatter = logging.Formatter(self.LOG__CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)

    def run(self, argv):
        """ Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        self._collect_debug_info()
        try:
            self.options, remainder = self.parser.parse_known_args(argv)
            self._login_shell_command_support_fix_run_argv(remainder)
            self.interactive_mode = not remainder
            self.initialize(remainder)
        except (Exception, KeyboardInterrupt) as err:
            self.log.error(err)
            self.log.debug(err, exc_info=True)
            return self.INITIALIZE_ERROR_RETURN_CODE

        try:
            retcode = self.run_interactive_mode() if self.interactive_mode \
                else self.run_command(remainder)
        except KeyboardInterrupt:
            self.log.error("INTERRUPTED!")
            raise
        finally:
            self._debug_info()
        return retcode

    def run_interactive_mode(self):
        interactive_mode = InteractiveMode(
            '(%s) ' % self.NAME,
            self.command_manager,
            self.env,
        )

        interactive_mode.cmdloop()
        return 0

    def run_command(self, argv):
        # self.pre_run_command(argv)
        return_code, error = self.command_manager.run_command(argv, self.env)
        # self.post_run_command(argv, return_code, error)
        return return_code

    def initialize(self, argv):
        self.log.debug('initialize `{0}`'.format(' '.join(argv)))

    # def pre_run_command(self, argv):
    # self.log.debug('pre_run_command `{0}`'.format(' '.join(argv)))
    #
    # def post_run_command(self, argv, command_return_code, command_error):
    #     self.log.debug('post_run_command `{0}`'.format(' '.join(argv)))

    def _debug_info(self):
        self.log.debug("write user debug info")
        if self._debug_info_deploy_app_name:
            # echo "127.0.0.1" > "$PLATFORM_DATA_PATH/$APP/HOST"
            # echo "$PORT" > "$PLATFORM_DATA_PATH/$APP/PORT"
            # echo "$hostname" > "$PLATFORM_DATA_PATH/$APP/HOSTNAME"
            app_path = os.path.join(self.env[PLATFORM_DATA_PATH_KEY],
                               self._debug_info_deploy_app_name)
            PORT = read_content(os.path.join(app_path, "PORT"))
            HOST = read_content(os.path.join(app_path, "HOST"))
            HOSTNAME = read_content(os.path.join(app_path, "HOSTNAME"))
            extra_info = """
        TEST DEPLOY RESULT FOR {0}
         - curl -H 'Host: {hn}' http://localhost:80/
         - curl http://{h}:{p}/

            """.format(self._debug_info_deploy_app_name, p=PORT, h=HOST,
                       hn=HOSTNAME)
        else:
            extra_info = ''

        self.log.warning("""

        HI, IF YOU WANT SEE MORE DEBUG INFORMATION SEE LOG FILE: {0}
         - tail {0}
         - tail -n 50 {0}
         - cat {0}
        \n""".format(self.log_file) + extra_info)

    def _login_shell_command_support_fix_parser(self):
        # -c uses for login shell
        self.parser.add_argument(
            '-c', '--command',
            nargs='?',
            action='store',
            dest='command',
            help="Run command and exit. (deprecated) "
                 "Used for login shell command execution."
        )

    def _login_shell_command_support_fix_run_argv(self, argv):
        # if -c or --command
        if self.options.command:
            command = shlex.split(self.options.command)
            argv[:] = command + argv

    def _collect_debug_info(self):
        self._debug_info_deploy_app_name = None

        def _collect_app_name_for_core_debug_info(manager, env):
            self._debug_info_deploy_app_name = env['APP']

        self.event_manager.add_event_listener(
            'deploy', _collect_app_name_for_core_debug_info
        )


def _make_log_session_id():
    chars = string.ascii_uppercase + string.digits
    rnd = ''.join([random.choice(chars) for _ in range(4)])
    timestamp = time.strftime("%Y%m%d%HH%MM%SS")
    session_id = "W{0}{1}".format(timestamp, rnd)
    return session_id
