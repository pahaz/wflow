from __future__ import unicode_literals, print_function, generators, division

from abc import abstractmethod
import time

from wdeploy.project_info import ProjectInfo
from wutil._six import add_metaclass
from wutil.metaclasses import make_ABCMeta_metaclass_which_store_class_brothers
from .project_runner import BaseProjectRunner

__author__ = 'pahaz'
_ABCBuilderMeta = make_ABCMeta_metaclass_which_store_class_brothers()


class BuildError(Exception):
    pass


@add_metaclass(_ABCBuilderMeta)
class BaseProjectBuilder(object):
    """
    Make the new container image with the build project.
    """

    def __init__(self, project_info, options):
        """
        :param project_info: object witch contain all information about project
        :type project_info: ProjectInfo
        :param options: global settings variables
        """
        if not isinstance(project_info, ProjectInfo):
            raise TypeError('Invalid project_info type. ProjectInfo required')

        self._info = project_info
        self._options = options

    @property
    def info(self):
        """ Return project info object
        :return: ProjectInfo
        """
        return self._info

    @property
    def options(self):
        """ Return options object
        :return: dict
        """
        return self._options

    @classmethod
    @abstractmethod
    def make_ProjectBuilder_or_None(cls, project_info, options):
        """Make and return ProjectBuilder instance or return None.

        options = {
            'DOCKER_VERSION': '1.14',
        }

        :param project_info: object witch contain all information about project
        :param options: global settings variables
        :return: cls instance or None
        """
        # TODO: fix docs example!
        return None

    @abstractmethod
    def build(self, do_on_build_message=None):
        return BaseProjectRunner(self._info, self._options)

    @abstractmethod
    def make_project_runner(self):
        return BaseProjectRunner(self._info, self._options)

    @abstractmethod
    def make_image_name(self):
        return "".format(self.info.name, time.strftime("%Y.%m.%d-%HH-%MM-%SS"))
