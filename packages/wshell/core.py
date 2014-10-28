from cliff.app import App

from .interactive import InteractiveMode
from .manager import CommandManager

__author__ = 'pahaz'


class Core(App):
    """
    Core class for build custom shell.
    """
    CONSOLE_MESSAGE_FORMAT = '%(name)s: %(message)s'
    LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'

    log = App.LOG

    def __init__(self, plugin_root_dir,
                 copyright='',
                 description='',
                 version=''):
        self.copyright = copyright
        super(Core, self).__init__(
            description=description,
            version=version,
            command_manager=CommandManager(plugin_root_dir),
            interactive_app_factory=InteractiveMode
        )

    def build_option_parser(self, description, version, argparse_kwargs=None):
        argparse_kwargs = argparse_kwargs or {}
        parser = super(Core, self).build_option_parser(
            description,
            version,
            argparse_kwargs)
        # -c uses for login shell
        parser.add_argument(
            '-c', '--command',
            action='store_true',
            dest='is_command_option_used',
            help="Run command and exit. (Deprecated)"
        )
        return parser

    def initialize_app(self, argv):
        pass

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)
