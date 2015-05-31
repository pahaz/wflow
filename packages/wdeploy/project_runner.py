from __future__ import unicode_literals, print_function, generators, division
from abc import ABCMeta, abstractmethod

from wdeploy.project_info import ProjectInfo
from wutil._six import add_metaclass

__author__ = 'pahaz'
LAST_IMAGE = object()


class NoImagesError(Exception):
    """
    Raised in project runner constructor. If no Images for running container.
    """


class WorkWithRemovedContainerError(Exception):
    """
    Raises when try use removed container.
    """


@add_metaclass(ABCMeta)
class BaseProjectRunner(object):
    def __init__(self, project_info, options):
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

    @property
    @abstractmethod
    def containers(self):
        """ Return iterable containers object
        :return: tuple
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def images(self):
        """ Return iterable images object
        :return: tuple
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def latest_image(self):
        """ Return the latest build image object
        :return: str
        """
        raise NotImplementedError

    # .....

    def runi(self, command, image=LAST_IMAGE):
        pass

    def run(self, command, image=LAST_IMAGE):
        pass

    def remove_stopped(self):
        pass

    def start_stopped_containers(self):
        """ Run a containers that has already been started but now stopped
        """

    def stop_all_containers(self):
        """ The main process inside the all containers will receive SIGTERM,
        and after a grace period, SIGKILL
        """

    def kill_all_containers(self):
        """ The main process inside the all containers will receive SIGKILL
        """

    def restart_all_containers(self):
        """ stop_all_containers and start_stopped_containers
        """

    def recreate_all_containers(self):
        pass

    def run_one_new_container(self):
        """ Run container on top of built image
        """

    def run_command_in_one_container(self):
        pass
