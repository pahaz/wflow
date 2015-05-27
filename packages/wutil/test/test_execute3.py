import os
import subprocess
import sys
import tempfile
import unittest
from wutil.test import BaseTestCase
from wutil.execute3 import shlex_split_and_group_by_commands, \
    ExecuteCommandParseError, execute, ExecuteCommandNonZeroExitStatus, \
    ExecuteCommandPipelineNonZeroExitStatus, ExecuteCommandTimeoutExpired

__author__ = 'pahaz'
cmd, out, err, file, mode = 'cmd', 'out', 'err', 'file', 'mode'


class TestShlexSplitAndGroup(BaseTestCase):
    def test_command_without_pipeline_and_redirection(self):
        COMMAND = "echo test"
        SPITED_RESULT = [
            {cmd: ['echo', 'test'], out: None, err: None},
        ]

        result = shlex_split_and_group_by_commands(COMMAND)
        self.assertEqual(result, SPITED_RESULT)

    def test_command_with_and_condition_without_pipeline_and_redirection(self):
        COMMAND = "cd test && ls"

        with self.assertRaises(ExecuteCommandParseError):
            shlex_split_and_group_by_commands(COMMAND)

    def test_command_with_or_condition_without_pipeline_and_redirection(self):
        COMMAND = "exit || echo problem"

        with self.assertRaises(ExecuteCommandParseError):
            shlex_split_and_group_by_commands(COMMAND)

    def test_command_with_one_pipeline(self):
        self.assertEqual(
            shlex_split_and_group_by_commands("cat | python"),
            [
                {cmd: ['cat'], out: subprocess.PIPE, err: None},
                {cmd: ['python'], out: None, err: None}, ])
        self.assertEqual(
            shlex_split_and_group_by_commands("cat &| python"),
            [
                {cmd: ['cat'], out: subprocess.PIPE, err: subprocess.STDOUT},
                {cmd: ['python'], out: None, err: None}, ])

    def test_one_command(self):
        self.assertEqual(
            shlex_split_and_group_by_commands("cat"),
            [
                {cmd: ['cat'], out: None, err: None}, ])
        self.assertEqual(
            shlex_split_and_group_by_commands("cat qwer aaa"),
            [
                {cmd: ['cat', 'qwer', 'aaa'], out: None, err: None}, ])

    def test_two_pipelines(self):
        self.assertEqual(
            shlex_split_and_group_by_commands("cat | py |& hall"),
            [
                {cmd: ['cat'], out: subprocess.PIPE, err: None},
                {cmd: ['py'], out: subprocess.PIPE, err: subprocess.STDOUT},
                {cmd: ['hall'], out: None, err: None}])

    def test_stdout_redirection(self):
        self.assertEqual(
            shlex_split_and_group_by_commands("cat > aaa"),
            [
                {cmd: ['cat'], out: {file: 'aaa', mode: 'wb'}, err: None}, ])

    def test_stdout_and_stderr_redirection(self):
        self.assertEqual(
            shlex_split_and_group_by_commands("cat > aaa 2> bbb"),
            [
                {cmd: ['cat'], out: {file: 'aaa', mode: 'wb'},
                 err: {file: 'bbb', mode: 'wb'}}, ])

    def test_exception_if_redirection_then_pipeline(self):
        with self.assertRaises(ExecuteCommandParseError) as cm:
            shlex_split_and_group_by_commands("cat > aaa | qwe")

        self.assertIn("Override redirection by pipeline", str(cm.exception))

    def test_redirect_stderr_and_pipline_stdout(self):
        self.assertEqual(
            shlex_split_and_group_by_commands("cat 2> err.log | py"),
            [
                {cmd: ['cat'], err: {file: 'err.log', mode: 'wb'},
                 out: subprocess.PIPE},
                {cmd: ['py'], err: None, out: None}, ])

    def test_exception_if_redirect_stdout_and_pipline_with_stderr(self):
        with self.assertRaises(ExecuteCommandParseError) as cm:
            shlex_split_and_group_by_commands("cat > aaa |& qwe")

        self.assertIn("Override redirection by pipeline", str(cm.exception))


