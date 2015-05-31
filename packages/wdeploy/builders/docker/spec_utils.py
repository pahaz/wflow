from __future__ import unicode_literals, print_function, generators, division
from collections import namedtuple
import os

from wutil._six import text_type

__author__ = 'pahaz'
VolumeSpec = namedtuple('VolumeSpec', 'host container mode')
PortSpec = namedtuple('PortSpec', 'host_ip host_port port protocol')


def parse_volume_spec(volume_config):
    if not isinstance(volume_config, text_type):
        raise TypeError('invalid volume_config type. volume_config required.')

    parts = volume_config.split(':')
    if len(parts) > 3:
        raise ValueError("Volume {0} has incorrect format, should be "
                         "/host:[/container][:mode]".format(volume_config))

    if len(parts) == 1:
        parts.append(parts[0])

    if len(parts) == 2:
        parts.append('rw')

    host, container, mode = parts
    if mode not in ('rw', 'ro'):
        raise ValueError("Volume {0} has invalid mode ({1}), should be "
                         "one of: rw, ro.".format(volume_config, mode))

    if not os.path.isabs(host):
        raise ValueError("Volume {0} has a not absolute path ({1})."
                         .format(volume_config, host))

    if not os.path.isabs(container):
        raise ValueError("Volume {0} has a not absolute path ({1})."
                         .format(volume_config, container))

    return VolumeSpec(host, container, mode)


def parse_port_spec(port_config):
    if not isinstance(port_config, (int, text_type)):
        raise TypeError('invalid port_config type. int or text_type required.')

    parts = str(port_config).split(':')
    if not 1 <= len(parts) <= 3:
        raise ValueError('Invalid port "%s", should be '
                         '[[host_ip:]host_port:]port[/protocol]'
                         .format(port_config))

    if len(parts) == 1:
        internal_port, = parts
        host_ip, host_port = '', ''
    elif len(parts) == 2:
        host_port, internal_port = parts
        host_ip = ''
    else:
        host_ip, host_port, internal_port = parts

    if '/' in internal_port:
        port, protocol = internal_port.split('/')
    else:
        port, protocol = internal_port, 'tcp'

    # TODO: validate host_ip, host_port, protocol
    try:
        i_port = int(port)
        if not 0 < i_port < 65536:
            raise ValueError()
    except ValueError:
        raise ValueError('Invalid port {0}, should be '
                         '0 < intager number < 65536'.format(port_config))

    return PortSpec(host_ip, host_port, port, protocol)


def convert_volumes_specs_to_binds(volumes_specs):
    return {v.host: {'bind': v.container, 'ro': v.mode == 'ro'}
            for v in volumes_specs}


def convert_ports_specs_to_port_binds(ports_specs):
    return {p.port + '/' + p.protocol: (p.host_ip, p.host_port)
            for p in ports_specs}
