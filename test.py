from __future__ import unicode_literals
import os
import subprocess
import unittest
import tempfile
import sys

__author__ = 'pahaz'

if sys.version_info[0] == 3:
    binary_type = bytes
else:
    binary_type = str

PLATFORM_NAME = 'wflow'
PLATFORM_PLUGIN_INSTALLER_COMMAND = PLATFORM_NAME + '-install-plugin'
PLATFORM_TRIGGER_EVENT_COMMAND = PLATFORM_NAME + '-trigger-event'

PLATFORM_USERNAME = 'wflow'
PLATFORM_DATA_PATH = '/home/' + PLATFORM_USERNAME

PLATFORM_PLUGINS_PATH = '/var/lib/' + PLATFORM_NAME + '/plugins'
PLATFORM_VENV_PATH = '/var/lib/' + PLATFORM_NAME + '/venv'
PLATFORM_PATH = '/usr/local/bin/' + PLATFORM_NAME
PLATFORM_PLUGIN_INSTALLER_PATH = '/usr/local/bin/' + \
                                 PLATFORM_PLUGIN_INSTALLER_COMMAND
PLATFORM_EVENT_TRIGGER_PATH = '/usr/local/bin/' + PLATFORM_TRIGGER_EVENT_COMMAND


def local(cmd, capture=True, env=None):
    print('run command `{0}`'.format(cmd))
    try:
        stdout_and_stderr = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        print('\n- RUN EXCEPTED - (code {1})\n{0}\n'
              '----------------'.format(e.output.decode(), e.returncode))
        raise
    if capture:
        if isinstance(stdout_and_stderr, binary_type):
            stdout_and_stderr = stdout_and_stderr.decode('utf-8', 'ignore')
        return stdout_and_stderr


