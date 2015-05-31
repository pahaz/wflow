from __future__ import unicode_literals, print_function, generators, division
import os
import re

from wutil._six import text_type

__author__ = 'pahaz'
VALID_NAME_PATTERN = r'^[a-z0-9-.]+$'  # `_` - special symbol
VALID_VERSION_PATTERN = r'^[a-z0-9-.]+$'  # `_` - special symbol
PROCESS_TYPE_PATTERN = r'^[a-z0-9-.]+$'


class ValidationError(ValueError):
    pass


def check_path_is_dir(path):
    if not os.path.exists(path):
        raise ValidationError('Invalid path "{0}". Not exists'.format(path))
    if not os.path.isdir(path):
        raise ValidationError('Invalid path "{0}". Is\'t a directory'
                              .format(path))


def check_project_name(name):
    _re_validator(VALID_NAME_PATTERN, name, 'project name')


def check_project_version_name(version):
    _re_validator(VALID_VERSION_PATTERN, version, 'project version name')


def check_process_type(type_):
    _re_validator(PROCESS_TYPE_PATTERN, type_, 'process type')


def check_port(port):
    try:
        port = int(port)
        if not 0 < port < 65536:
            raise ValueError('Invalid port')
    except (ValueError, TypeError):
        raise ValidationError('Invalid port. Required 0 < port number < 65536')


def check_index(index):
    if not isinstance(index, int):
        raise ValidationError('Invalid index type. int required.')
    if index <= 0:
        raise ValidationError('Invalid index value. 0 < index')


def _re_validator(pattern, value, name):
    if not isinstance(value, text_type):
        raise ValidationError('Invalid `{0}`. Required text type'.format(name))
    if not re.match(pattern, value):
        raise ValidationError('Invalid `{0}`. Use chars: `{1}`'
                              .format(name, pattern))