class ExecuteTestCase(BaseTestCase):
    def assertExecuteResult(self, result, returncode, stdout, stderr,
                            pipeline_stderr, use_strip=True):
        chars = b'' if not use_strip else b' \r\n\t'
        self.assertEqual(result.returncode, returncode)
        if stdout is not None:
            self.assertEqual(result.stdout.strip(chars), stdout)
        if stderr is not None:
            self.assertEqual(result.stderr.strip(chars), stderr)
        if pipeline_stderr is not None:
            self.assertEqual(result.pipeline_stderr.strip(chars),
                             pipeline_stderr)

    def test_execute_result(self):
        command = '''python -c "print('hi!')"'''
        z = execute(command)
        self.assertExecuteResult(z, 0, b'hi!', None, None)
        self.assertEqual(z.cmd, command)

    def test_execute_raise_non_zero_error_by_default(self):
        command = '''python -c "import sys; sys.exit(23);"'''
        with self.assertRaises(ExecuteCommandNonZeroExitStatus):
            z = execute(command)
            self.assertExecuteResult(z, 23, b'', None, None)

        z = execute(command, check_return_code_and_raise_error=False)
        self.assertExecuteResult(z, 23, b'', None, None)

    def test_set_env_variable(self):
        command = 'python -c "import sys, os; ' \
                  'os.environ.get(\'SSECRET\') == \'SSEC!\' and ' \
                  'sys.exit(24);"'
        z = execute(command)
        self.assertExecuteResult(z, 0, b'', None, None)

        command = 'python -c "import sys, os; ' \
                  'os.environ.get(\'SSECRET\') == \'SSEC!\' or ' \
                  'sys.exit(24);"'
        z = execute(command, env=self.make_python_env({'SSECRET': 'SSEC!'}))
        self.assertExecuteResult(z, 0, b'', None, None)

    def test_set_env_variable2(self):
        env_name = 'AKAWKFN'
        command = self.make_print_env_variable_command(env_name)
        z = execute(command)
        self.assertExecuteResult(z, 0, b'None', None, None)

        z = execute(command, env=self.make_python_env({env_name: "SEC!"}))
        self.assertExecuteResult(z, 0, b'SEC!', None, None)

    def test_security_execute_with_shell_false(self):
        command = '"{0}" -c "import sys; ' \
                  'print(\\\"SSS! $SSS %SSS%\\\")"' \
            .format(self.get_python_command_path())
        z = execute(command)
        self.assertExecuteResult(z, 0, b'SSS! $SSS %SSS%', None, None)

    def test_insecurity_execute_with_shell_true(self):
        command = '"{0}" -c "import sys; ' \
                  'print(\\\"SSS! $SSS %SSS%\\\")"' \
            .format(self.get_python_command_path())
        z = execute(command, env=self.make_python_env({"SSS": "+"}),
                    shell=True)

        self.assertEqual(z.returncode, 0)
        self.assertNotEqual(z.stdout, b'SSS! $SSS %SSS%')

    def test_timeout(self):
        command = 'python -c "import time; time.sleep(0.5);"'
        with self.assertRaises(ExecuteCommandTimeoutExpired):
            execute(command, timeout=0.2)

    # def test_execute_init_env_script(self):
    # with self.assertRaises(InitEnvScriptError):
    # _execute_init_env_script('kawbgajwbgkabg')
    #
    # with tempfile.TemporaryDirectory() as tmpdirname:
    #         self.assertTrue(os.path.exists(tmpdirname))
    #         os.system('virtualenv {0}'.format(tmpdirname))
    #
    #         if sys.platform == 'win32':
    #             path = os.path.join(tmpdirname, 'Scripts', 'activate')
    #         else:
    #             path = os.path.join(tmpdirname, 'bin', 'activate')
    #         env = _execute_init_env_script(path)
    #
    #     self.assertEqual(env['VIRTUAL_ENV'], tmpdirname)

    def make_python_env(self, extra=None):
        # required for starting python on windows
        env = {'SYSTEMROOT': os.environ.get('SYSTEMROOT', '')}
        if extra:
            env.update(extra)
        return env

    def make_print_env_variable_command(self, env_name):
        return '''python -c "import os; print(os.environ.get('{0}'))"''' \
            .format(env_name)

    def get_python_command_path(self):
        return sys.executable


class ExecuteWithShellTestCase(unittest.TestCase):
    def test_cd(self):
        ECHO_CWD_COMMAND = 'python -c "import os; print(os.getcwd())"'
        tmp = tempfile.gettempdir()
        COMMAND = 'cd "{0}" && {1}'.format(tmp, ECHO_CWD_COMMAND)

        r = execute(COMMAND, shell=True)
        self.assertEqual(r.stdout_text.strip(), tmp)

    def test_cd_without_shell(self):
        ECHO_CWD_COMMAND = 'python -c "import os; print(os.getcwd())"'
        tmp = tempfile.gettempdir()
        COMMAND = 'cd "{0}" && {1}'.format(tmp, ECHO_CWD_COMMAND)

        with self.assertRaises(ExecuteCommandParseError):
            execute(COMMAND)

    def test_exit_1_or_echo_1(self):
        EXIT_1_COMMAND = 'python -c "import sys; sys.exit(1)"'
        ECHO_1_COMMAND = 'python -c "print(1)"'
        COMMAND = "{0} || {1}".format(EXIT_1_COMMAND, ECHO_1_COMMAND)

        with self.assertRaises(ExecuteCommandParseError):
            execute(COMMAND)

        r = execute(COMMAND, shell=True)
        self.assertEqual(r.stdout_text.strip(), "1")
