from __future__ import unicode_literals, print_function, generators, division
import logging
import unittest
from wdeploy.builders.docker import _make_container_name

from wdeploy.builders.docker.runner import DockerProjectRunner
from wdeploy.builders.docker.test import make_test_image
from wdeploy.builders.docker.utils import create_docker_client, \
    create_container
from wdeploy.test import make_mock_project_info

__author__ = 'pahaz'
logging.basicConfig(level=logging.DEBUG)


class BaseDockerProjectRunner(unittest.TestCase):
    @staticmethod
    def make_info():
        return make_mock_project_info(name='test-runner')

    @staticmethod
    def make_runner():
        info = TestScaleDockerProjectRunner.make_info()
        r = DockerProjectRunner(info, {})
        return r

    @staticmethod
    def clean_containers():
        r = TestScaleDockerProjectRunner.make_runner()
        for x in r.containers:
            r.remove(x)

    @classmethod
    def tearDownClass(cls):
        cls.clean_containers()

    @classmethod
    def setUpClass(cls):
        info = make_mock_project_info(name='test-runner')
        make_test_image(info)
        cls.clean_containers()


class TestScaleDockerProjectRunner(BaseDockerProjectRunner):
    def test_scale_1(self):
        r = self.make_runner()
        count_before = len(r.containers)
        r.scale('scale-1')
        count_after = len(r.containers)

        self.assertEqual(count_after - count_before, 1)

    def test_scale_2(self):
        r = self.make_runner()
        count_before = len(r.containers)
        r.scale('scale-2', 2)
        count_after = len(r.containers)

        self.assertEqual(count_after - count_before, 2)

    def test_scale_1_then_2(self):
        r = self.make_runner()

        count_before = len(r.containers)
        r.scale('scale-1-then-2', count=1)
        count_after = len(r.containers)
        self.assertEqual(count_after - count_before, 1)

        r.scale('scale-1-then-2', count=2)
        count_after = len(r.containers)
        self.assertEqual(count_after - count_before, 2)


class TestDiscoverDockerProjectRunner(BaseDockerProjectRunner):
    @staticmethod
    def create_container(image):
        c = create_docker_client()
        container_name = _make_container_name(image, 'test', 1)
        container = create_container(c, image,
                                     '/bin/sh -c "echo test"',
                                     name=container_name)
        c.close()
        return container

    def test_discover(self):
        r = self.make_runner()
        count_before = len(r.containers)
        container = self.create_container(r._latest_image)
        count_after = len(r.containers)
        self.assertEqual(count_after - count_before, 0)
        r.discover()
        count_after = len(r.containers)
        self.assertEqual(count_after - count_before, 1)
        r.remove(container)

    def test_rediscovered_images(self):
        r = self.make_runner()
        r.scale('test-reinspect')
        containers = r.containers
        images_1 = [x.image for x in containers]
        # print(images_1)
        make_test_image(r.info)
        for c in containers:
            c.reinspect()
        images_2 = [x.image for x in containers]
        # print(images_2)
        self.assertEqual(images_1, images_2)