def set_user_password(user, password):
    p = subprocess.Popen(['passwd', user], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write('{0}\n'.format(password).encode())
    p.stdin.write(password.encode())
    stdout, stderr = p.communicate()
    # print(stderr, stdout)
    assert b'password updated successfully' in stderr
    assert not stdout


def git_push(cwd, remote_repo, password):
    import pexpect

    z = pexpect.spawn('git push "{0}" master'
                      .format(remote_repo),
                      cwd=cwd)

    try:
        ind = z.expect(['connecting (yes/no)?', 's password:'],
                       timeout=1.0)
        if ind == 0:
            z.sendline('yes')
            z.expect('s password:', timeout=1.0)

        z.sendline(password)
        z.expect(pexpect.EOF, timeout=10.0)
    except pexpect.TIMEOUT:
        print('\n- TIMEOUT - \n{0}\n'
              '----------------'.format(z.before.decode()))
        raise

    stdout_and_stderr = z.before

    if isinstance(stdout_and_stderr, binary_type):
        stdout_and_stderr = stdout_and_stderr.decode('utf-8', 'ignore')

    return stdout_and_stderr


def git_clone(cwd, remote_repo, password):
    import pexpect

    z = pexpect.spawn('git clone "{0}"'
                      .format(remote_repo),
                      cwd=cwd)
    try:
        ind = z.expect(['connecting (yes/no)?', 's password:'],
                       timeout=1.0)
        if ind == 0:
            z.sendline('yes')
            z.expect('s password:', timeout=1.0)

        z.sendline(password)
        z.expect(pexpect.EOF, timeout=5.0)
    except pexpect.TIMEOUT:
        print('\n- TIMEOUT - \n{0}\n'
              '----------------'.format(z.before.decode()))
        raise

    stdout_and_stderr = z.before

    if isinstance(stdout_and_stderr, binary_type):
        stdout_and_stderr = stdout_and_stderr.decode('utf-8', 'ignore')

    return stdout_and_stderr


class TestPlugin(unittest.TestCase):
    def test_example_simple_plugin(self):
        local('make create_scripts')
        local('make create_configs')
        local('make patch_shebang')
        local('make create_user')

        z = local('wflow-install-plugin plugins/example_simple_plugin --force',
                  capture=True)

        self.assertIn('install example_simple_plugin', z)
        self.check_install_done(z)
        self.check_environments(z)
        self.check_path(z)

        z = local('wflow-trigger-event example-bash',
                  capture=True)

        self.assertIn('event example-bash', z)
        self.check_environments(z)
        self.check_pwd(PLATFORM_PLUGINS_PATH + '/example_simple_plugin', z)
        self.check_path(z)

        z = local('wflow-trigger-event example-python3',
                  capture=True)

        self.assertIn('event example-python3', z)
        self.check_environments(z)
        self.check_pwd(PLATFORM_PLUGINS_PATH + '/example_simple_plugin', z)
        self.check_path(z)

    def test_example_python_plugin(self):
        local('make create_scripts')
        local('make create_configs')
        local('make patch_shebang')
        local('make create_user')

        z = local('wflow-install-plugin plugins/example_python_plugin --force',
                  capture=True)

        self.assertIn('install example_python_plugin', z)
        self.check_install_done(z)
        self.check_environments(z)
        self.check_path(z)

        z = local('wflow-trigger-event example',
                  capture=True)

        self.assertIn('event example', z)
        self.check_environments(z)
        self.check_pwd(PLATFORM_PLUGINS_PATH + '/example_python_plugin', z)

        z = local('wflow printenv')
        self.check_environments(z)

        with self.assertRaises(subprocess.CalledProcessError):
            local('wflow error')

    def test_git_plugin(self):
        local('make create_scripts')
        local('make create_configs')
        local('make patch_shebang')
        local('make create_user')
        local('make test_requirements')
        local('wflow-deactivate-plugin docker_buildstep_plugin')

        passwd = 'qwer'

        z = local('wflow-install-plugin plugins/git_plugin --force',
                  capture=True)
        self.check_install_done(z)

        set_user_password('wflow', passwd)

        project_name = 'nalksegbjeusbawufbaaw.8iq.ru'
        remote_repo = 'ssh://wflow@127.0.0.1/' + project_name
        with tempfile.TemporaryDirectory() as tmpdirname:
            repo_local_path = os.path.join('/home/wflow/', project_name)
            if os.path.exists(repo_local_path):
                local('rm -rf {0}'.format(repo_local_path))

            local('cd {0} && echo "2" > README.md'.format(tmpdirname))
            local('cd {0} && echo "{1}" > secret.txt'
                  .format(tmpdirname, project_name))

            local('cd {0} && git init'.format(tmpdirname))
            local('cd {0} && git add *'.format(tmpdirname))
            local('cd {0} && git commit -am "init"'.format(tmpdirname))

            z = git_push(tmpdirname,
                         remote_repo,
                         passwd)

            self.assertIn(project_name, z)
            self.assertIn(' * [new branch]      master -> master', z)
            self.assertNotIn(' ! [rejected]        master -> master', z)
            self.assertIn('Writing objects: 100%', z)

            z = git_clone(tmpdirname,
                          remote_repo,
                          passwd)

            self.assertIn(project_name, z)
            self.assertIn('Receiving objects: 100%', z)

            secret_txt = os.path.join(tmpdirname, project_name, 'secret.txt')
            with open(secret_txt) as f:
                z = f.read().strip()

            self.assertEqual(z, project_name)

        local('wflow-activate-plugin docker_buildstep_plugin')

    def check_environments(self, z):
        self.assertIn('PLATFORM_NAME=' + PLATFORM_NAME, z)
        self.assertIn('PLATFORM_PLUGIN_INSTALLER_COMMAND=' +
                      PLATFORM_PLUGIN_INSTALLER_COMMAND, z)
        self.assertIn('PLATFORM_TRIGGER_EVENT_COMMAND=' +
                      PLATFORM_TRIGGER_EVENT_COMMAND, z)
        self.assertIn('PLATFORM_DATA_PATH=' + PLATFORM_DATA_PATH, z)
        self.assertIn('PLATFORM_PLUGINS_PATH=' + PLATFORM_PLUGINS_PATH, z)
        self.assertIn('PLATFORM_VENV_PATH=' + PLATFORM_VENV_PATH, z)

    def check_pwd(self, pwd, z):
        self.assertIn('PWD=' + pwd, z)

    def check_path(self, z):
        self.assertIn('PATH=/var/lib/wflow/venv/bin', z)

    def check_install_done(self, z):
        self.assertIn('----> done', z)


if __name__ == "__main__":
    unittest.main()
