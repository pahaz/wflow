from __future__ import unicode_literals, print_function, generators, division
import unittest

from wdeploy.builders.docker.spec_utils import VolumeSpec, parse_volume_spec, \
    convert_volumes_specs_to_binds, PortSpec, parse_port_spec, \
    convert_ports_specs_to_port_binds

__author__ = 'pahaz'


class TestVolumeSpecParsing(unittest.TestCase):
    def make_volume_spec(self, host='', container='', mode='rw'):
        return VolumeSpec(host, container, mode)

    def test_parse_volume_spec(self):
        VOLUME = '/qwe:/tmp'
        RESULT = self.make_volume_spec('/qwe', '/tmp', 'rw')
        r = parse_volume_spec(VOLUME)
        self.assertEqual(r, RESULT)

    def test_parse_volume_spec_with_ro_mode(self):
        VOLUME = '/qwe:/tmp:ro'
        RESULT = self.make_volume_spec('/qwe', '/tmp', 'ro')
        r = parse_volume_spec(VOLUME)
        self.assertEqual(r, RESULT)

    def test_parse_volume_spec_with_only_host_path(self):
        VOLUME = '/qwe'
        RESULT = self.make_volume_spec('/qwe', '/qwe', 'rw')
        r = parse_volume_spec(VOLUME)
        self.assertEqual(r, RESULT)

    def test_convert_volumes_specs_to_binds(self):
        VOLUME_SPEC = self.make_volume_spec('/qwe', '/tmp', 'ro')
        RESULT = {'/qwe': {'bind': '/tmp', 'ro': True}}
        binds = convert_volumes_specs_to_binds([VOLUME_SPEC])
        self.assertEqual(binds, RESULT)


class TestPortsSpecParsing(unittest.TestCase):
    def make_port_spec(self, host_ip='', host_port='', port='5000',
                       protocol='tcp'):
        return PortSpec(host_ip, host_port, port, protocol)

    def test_parse_port_spec(self):
        PORT = '5000'
        RESULT = self.make_port_spec('', '', '5000', 'tcp')
        r = parse_port_spec(PORT)
        self.assertEqual(r, RESULT)

    def test_parse_port_spec_with_host_port(self):
        PORT = '4999:5000'
        RESULT = self.make_port_spec('', '4999', '5000', 'tcp')
        r = parse_port_spec(PORT)
        self.assertEqual(r, RESULT)

    def test_parse_port_spec_with_host_port_and_ip(self):
        PORT = '127.0.0.1:4999:5000'
        RESULT = self.make_port_spec('127.0.0.1', '4999', '5000', 'tcp')
        r = parse_port_spec(PORT)
        self.assertEqual(r, RESULT)

    def test_parse_port_spec_with_host_ip_and_empty_port(self):
        PORT = '127.0.0.1::5000'
        RESULT = self.make_port_spec('127.0.0.1', '', '5000', 'tcp')
        r = parse_port_spec(PORT)
        self.assertEqual(r, RESULT)

    def test_parse_port_spec_with_empty_port_raise_error(self):
        PORT = ''
        with self.assertRaises(ValueError):
            parse_port_spec(PORT)

    def test_parse_int_port(self):
        PORT = 5000
        RESULT = self.make_port_spec('', '', '5000', 'tcp')
        r = parse_port_spec(PORT)
        self.assertEqual(r, RESULT)

    def test_convert_ports_specs_to_port_binds(self):
        PORT_SPCK = self.make_port_spec('127.0.0.1', '65000', '5000', 'tcp')
        RESULT = {'5000/tcp': ('127.0.0.1', '65000')}
        r = convert_ports_specs_to_port_binds([PORT_SPCK])
        self.assertEqual(r, RESULT)
