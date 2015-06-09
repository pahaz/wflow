import os
import tempfile
import unittest
import sys
import subprocess

from wutil.execute import simple_execute, \
    execute, ReturnCodeError, _execute_init_env_script, InitEnvScriptError
from wutil.test import BaseTestCase


__author__ = 'pahaz'


def _make_print_environ_cmd(env_name):
    return '''python -c "import os; print(os.environ.get('{0}'))"''' \
        .format(env_name)


# @unittest.skip("long time test!")
class TestExecuteFunctions(BaseTestCase):
    def test_execute_return_code(self):
        cmd = '''python -c "print('hi!')"'''
        z = simple_execute(cmd)
        self.assertEqual(z, 0)

        cmd = '''python -c "import sys; sys.exit(23);"'''
        with self.assertRaises(ReturnCodeError):
            z = simple_execute(cmd)
            self.assertEqual(z, 23)

        z = simple_execute(cmd, check_return_code_and_raise_error=False)
        self.assertEqual(z, 23)


    def test_execute_set_env(self):
        cmd = 'python -c "import sys, os; ' \
              'os.environ.get(\'SSECRET\') == \'SSECRET!\' and sys.exit(24);"'
        z = simple_execute(cmd)
        self.assertEqual(z, 0)

        cmd = 'python -c "import sys, os; ' \
              'os.environ.get(\'SSECRET\') == \'SSECRET!\' or sys.exit(24);"'
        env = self.make_default_env({'SSECRET': 'SSECRET!'})
        z = simple_execute(cmd, env=env)
        self.assertEqual(z, 0)

    def test_security_execute(self):
        python = self.get_python_command_path()
        cmd = '"{0}" -c "import sys; ' \
              '\'SSECRET! $SSECRET\' == ' \
              '\'SSECRET! \' + \'$\' + \'SSECRET\' or sys.exit(29)"'\
            .format(python)

        z = simple_execute(cmd)
        self.assertEqual(z, 0)

    @unittest.skipIf(sys.platform == 'win32', 'Windows skip ..')
    def test_security_execute2(self):
        python = self.get_python_command_path()
        cmd = '"{0}" -c "import sys; ' \
              '\'SSECRET! $SSECRET\' != ' \
              '\'SSECRET! \' + \'$\' + \'SSECRET\' or sys.exit(29)"'\
            .format(python)

        z = simple_execute(cmd, shell=True)
        self.assertEqual(z, 0)

    @unittest.skipIf(sys.platform == 'win32', 'Windows skip ..')
    def test_execute_with_output(self):
        cmd = '''python -c "print('hi!')"'''
        z, out, _ = execute(cmd)
        out = out.strip()
        self.assertEqual(z, 0)
        self.assertEqual(out, b'hi!')

        secret_env = 'AKAWKFN'
        cmd = _make_print_environ_cmd(secret_env)
        z, out, _ = execute(cmd)
        out = out.strip()
        self.assertEqual(z, 0)
        self.assertEqual(out, b"None")

        env = self.make_default_env({secret_env: "SECRET!"})
        z, out, _ = execute(cmd, env=env)
        out = out.strip()
        self.assertEqual(z, 0)
        self.assertEqual(out, b"SECRET!")

    @unittest.skipIf(sys.platform == 'win32', 'Windows skip ..')
    def test_security_execute_with_output(self):
        python = self.get_python_command_path()
        cmd = '"{0}" -c "import sys; print(\'SSECRET! $SSECRET %SSECRET%\')"'\
            .format(python)

        z, out, _ = execute(cmd)
        out = out.strip()
        self.assertEqual(z, 0)
        self.assertEqual(b'SSECRET! $SSECRET %SSECRET%', out, 'INSECURE~!!')

    @unittest.skipIf(sys.platform == 'win32', 'Windows skip ..')
    def test_security_execute_with_output2(self):
        python = self.get_python_command_path()
        cmd = '"{0}" -c "import sys; print(\'SSECRET! $SSECRET %SSECRET%\')"'\
            .format(python)
        z, out, _ = execute(cmd, shell=True)
        out = out.strip()
        self.assertEqual(z, 0)
        self.assertNotEqual(out, b'SSECRET! $SSECRET %SSECRET%')

    def test_execute_init_env_script(self):
        with self.assertRaises(InitEnvScriptError):
            _execute_init_env_script('kawbgajwbgkabg')

        with tempfile.TemporaryDirectory() as tmpdirname:
            self.assertTrue(os.path.exists(tmpdirname))
            os.system('virtualenv {0}'.format(tmpdirname))

            if sys.platform == 'win32':
                path = os.path.join(tmpdirname, 'Scripts', 'activate')
            else:
                path = os.path.join(tmpdirname, 'bin', 'activate')
            env = _execute_init_env_script(path)

        self.assertEqual(env['VIRTUAL_ENV'], tmpdirname)

    def make_default_env(self, extra=None):
        # required for starting python on windows
        cmd = _make_print_environ_cmd('SYSTEMROOT')
        out = subprocess.check_output(cmd, shell=True)
        SYSTEMROOT = out.strip().decode('ascii')
        env = {'SYSTEMROOT': SYSTEMROOT}
        if extra:
            env.update(extra)
        return env

    def get_python_command_path(self):
        cmd = "python -c \"import sys; print(sys.executable)\""
        out = subprocess.check_output(cmd, shell=True)
        PYTHON = out.strip().decode('ascii')
        return PYTHON


if __name__ == "__main__":
    unittest.main()
