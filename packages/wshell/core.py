import argparse
import os
import shlex
import logging
import sys

from .interactive import InteractiveMode
from .command.complete import CompleteCommand
from .command.help import HelpCommand, HelpAction


__author__ = 'pahaz'


class Core(object):
    """
    Core class is the manager interface.
    """
    _RUN_SUBCOMMAND__ERROR_RETURN_CODE = 1
    _RUN_SUBCOMMAND__COMMAND_NOT_FOUND_RETURN_CODE = 2
    _RUN__INITIALIZE_ERROR_RETURN_CODE = 3

    LOG__DEFAULT_LOG_LEVEL = 0
    LOG__CONSOLE_MESSAGE_FORMAT = '%(message)s'
    LOG__LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'

    NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    LOG = logging.getLogger(NAME)
    LOG_LEVELS = {
        -1: logging.ERROR,
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }

    def __init__(self,
                 manager,
                 copyright='', description='', version='0.0',
                 interactive_app_factory=InteractiveMode):
        self.copyright = copyright
        self.description = description
        self.version = version

        self.command_manager = manager
        self.command_manager.add_command(HelpCommand)
        self.command_manager.add_command(CompleteCommand)
        self.event_manager = manager
        self.env = manager.get_env()

        self.interactive_app_factory = interactive_app_factory
        self.parser = self.build_option_parser(description, version)
        self.interactive_mode = False
        self.interactive_app = None

    def build_option_parser(self, description, version, argparse_kwargs=None):
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
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.LOG__DEFAULT_LOG_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=-1,
            help='suppress output except errors',
        )
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="show this help message and exit",
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='show tracebacks on errors',
        )

        # -c uses for login shell
        parser.add_argument(
            '-c', '--command',
            nargs='?',
            action='store',
            dest='command',
            help="Run command and exit. (deprecated) "
                 "Used for login shell command execution."
        )
        return parser

    def configure_logging(self):
        """Create logging handlers for any log output.
        """
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        # Set up logging to a file
        if self.options.log_file:
            file_handler = logging.FileHandler(
                filename=self.options.log_file,
            )
            formatter = logging.Formatter(self.LOG__LOG_FILE_MESSAGE_FORMAT)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Always send higher-level messages to the console via stderr
        console = logging.StreamHandler()
        console_level = self.LOG_LEVELS.get(self.options.verbose_level,
                                            logging.DEBUG)
        console.setLevel(console_level)
        formatter = logging.Formatter(self.LOG__CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)

    def _login_shell_command_argv_support(self, argv):
        # if -c or --command
        if self.options.command:
            command = shlex.split(self.options.command)
            argv[:] = command + argv

    def run(self, argv):
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            self.options, remainder = self.parser.parse_known_args(argv)
            self.configure_logging()
            self._login_shell_command_argv_support(remainder)
            self.interactive_mode = not remainder
            self.initialize(remainder)
        except Exception as err:
            if hasattr(self, 'options'):
                debug = self.options.debug
            else:
                debug = True
            if debug:
                self.LOG.exception(err)
                raise
            else:
                self.LOG.error(err)
            return self._RUN__INITIALIZE_ERROR_RETURN_CODE

        return self.run_interactive_mode() if self.interactive_mode else \
            self.run_command(remainder)

    def run_interactive_mode(self):
        self.interactive_app = self.interactive_app_factory(
            self,
            self.command_manager)
        self.interactive_app.cmdloop()
        return 0

    def run_command(self, argv):
        try:
            command_factory, command_name, command_argv = \
                self.command_manager.find_command(argv)
        except ValueError as e:
            if self.options.debug:
                self.LOG.exception(e)
            else:
                self.LOG.error(e)
            return self._RUN_SUBCOMMAND__COMMAND_NOT_FOUND_RETURN_CODE

        command = command_factory(self, self.options)

        result = self._RUN_SUBCOMMAND__ERROR_RETURN_CODE
        error = None
        try:
            # pre run
            self.LOG.debug('pre_run_command `{0}`'
                           .format(command_name))
            self.pre_run_command(command)

            # trigger event
            pre_run_event_name = 'pre-' + command_name
            self.LOG.debug('trigger_event `{0}`'.format(pre_run_event_name))
            event_result_list = self.event_manager.trigger_event(
                pre_run_event_name,
                command=command,
                env=self.env)
            if event_result_list:
                self.LOG.debug('event `{1}` results: {0}'
                               .format(event_result_list, pre_run_event_name))

            # run
            run_command_full_name = (command_name
                                     if self.interactive_mode
                                     else ' '.join([self.NAME, command_name]))
            result = command.run(run_command_full_name, command_argv)
        except Exception as e:
            error = e  # use in finally
            msg = "Caught exception: {0}".format(e)
            if self.options.debug:
                self.LOG.exception(msg)
            else:
                self.LOG.error(msg)

            self.LOG.debug('Debug error: {0}'.format(error), exc_info=True)
        finally:
            try:
                # post run
                self.LOG.debug('post_run_command `{0}`'.format(command_name))
                self.post_run_command(command, result, error)

                # trigger event
                name = command.get_name()
                event_name = 'post-' + name
                self.LOG.debug('trigger_event `{0}`'.format(event_name))
                event_result_list = self.event_manager.trigger_event(
                    event_name,
                    command=command,
                    result=result,
                    error=error,
                    env=self.env)
                if event_result_list:
                    self.LOG.debug('event `{1}` results: {0}'
                                   .format(event_result_list, event_name))

            except Exception as e:
                msg = "Could not clean up: {0}".format(e)
                if self.options.debug:
                    self.LOG.exception(msg)
                else:
                    self.LOG.error(msg)

                self.LOG.debug('Debug error: {0}'.format(error), exc_info=True)
        return result

    def initialize(self, argv):
        pass

    def pre_run_command(self, command):
        pass

    def post_run_command(self, command, result, error):
        pass
