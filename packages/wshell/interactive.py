import shlex
import sys
import itertools
from cmd import Cmd

__author__ = 'pahaz'


class InteractiveMode(Cmd):
    """
    Core class for shell interactive mode.
    """
    use_rawinput = True
    doc_header = "Shell commands (type help <topic>):"
    app_cmd_header = "Application commands (type help <topic>):"
    exclude_commands = ['complete', 'help']

    def __init__(self, app_core, command_manager, stdin=None, stdout=None):
        self.app_core = app_core
        self.prompt = '(%s) ' % app_core.NAME
        self.command_manager = command_manager
        super(InteractiveMode, self).__init__('tab', stdin, stdout)

    def cmdloop(self, intro=None):
        super(InteractiveMode, self).cmdloop(intro)

    def emptyline(self):
        pass

    def default(self, line):
        # Tie in the default command processor to
        # dispatch commands known to the command manager.
        # We send the message through our parent app,
        # since it already has the logic for executing
        # the subcommand.
        line_parts = shlex.split(line)
        self.app_core.run_command(line_parts)

    def complete(self, text, state):
        return super(InteractiveMode, self).complete(text, state)

    def completenames(self, text, *ignored):
        names_base = super(InteractiveMode, self).completenames(text, *ignored)
        if not text:
            names_app = [
                n for n, v in self.command_manager
                if n not in self.exclude_commands and
                not v.is_hidden_for_command_list()
            ]
        else:
            names_app = [
                n for n, v in self.command_manager
                if n not in self.exclude_commands and
                not v.is_hidden_for_command_list() and
                n.startswith(text)
            ]

        return sorted(names_app + names_base)

    def do_help(self, line):
        """
        List available commands with "help" or detailed help with "help cmd".
        """
        if line:
            # Check if the arg is a builtin command or something
            # coming from the command manager
            arg_parts = shlex.split(line)
            method_name = '_'.join(
                itertools.chain(
                    ['do'],
                    itertools.takewhile(
                        lambda x: not x.startswith('-'),
                        arg_parts
                    )
                )
            )
            # Have the command manager version of the help
            # command produce the help text since cmd and
            # cmd2 do not provide help for "help"
            if hasattr(self, method_name):
                return super(InteractiveMode, self).do_help(method_name[3:])
            # Dispatch to the underlying help command,
            # which knows how to provide help for extension
            # commands.
            self.default('help ' + line)
        else:
            super(InteractiveMode, self).do_help(line)
            cmd_names = sorted([n for n, v in self.command_manager
                                if n not in self.exclude_commands
                                and not v.is_hidden_for_command_list()])
            self.print_topics(self.app_cmd_header, cmd_names, 15, 80)
        return

    def do_EOF(self, line):
        """exit"""
        sys.exit()

    do_q = do_quit = do_exit = do_EOF
