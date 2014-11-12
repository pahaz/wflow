from __future__ import unicode_literals
import subprocess
import unittest

__author__ = 'stribog'

SCRIPT_NAME = 'wflow'
SCRIPT_PLUGIN_INSTALLER_NAME = SCRIPT_NAME + '-install-plugin'
SCRIPT_TRIGGER_EVENT_NAME = SCRIPT_NAME + '-trigger-event'

SCRIPT_USER_NAME = 'wflow'
SCRIPT_DATA_PATH = '/home/' + SCRIPT_USER_NAME

SCRIPT_PLUGIN_PATH = '/var/lib/' + SCRIPT_NAME + '/plugins'
SCRIPT_VENV_PATH = '/var/lib/' + SCRIPT_NAME + '/venv'
SCRIPT_PATH = '/usr/local/bin/' + SCRIPT_NAME
SCRIPT_PLUGIN_INSTALLER_PATH = '/usr/local/bin/' + SCRIPT_PLUGIN_INSTALLER_NAME
SCRIPT_TRIGGER_EVENT_PATH = '/usr/local/bin/' + SCRIPT_TRIGGER_EVENT_NAME


def local(cmd, capture=True, env=None):
    try:
        stdout_and_stderr = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        print('EXCEPTED (code {1}): \n{0}'.format(e.output, e.returncode))
        raise
    if capture:
        return stdout_and_stderr


class TestPlugin(unittest.TestCase):
    def test_example_simple_plugin(self):
        local('make create_files')
        local('make patch_shebang')

        z = local('wflow-install-plugin plugins/example_simple_plugin --force',
                  capture=True)

        self.assertIn('install example_simple_plugin', z)
        self.check_environments(z)
        self.check_path(z)

        z = local('wflow-trigger-event example-bash',
                  capture=True)

        self.assertIn('event example-bash', z)
        self.check_environments(z)
        self.check_pwd(SCRIPT_PLUGIN_PATH + '/example_simple_plugin', z)
        self.check_path(z)

        z = local('wflow-trigger-event example-python3',
                  capture=True)

        self.assertIn('event example-python3', z)
        self.check_environments(z)
        self.check_pwd(SCRIPT_PLUGIN_PATH + '/example_simple_plugin', z)
        self.check_path(z)

        z = local('wflow-install-plugin plugins/example_python_plugin --force',
                  capture=True)

        self.assertIn('install example_python_plugin', z)
        self.check_environments(z)
        self.check_path(z)

        z = local('wflow-trigger-event example',
                  capture=True)

        self.assertIn('event example', z)
        self.check_environments(z)
        self.check_pwd(SCRIPT_PLUGIN_PATH + '/example_python_plugin', z)

    def check_environments(self, z):
        self.assertIn('SCRIPT_NAME=' + SCRIPT_NAME, z)
        self.assertIn('SCRIPT_PLUGIN_INSTALLER_NAME=' +
                      SCRIPT_PLUGIN_INSTALLER_NAME, z)
        self.assertIn('SCRIPT_TRIGGER_EVENT_NAME=' +
                      SCRIPT_TRIGGER_EVENT_NAME, z)
        self.assertIn('SCRIPT_DATA_PATH=' + SCRIPT_DATA_PATH, z)
        self.assertIn('SCRIPT_PLUGIN_PATH=' + SCRIPT_PLUGIN_PATH, z)
        self.assertIn('SCRIPT_VENV_PATH=' + SCRIPT_VENV_PATH, z)

    def check_pwd(self, pwd, z):
        self.assertIn('PWD=' + pwd, z)

    def check_path(self, z):
        self.assertIn('PATH=/var/lib/wflow/venv/bin', z)


if __name__ == "__main__":
    unittest.main()
