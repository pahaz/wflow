from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
from wutil._six import add_metaclass

__author__ = 'pahaz'


@add_metaclass(ABCMeta)
class BaseContainer(object):
    STATUS_RUNNING = 'running'
    STATUS_STOPPED = 'stopped'

    @property
    def is_running(self):
        """ Return True if container is running
        :return: bool
        """
        return self.status == self.STATUS_RUNNING

    @property
    @abstractmethod
    def status(self):
        """ Return container status
        :return: str
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self):
        """ Return container name
        :return: str
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def image(self):
        """ Return image
        :return: str
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        """ Return container name
        :return: str
        """
        raise NotImplementedError

    def __str__(self):
        # id_ = self.id[:12] + "..." if len(self.id) > 12 else self.id
        return "Container {0} ({1})".format(self.name, self.status)

    def __repr__(self):
        # id_ = self.id[:12] + "..." if len(self.id) > 12 else self.id
        return "<Container({0}, {1})>".format(self.name, self.status)

    def __eq__(self, other):
        t1 = type(self)
        t2 = type(other)
        if issubclass(t1, t2) or issubclass(t2, t1):
            return self.id == other.id
        return False
    # ...

    def get_environment(self):
        pass

    def get_links(self):
        pass

    def get_build_version(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def kill(self):
        pass

    def restart(self):
        pass

    def remove(self):
        pass

    def wait(self):
        pass

    # def logs(self):
    #     pass
