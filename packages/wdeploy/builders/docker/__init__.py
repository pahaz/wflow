from __future__ import unicode_literals, print_function, generators, division

from wdeploy.project_info import ProjectInfo
from wdeploy.validators import check_process_type
from wutil._six import text_type

__author__ = 'pahaz'
DOCKER_CLIENT_BASE_URL = 'unix://var/run/docker.sock'
DOCKER_CLIENT_VERSION = '1.13'
BUILDSTEP_IMAGE = 'herokuish:dev'


def _make_process_command(process_type):
    check_process_type(process_type)
    return '/bin/bash -c "/start {0}"'.format(process_type)


def _parse_container_name(name):
    if not isinstance(name, text_type):
        t = type(name).__name__
        raise TypeError("Bad name type ({0}). Text type required".format(t))
    name = name.strip('/')
    try:
        image, process_type, index = name.rsplit("__", 2)
        check_image_name(image)
        index = int(index)
    except ValueError:
        return None, None, None
    return image, process_type, index


def _make_container_name(image, precess_type, index):
    if not isinstance(image, text_type):
        t = type(image).__name__
        raise TypeError("Bad image type ({0}). Text type required".format(t))
    if not isinstance(precess_type, text_type):
        raise TypeError("Bad precess_type type. Text type required")
    if not isinstance(index, (int, text_type)):
        raise TypeError("Bad index type. Text type required")
    return "{0}__{1}__{2}".format(image, precess_type, index)


def _clean_container_name(name):
    if name is None:
        return None
    if not isinstance(name, text_type):
        t = type(name).__name__
        raise TypeError("Bad name type ({0}). Text type required".format(t))
    image, process_type, index = _parse_container_name(name)
    is_correct_name = image is not None and process_type is not None and \
        index is not None
    return _make_container_name(image, process_type, index) \
        if is_correct_name else None


def _parse_image_name(name):
    if not isinstance(name, text_type):
        t = type(name).__name__
        raise TypeError("Bad name type ({0}). Text type required".format(t))
    name = name.split(':', 1)[0]
    try:
        build, project_name, version = name.rsplit("__", 2)
        if 'build' != build:
            raise ValueError
    except ValueError:
        return None, None
    return project_name, version


def _make_image_name(project_name, version):
    if isinstance(project_name, ProjectInfo):
        project_name = project_name.name
    if not isinstance(project_name, text_type):
        t = type(project_name).__name__
        raise TypeError("Bad project_name type ({0}). Text type required"
                        .format(t))
    return "build__{0}__{1}".format(project_name, version)


def _clean_image_name(name):
    """
    Default image name may contain version string. This function cleaning
    image name.

    Example:

        build__test3__2015.05.06-10H-29M-14S:latest - docker image name
        build__test3__2015.05.06-10H-29M-14S - cleaned image name

    :param name: docker image name
    :return: str if image name is correct else None
    """
    if name is None:
        return None
    if not isinstance(name, text_type):
        t = type(name).__name__
        raise TypeError("Bad name type ({0}). Text type required".format(t))
    project_name, version = _parse_image_name(name)
    is_correct_name = project_name is not None and version is not None
    return _make_image_name(project_name, version) if is_correct_name else None


def check_image_name(name):
    project_name, version = _parse_image_name(name)
    if project_name is None or version is None:
        raise ValueError()


def check_container_name(name):
    image, process_type, index = _parse_container_name(name)
    if image is None or process_type is None or index is None:
        raise ValueError()
