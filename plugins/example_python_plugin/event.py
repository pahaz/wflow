from __future__ import print_function
import os

__author__ = 'pahaz'
__plugin_root__ = os.path.dirname(__file__)


def strenv(env):
    return '\n'.join(["{0}={1}".format(k, v) for k, v in env.items()])


def simple_event_listener(manager, env):
    # save current cwd
    _cwd = os.getcwd()
    os.chdir(__plugin_root__)

    NAME = env.get('PLATFORM_NAME')
    PLUGIN_INSTALLER_COMMAND = env.get('PLATFORM_PLUGIN_INSTALLER_COMMAND')
    TRIGGER_EVENT_COMMAND = env.get('PLATFORM_TRIGGER_EVENT_COMMAND')
    USER_NAME = env.get('PLATFORM_USERNAME')
    DATA_PATH = env.get('PLATFORM_DATA_PATH')
    PLUGINS_PATH = env.get('PLATFORM_PLUGINS_PATH')
    VENV_PATH = env.get('PLATFORM_VENV_PATH')

    print("event example ... ")
    print("event example ... ")
    print("simple_event_listener(**{0!r})".format(env.as_dict()))
    print(strenv(env))
    print("PWD=" + __plugin_root__)
    print('EVENT!',
          NAME, PLUGIN_INSTALLER_COMMAND, TRIGGER_EVENT_COMMAND, USER_NAME,
          DATA_PATH, PLUGINS_PATH, VENV_PATH)
    print('hook ... example ...')
    print('hook ... example ...')

    # restore cwd
    os.chdir(_cwd)
