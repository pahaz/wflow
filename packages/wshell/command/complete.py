import logging
from cliff.complete import CompleteDictionary
import stevedore
from ..command_interface import Command

__author__ = 'pahaz'


class CompleteCommand(Command):
    """print bash completion command
    """

    log = logging.getLogger(__name__ + '.CompleteCommand')

    def __init__(self, app, app_args):
        super(CompleteCommand, self).__init__(app, app_args)
        self._formatters = stevedore.ExtensionManager(
            namespace='cliff.formatter.completion',
        )

    def get_parser(self, full_command_name):
        parser = super(CompleteCommand, self).get_parser(full_command_name)
        parser.add_argument(
            "--name",
            default=None,
            metavar='<command_name>',
            help="Command name to support with command completion"
        )
        parser.add_argument(
            "--shell",
            default='bash',
            metavar='<shell>',
            choices=sorted(self._formatters.names()),
            help="Shell being used. Use none for data only (default: bash)"
        )
        return parser

    def get_actions(self, command):
        the_cmd = self.app.command_manager.find_command(command)
        cmd_factory, cmd_name, search_args = the_cmd
        cmd = cmd_factory(self.app, search_args)
        if self.app.interactive_mode:
            full_name = (cmd_name)
        else:
            full_name = (' '.join([self.app.NAME, cmd_name]))
        cmd_parser = cmd.get_parser(full_name)
        return cmd_parser._get_optional_actions()

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        name = parsed_args.name or self.app.NAME
        try:
            shell_factory = self._formatters[parsed_args.shell].plugin
        except KeyError:
            raise RuntimeError('Unknown shell syntax %r' % parsed_args.shell)
        shell = shell_factory(name, self.app.stdout)

        dicto = CompleteDictionary()
        for cmd in self.app.command_manager:
            command = cmd[0].split()
            dicto.add_command(command, self.get_actions(command))

        shell.write(dicto.get_commands(), dicto.get_data())

        return 0
