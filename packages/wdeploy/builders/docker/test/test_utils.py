from __future__ import unicode_literals, print_function, generators, division
import os
import shutil
import tempfile

from wdeploy.builders.docker.test import BaseDockerContainerTestCase

__author__ = 'pahaz'


class TestDockerCreate(BaseDockerContainerTestCase):
    def test_port_binding(self):
        client = type(self).client

        container = self.make_container(
            command='/bin/sh -c "python -m SimpleHTTPServer"',
            ports=['8000'])

        container.start()
        inspect = client.inspect_container(container.id)
        ports = inspect['NetworkSettings']['Ports']

        self.assertEqual(ports['8000/tcp'][0]['HostIp'], '0.0.0.0')
        self.assertTrue(0 < int(ports['8000/tcp'][0]['HostPort']) < 65536)

    def test_volumes_binding(self):
        client = type(self).client
        TMP_FILENAME = '1.txt'

        tmp_host = tempfile.mkdtemp()
        with open(os.path.join(tmp_host, TMP_FILENAME), 'w') as f:
            f.write('test')

        container = self.make_container(
            command='/bin/sh -c "ls /tmp/test"',
            volumes=["{0}:/tmp/test".format(tmp_host)])

        container.start()
        container.wait()
        inspect = client.inspect_container(container.id)
        logs = container.logs_text().strip()

        self.assertEqual(inspect['Volumes'], {'/tmp/test': tmp_host})
        self.assertEqual(inspect['VolumesRW'], {'/tmp/test': True})
        self.assertEqual(logs, TMP_FILENAME)

        shutil.rmtree(tmp_host)
