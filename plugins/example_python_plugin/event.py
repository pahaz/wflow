from __future__ import print_function
import os

__author__ = 'pahaz'
__plugin_root__ = os.path.dirname(__file__)


def strenv(env):
    return '\n'.join(["{0}={1}".format(k, v) for k, v in env.items()])


def simple_event_listener(**kwargs):
    # save current cwd
    _cwd = os.getcwd()
    os.chdir(__plugin_root__)

    env = kwargs.get('env') or {}
    NAME = env.get('SCRIPT_NAME')
    PLUGIN_INSTALLER_NAME = env.get('SCRIPT_PLUGIN_INSTALLER_NAME')
    TRIGGER_EVENT_NAME = env.get('SCRIPT_TRIGGER_EVENT_NAME')
    USER_NAME = env.get('SCRIPT_USER_NAME')
    DATA_PATH = env.get('SCRIPT_DATA_PATH')
    PLUGINS_PATH = env.get('SCRIPT_PLUGINS_PATH')
    VENV_PATH = env.get('SCRIPT_VENV_PATH')

    print("event example ... ")
    print("event example ... ")
    print("simple_event_listener(**{0!r})".format(kwargs))
    print(strenv(env))
    print("PWD=" + __plugin_root__)
    print('EVENT!',
          NAME, PLUGIN_INSTALLER_NAME, TRIGGER_EVENT_NAME, USER_NAME,
          DATA_PATH, PLUGINS_PATH, VENV_PATH)
    print('hook ... example ...')
    print('hook ... example ...')

    # restore cwd
    os.chdir(_cwd)
