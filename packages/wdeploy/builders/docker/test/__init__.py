from __future__ import unicode_literals, print_function, generators, division
import unittest

from docker import Client

from wdeploy.builders.docker import DOCKER_CLIENT_BASE_URL, \
    DOCKER_CLIENT_VERSION, _make_image_name
from wdeploy.builders.docker.utils import create_container, \
    create_docker_client, container_start_and_attach

__author__ = 'pahaz'


def make_test_image(info, build_command='/bin/sh -c "echo do build .."',
                    varsion='1', base_image='busybox'):
    client = create_docker_client()
    new_image_name = _make_image_name(info.name, varsion)
    container = create_container(client, base_image, build_command)
    container_start_and_attach(client, container, lambda x: print(repr(x)))
    image = client.commit(container.id, new_image_name)
    client.remove_container(container.id)
    client.close()
    return image['Id']


class BaseDockerContainerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_url = DOCKER_CLIENT_BASE_URL
        version = DOCKER_CLIENT_VERSION
        cls.client = Client(base_url=base_url, version=version)
        cls.test_containers = []

    @classmethod
    def tearDownClass(cls):
        for x in cls.test_containers:
            cls.client.kill(x)
            cls.client.remove_container(x, force=True)
        cls.client.close()

    def make_container(self, command='/bin/sh -c "echo finished"',
                       image='busybox', name=None, environment=None,
                       volumes=None, ports=None):
        cls = type(self)
        container = create_container(cls.client, image, command, name=name,
                                  environment=environment,
                                  volumes=volumes, ports=ports)
        cls.test_containers.append(container.id)
        return container
