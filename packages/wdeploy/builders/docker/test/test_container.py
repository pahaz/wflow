from __future__ import unicode_literals, print_function, generators, division
import random
import string
import unittest

from wdeploy.builders.docker.container import DockerContainer
from wdeploy.builders.docker.test import BaseDockerContainerTestCase
from wdeploy.container import BaseContainer
from wutil.execute3 import execute

__author__ = 'pahaz'


def make_random_salt(y):
    SALT = ''.join([random.choice(string.ascii_letters) for x in range(y)])
    return SALT


class TestContainer(BaseDockerContainerTestCase):
    @unittest.skip('long')
    def test_puling_image(self):
        execute('docker rmi busybox')
        self.make_container(image='busybox')

    def test_default_docker_create_options(self):
        c = self.make_container()
        self.assertTrue(c.is_detached)
        self.assertTrue(not c.is_interactive)
        self.assertFalse(c.is_running)
        self.assertEqual(c.status, BaseContainer.STATUS_STOPPED)
        self.assertIsNotNone(c.name)
        self.assertIsNotNone(c.image)
        self.assertIsNotNone(c.id)
        self.assertEqual(c.image, 'busybox')
        self.assertEqual(c.index, None)
        self.assertEqual(c.type, None)

    @unittest.skip('docker.errors.InvalidVersion: rename was only introduced '
                   'in API version 1.17')
    def test_rename(self):
        SALT = make_random_salt(5)
        NAME = 'name' + SALT
        NEW_NAME = 'newname' + SALT
        c = self.make_container(name=NAME)
        self.assertEqual(c.name, NAME)
        c.rename(NEW_NAME)
        self.assertEqual(c.name, NEW_NAME)

    def test_start_stop(self):
        COMMAND = '/bin/sh -c "while true; do echo finished; done"'
        c = self.make_container(command=COMMAND)
        c.start()
        self.assertEqual(c.is_running, True)
        self.assertEqual(c.status, BaseContainer.STATUS_RUNNING)
        c.stop()
        self.assertEqual(c.is_running, False)
        self.assertEqual(c.status, BaseContainer.STATUS_STOPPED)

    def test_wait(self):
        COMMAND = '/bin/sh -c "exit 1"'
        c = self.make_container(command=COMMAND)
        c.start()
        self.assertEqual(c.is_running, True)
        status = c.wait()
        self.assertEqual(c.is_running, False)
        self.assertEqual(status, 1)

    def test_logs(self):
        SALT = make_random_salt(5)
        COMMAND = '/bin/sh -c "echo {0}"'.format(SALT)
        c = self.make_container(command=COMMAND)
        c.start()
        c.wait()
        logs = [x for x in c.logs()]
        self.assertEqual(logs, [SALT.encode(encoding='utf-8') + b'\n'])

    def test_attach(self):
        SALT = make_random_salt(5)
        COMMAND = '/bin/sh -c "sleep 1; echo {0}"'.format(SALT)
        c = self.make_container(command=COMMAND)
        c.start()
        logs = [x for x in c.attach()]
        self.assertEqual(logs, [SALT.encode(encoding='utf-8') + b'\n'])

    def test_reinspect(self):
        SALT = make_random_salt(5)
        COMMAND = '/bin/sh -c "echo {0}"'.format(SALT)
        c = self.make_container(command=COMMAND)
        c.start()
        logs = [x for x in c.attach()]
        self.assertEqual(c.is_running, True)
        c.reinspect()
        self.assertEqual(c.is_running, False)

    def test_kill(self):
        COMMAND = '/bin/sh -c "while true; do echo finished; done"'
        c = self.make_container(command=COMMAND)
        c.start()
        c.kill()
        self.assertEqual(c.is_running, False)

    def test_make_container_without_options(self):
        c = self.make_container()
        dc = DockerContainer(self.client, c.id)
        self.assertEqual(c.id, dc.id)

    def test_ports(self):
        PORT = '8000'
        c = self.make_container(
            command='/bin/sh -c "python -m SimpleHTTPServer"',
            ports=[PORT])

        c.start()
        port_map = c.ports()
        self.assertIn(PORT, port_map)
        self.assertEqual(len(port_map[PORT]), 1)
        self.assertEqual(port_map[PORT][0][0], '0.0.0.0')
        self.assertTrue(0 < int(port_map[PORT][0][1]) < 65536)
