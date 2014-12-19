from __future__ import unicode_literals
import os
import subprocess
import unittest
import tempfile

import six


__author__ = 'pahaz'

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
        print('\n- RUN EXCEPTED - (code {1})\n{0}\n'
              '----------------'.format(e.output.decode(), e.returncode))
        raise
    if capture:
        if isinstance(stdout_and_stderr, six.binary_type):
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
        z.expect(pexpect.EOF, timeout=5.0)
    except pexpect.TIMEOUT:
        print('\n- TIMEOUT - \n{0}\n'
              '----------------'.format(z.before.decode()))
        raise

    stdout_and_stderr = z.before

    if isinstance(stdout_and_stderr, six.binary_type):
        stdout_and_stderr = stdout_and_stderr.decode('utf-8', 'ignore')

    return stdout_and_stderr


def git_clone(cwd, remote_repo, password):
    import pexpect

    z = pexpect.spawn('git clone "{0}"'
                      .format(remote_repo),
                      cwd=cwd)
    try:
        ind = z.expect(['connecting (yes/no)? ', 's password:'],
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

    if isinstance(stdout_and_stderr, six.binary_type):
        stdout_and_stderr = stdout_and_stderr.decode('utf-8', 'ignore')

    return stdout_and_stderr


class TestPlugin(unittest.TestCase):
    def test_example_simple_plugin(self):
        local('make create_files')
        local('make patch_shebang')

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
        self.check_pwd(SCRIPT_PLUGIN_PATH + '/example_simple_plugin', z)
        self.check_path(z)

        z = local('wflow-trigger-event example-python3',
                  capture=True)

        self.assertIn('event example-python3', z)
        self.check_environments(z)
        self.check_pwd(SCRIPT_PLUGIN_PATH + '/example_simple_plugin', z)
        self.check_path(z)

    def test_example_python_plugin(self):
        local('make create_files')
        local('make patch_shebang')

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
        self.check_pwd(SCRIPT_PLUGIN_PATH + '/example_python_plugin', z)

        z = local('wflow printenv')
        self.check_environments(z)

        with self.assertRaises(subprocess.CalledProcessError):
            local('wflow error')

    def test_git_plugin(self):
        local('make create_files')
        local('make patch_shebang')

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

    def check_install_done(self, z):
        self.assertIn('----> done', z)


if __name__ == "__main__":
    unittest.main()
