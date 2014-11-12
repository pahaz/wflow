import os
import stat
import subprocess

__author__ = 'pahaz'


def read_content(path):
    with open(path) as f:
        content = f.read().strip()
    return content


def write_content(path, content):
    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))


def set_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)


def execute(command, env, shell=False, cwd=None):
    if not shell:
        command = [command]
    return subprocess.call(command, env=env, shell=shell, cwd=cwd)


def execute_with_venv_activate(venv_path, command, command_env, cwd=None):
    venv_activate_path = os.path.join(venv_path, 'bin', 'activate')
    if not os.path.exists(venv_activate_path):
        venv_activate_path = None

    prefix = '. {0} && '.format(venv_activate_path) \
        if venv_activate_path else ''

    return execute(prefix + command, command_env, shell=True, cwd=cwd)
