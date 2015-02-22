import json
import logging
import os
import shlex
import subprocess
import sys
import select
import time

from wutil._six import text_type


__author__ = 'pahaz'
log = logging.getLogger(__name__)


class ReturnCodeError(Exception):
    pass


class InitEnvScriptError(Exception):
    pass


def simple_execute(command,
                   cwd=None,
                   env=None,
                   init_env_script=None,
                   init_env_script_use_cache=True,
                   shell=False,
                   check_return_code_and_raise_error=True):
    """Execute shell command (DEPRECATED)

    :param command: shell command
    :param env: shell environment
    :param shell: use row shell (False = secure)
    :param cwd: work dir
    :return: command exit status code
    """
    r, _, _ = execute(
        command, env=env, shell=shell, cwd=cwd,
        init_env_script=init_env_script,
        init_env_script_use_cache=init_env_script_use_cache,

        stderr_to_stdout=True,
        is_collecting_to_buf_stdout=False,
        is_collecting_to_buf_stderr=False,
        stdout=sys.stderr,
        stderr=None,

        check_return_code_and_raise_error=check_return_code_and_raise_error, )
    return r


def execute(
        command,
        cwd=None,
        env=None,
        init_env_script=None,
        init_env_script_use_cache=True,
        shell=False,

        stderr_to_stdout=False,
        is_collecting_to_buf_stdout=True,
        is_collecting_to_buf_stderr=True,
        stdout=sys.stdout,
        stderr=sys.stderr,

        check_return_code_and_raise_error=True):
    """Execute shell command

    # TODO: timeouts

    :param command: command
    :param cwd: current work dir
    :param env: environment
    :param init_env_script: environment initialize script
    :param init_env_script_use_cache: cache script environment
    :param shell: use shell (False = secure)
    :param stderr_to_stdout: redirect stderr to stdout
    :param check_return_code_and_raise_error: raise exception if return code != 0
    :param is_collecting_to_buf_stdout: collect stdout and return it
    :param is_collecting_to_buf_stderr: collect stderr and return it
    :param stdout: stdout pipe
    :param stderr: stderr pipe
    :return: tuple(int(return code), bytes(output), bytes(error))
    """
    printable_command = ' '.join(command) \
        if isinstance(command, (tuple, list)) else command

    # https://github.com/pexpect/pexpect/issues/30/
    if hasattr(stdout, 'buffer'):
        stdout = getattr(stdout, 'buffer')
    if hasattr(stderr, 'buffer'):
        stderr = getattr(stderr, 'buffer')

    if env and not isinstance(env, dict):
        if hasattr(env, 'as_dict'):
            env = env.as_dict()
        else:
            raise TypeError("'env' argument must be a dict type or "
                            "hasattr .as_dict()")

    if init_env_script:
        init_env = _execute_init_env_script(
            init_env_script,
            cache_path_env=init_env_script_use_cache)
        if env:
            init_env.update(env.items())
        env = init_env

    if not shell and isinstance(command, text_type):
        command = shlex.split(command)

    _buf_out = []
    _buf_err = []
    _stdout = subprocess.PIPE
    _stderr = subprocess.STDOUT if stderr_to_stdout else subprocess.PIPE

    log.debug('execute({0}, env={1!r}, shell={2}, cwd={3}) err={4} out={5}'
              .format(printable_command, env, shell, cwd, _stderr, _stdout))
    t0 = time.time()

    with subprocess.Popen(command,
                          env=env,
                          shell=shell,
                          cwd=cwd,
                            # stdin=subprocess.STD_INPUT_HANDLE,
                          stdout=_stdout,
                          stderr=_stderr) as proc:
        try:

            if not is_collecting_to_buf_stderr and \
                    not is_collecting_to_buf_stdout and \
                    not stdout and not stderr:
                proc.wait()

            if stderr_to_stdout and not is_collecting_to_buf_stdout and \
                    not stdout:
                proc.wait()

            if stderr_to_stdout:
                while proc.poll() is None:
                    t = proc.stdout.read()
                    if is_collecting_to_buf_stdout:
                        _buf_out.append(t)
                    if stdout:
                        stdout.write(t)

            else:
                ds = [proc.stdout, proc.stderr]

                log.debug('before select in={0}'.format(proc.stdin))

                while proc.poll() is None:
                    r, _, _ = select.select(ds, [], [])

                    print('select')

                    if proc.stdout in ds:
                        t = proc.stdout.read()
                        log.info('t:' + repr(t))
                        if is_collecting_to_buf_stdout:
                            _buf_out.append(t)
                        if stdout:
                            stdout.write(t)

                    if proc.stderr in ds:
                        t = proc.stderr.read()
                        log.info('t:' + repr(t))
                        if is_collecting_to_buf_stderr:
                            _buf_err.append(t)
                        if stderr:
                            stderr.write(t)



        except Exception:
            log.exception("Exception '{0}'".format(printable_command))
            proc.kill()
            proc.wait()

    return_code = proc.returncode
    t1 = time.time()
    log.debug('{4} <- {5} - simple_execute({0}, env={1!r}, shell={2}, cwd={3})'
              .format(printable_command, env, shell, cwd, return_code,
                      t1 - t0))
    if return_code != 0 and check_return_code_and_raise_error:
        raise ReturnCodeError('"{0}" return code {1} != 0'
                              .format(printable_command, return_code))

    return return_code, b''.join(_buf_out), b''.join(_buf_err)


def _execute_init_env_script(path, cache_path_env=True):
    # TODO: use cache decorator
    # TODO: windows support
    _cache = getattr(_execute_init_env_script, '_cache', None)
    if not _cache:
        _cache = {}
        setattr(_execute_init_env_script, '_cache', _cache)

    if not cache_path_env:
        _cache = {}

    if path in _cache:
        return _cache[path]

    if not os.path.exists(path):
        msg = "'init_env_script' path not exists"
        log.error(msg)
        raise InitEnvScriptError(msg)

    json_dumps_env = 'python -c "' \
                     'import os, json; ' \
                     'print(json.dumps(dict(os.environ.items())));' \
                     '"'

    if sys.platform == 'win32':
        json_dumps_env = '{0} && {1}'.format(path, json_dumps_env)
    else:
        json_dumps_env = '. {0} && {1}'.format(path, json_dumps_env)

    return_code, json_, _ = execute(
        json_dumps_env,
        shell=True,

        stderr_to_stdout=True,
        is_collecting_to_buf_stdout=True,
        is_collecting_to_buf_stderr=False,
        stdout=None,
        stderr=None,

        check_return_code_and_raise_error=False, )

    if return_code != 0:
        msg = "'init_env_script' return code {0} != 0".format(return_code)
        log.error(msg)
        raise InitEnvScriptError(msg)

    json_ = json_.decode('ascii')
    env = json.loads(json_)

    if 'PWD' in env:
        del env['PWD']

    _cache[path] = env
    return env
