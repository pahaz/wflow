"""
Copied form cliff with come changes.
Bash completion for the CLI.
"""
from __future__ import unicode_literals, print_function, generators, division
import sys
import logging

from wutil._six import string_types
from ..abc_command import AbstractCommand


class CompleteDictionary:
    """dictionary for bash completion
    """

    def __init__(self):
        self._dictionary = {}

    def add_command(self, command, actions):
        optstr = ' '.join(opt for action in actions
                          for opt in action.option_strings)
        dicto = self._dictionary
        for subcmd in command[:-1]:
            dicto = dicto.setdefault(subcmd, {})
        dicto[command[-1]] = optstr

    def get_commands(self):
        return ' '.join(k for k in sorted(self._dictionary.keys()))

    def _get_data_recurse(self, dictionary, path):
        ray = []
        keys = sorted(dictionary.keys())
        for cmd in keys:
            name = path + "_" + cmd if path else cmd
            value = dictionary[cmd]
            if isinstance(value, string_types):
                ray.append((name, value))
            else:
                cmdlist = ' '.join(sorted(value.keys()))
                ray.append((name, cmdlist))
                ray += self._get_data_recurse(value, name)
        return ray

    def get_data(self):
        return sorted(self._get_data_recurse(self._dictionary, ""))


class CompleteShellBase(object):
    """base class for bash completion generation
    """

    def __init__(self, name, output):
        self.name = str(name)
        self.output = output

    def write(self, cmdo, data):
        self.output.write(self.get_header())
        self.output.write("  cmds='{0}'\n".format(cmdo))
        for datum in data:
            self.output.write('  cmds_{0}=\'{1}\'\n'.format(*datum))
        self.output.write(self.get_trailer())


class CompleteNoCode(CompleteShellBase):
    """completion with no code
    """

    def __init__(self, name, output):
        super(CompleteNoCode, self).__init__(name, output)

    def get_header(self):
        return ''

    def get_trailer(self):
        return ''


class CompleteBash(CompleteShellBase):
    """completion for bash
    """

    def __init__(self, name, output):
        super(CompleteBash, self).__init__(name, output)

    def get_header(self):
        return ('_' + self.name + """()
{
  local cur prev words
  COMPREPLY=()
  _get_comp_words_by_ref -n : cur prev words

  # Command data:
""")

    def get_trailer(self):
        return ("""
  cmd=""
  words[0]=""
  completed="${cmds}"
  for var in "${words[@]:1}"
  do
    if [[ ${var} == -* ]] ; then
      break
    fi
    if [ -z "${cmd}" ] ; then
      proposed="${var}"
    else
      proposed="${cmd}_${var}"
    fi
    local i="cmds_${proposed}"
    local comp="${!i}"
    if [ -z "${comp}" ] ; then
      break
    fi
    if [[ ${comp} == -* ]] ; then
      if [[ ${cur} != -* ]] ; then
        completed=""
        break
      fi
    fi
    cmd="${proposed}"
    completed="${comp}"
  done

  if [ -z "${completed}" ] ; then
    COMPREPLY=( $( compgen -f -- "$cur" ) $( compgen -d -- "$cur" ) )
  else
    COMPREPLY=( $(compgen -W "${completed}" -- ${cur}) )
  fi
  return 0
}
complete -F _""" + self.name + ' ' + self.name + '\n')


class CompleteCommand(AbstractCommand):
    """print bash completion command
    """

    log = logging.getLogger(__name__)
    _run_command = "default complete"

    def get_parser(self, run_command):
        parser = super(CompleteCommand, self).get_parser(run_command)
        parser.add_argument(
            "--name",
            default=None,
            metavar='<command_name>',
            help="Command name to support with command completion"
        )
        return parser

    def get_actions(self, command):
        the_cmd = self._command_manager.find_command(command)
        cmd_factory, cmd_name, search_args = the_cmd
        cmd = cmd_factory(self._event_manager,
                          self._command_manager,
                          self._env)
        cmd_parser = cmd.get_parser(self._run_command)
        return cmd_parser._get_optional_actions()

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        name = parsed_args.name or self._run_command

        shell = CompleteBash(name, sys.stdout)

        dicto = CompleteDictionary()
        for cmd in self._command_manager:
            if not cmd.is_hidden_for_command_list():
                command = cmd[0].split()
                dicto.add_command(command, self.get_actions(command))

        shell.write(dicto.get_commands(), dicto.get_data())

        return 0

    def run(self, command, sub_argv):
        self._run_command = command
        return super(CompleteCommand, self).run(command, sub_argv)
