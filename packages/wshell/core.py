import argparse
from cliff.app import App

from .interactive import InteractiveMode
from .command.complete import CompleteCommand
from .command.help import HelpCommand, HelpAction

__author__ = 'pahaz'


class Core(App):
    """
    Core class is the manager interface.
    """
    CONSOLE_MESSAGE_FORMAT = '%(name)s: %(message)s'
    LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'

    log = App.LOG

    def __init__(self, manager,
                 copyright='', description='', version='0.0',
                 stdin=None, stdout=None, stderr=None,
                 interactive_app_factory=InteractiveMode):
        self.copyright = copyright
        self.description = description
        self.version = version
        self._set_streams(stdin, stdout, stderr)
        self.command_manager = manager
        self.command_manager.add_command(HelpCommand)
        self.command_manager.add_command(CompleteCommand)
        self.event_manager = manager
        self.env = manager.get_environ()
        self.interactive_app_factory = interactive_app_factory
        self.parser = self.build_option_parser(description, version)
        self.interactive_mode = False
        self.interpreter = None

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
            default=self.DEFAULT_VERBOSE_LEVEL,
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
            const=0,
            help='suppress output except warnings and errors',
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
            action='store_true',
            dest='is_command_option_used',
            help="Run command and exit. (deprecated) "
                 "Used for login shell command execution."
        )
        return parser

    def initialize_app(self, argv):
        pass

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command `{0}`'.format(cmd.get_name()))

        name = cmd.get_name()
        event_name = 'pre-' + name
        rez = self.event_manager.trigger_event(event_name, cmd=cmd,
                                               env=self.env)
        if rez:
            self.log.debug('event `{1}` results: {0}'.format(rez, event_name))

    def clean_up(self, cmd, result, error):
        self.log.debug('clean_up `{0}`'.format(cmd.get_name()))
        if error:
            self.log.debug('got an error: {0}'.format(error))

        name = cmd.get_name()
        event_name = 'post-' + name
        rez = self.event_manager.trigger_event(event_name, cmd=cmd,
                                               result=result, error=error,
                                               env=self.env)
        if rez:
            self.log.debug('event {1} results: {0}'.format(rez, event_name))
