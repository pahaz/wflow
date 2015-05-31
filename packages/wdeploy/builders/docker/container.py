from __future__ import unicode_literals, print_function, generators, division
from collections import namedtuple
import logging
from pprint import pprint

import dockerpty

from wdeploy.builders.docker import _parse_container_name, _clean_image_name, \
    _clean_container_name
from wdeploy.container import BaseContainer
from wdeploy.project_runner import WorkWithRemovedContainerError
from wutil.mixin import InvalidateMixin

__author__ = 'pahaz'
DockerContainerOptions = namedtuple(
    'DockerContainerOptions', 'binds ports_binds'
)
default_docker_container_options = DockerContainerOptions(
    binds=None, ports_binds=None
)
default_logger = logging.getLogger("docker.container")


class DockerContainer(BaseContainer, InvalidateMixin):
    invalid_object_error = WorkWithRemovedContainerError('Invalid container')

    def reinspect(self):
        # {'State': {'Pid': 0, 'OOMKilled': False, 'Paused': False,
        # 'Running': False, 'FinishedAt': '0001-01-01T00:00:00Z',
        #            'Restarting': False, 'Error': '',
        #            'StartedAt': '0001-01-01T00:00:00Z', 'ExitCode': 0},
        #  'Config': {'Env': ['PORT=5000',
        #                     'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'],
        #             'Hostname': 'ac03ee94998f', 'Entrypoint': None,
        #             'PortSpecs': None, 'Memory': 0, 'OnBuild': None,
        #             'OpenStdin': False, 'MacAddress': '', 'Cpuset': '',
        #             'User': '', 'CpuShares': 0, 'AttachStdout': False,
        #             'NetworkDisabled': False, 'WorkingDir': '/',
        #             'Cmd': ['/bin/bash', '-c', '/start web'],
        #             'StdinOnce': False, 'AttachStdin': False, 'MemorySwap': 0,
        #             'Volumes': {'/tmp/app': {},
        #                         '/home/wflow/n4/DATA:/data': {}}, 'Tty': False,
        #             'AttachStderr': False, 'Domainname': '',
        #             'Image': 'build__n4__2015.05.15.19H.24M.20S',
        #             'ExposedPorts': {'5000/tcp': {}}}, 'HostsPath': '',
        #  'Args': ['-c', '/start web'], 'Driver': 'aufs',
        #  'ExecDriver': 'native-0.2', 'Path': '/bin/bash', 'HostnamePath': '',
        #  'VolumesRW': {'/tmp/app': True, '/home/wflow/n4/DATA:/data': True},
        #  'RestartCount': 0,
        #  'Name': '/build__n4__2015.05.15.19H.24M.20S__web__1',
        #  'Created': '2015-05-15T19:24:21.833160233Z', 'ResolvConfPath': '',
        #  'Volumes': {
        #  '/tmp/app': '/var/lib/docker/vfs/dir/49d61c54efa6603db1869e550b191941c577677f2c9a7da89c33a004ec5c99db',
        #  '/home/wflow/n4/DATA:/data': '/var/lib/docker/vfs/dir/f56a931198a703cbc9a68ac6709a0fcecebaed01ae4e394679a6d2f4dad44f76'},
        #  'ExecIDs': None, 'ProcessLabel': '',
        #  'NetworkSettings': {'Bridge': '', 'GlobalIPv6PrefixLen': 0,
        #                      'LinkLocalIPv6Address': '',
        #                      'GlobalIPv6Address': '', 'IPv6Gateway': '',
        #                      'PortMapping': None, 'IPPrefixLen': 0,
        #                      'LinkLocalIPv6PrefixLen': 0, 'MacAddress': '',
        #                      'IPAddress': '', 'Gateway': '', 'Ports': None},
        #  'AppArmorProfile': '',
        #  'Image': '120fade3f7893b945f4c0d8410309c0d2622c54e39c9f7c171d0e4472973d0bc',
        #  'HostConfig': {'CapDrop': None, 'PortBindings': None,
        #                 'NetworkMode': '', 'SecurityOpt': None, 'Links': None,
        #                 'IpcMode': '', 'LxcConf': None, 'ContainerIDFile': '',
        #                 'Devices': None, 'CapAdd': None, 'Binds': None,
        #                 'RestartPolicy': {'MaximumRetryCount': 0, 'Name': ''},
        #                 'PublishAllPorts': False, 'Dns': None, 'PidMode': '',
        #                 'ExtraHosts': None, 'DnsSearch': None,
        #                 'Privileged': False, 'VolumesFrom': None,
        #                 'ReadonlyRootfs': False},
        #  'Id': 'ac03ee94998fb09533c05c1a38e8c5714509eb4d7561c09dad582d3696713cbf',
        #  'MountLabel': ''}
        self.log.debug('{0} reinspect'.format(self.name))
        self._container = self._client.inspect_container(self.id)

    def __init__(self, client, container, options=None, log=None):
        # TODO: check if client is closed ??
        if options and not isinstance(options, DockerContainerOptions):
            raise TypeError('Invalid options type. DockerContainerOptions '
                            'required.')
        self._client = client
        self._container = client.inspect_container(container)
        self._options = options or default_docker_container_options
        self.log = log or default_logger

    def _debug(self):
        pprint(self._container)

    @property
    def id(self):
        return self._container['Id']

    @property
    def name(self):
        name = self._container['Name']
        c_name = _clean_container_name(name)
        return c_name or name

    @property
    def image(self):
        image = self._container['Config']['Image']
        c_image = _clean_image_name(image)
        return c_image or image

    @property
    def status(self):
        return self.STATUS_RUNNING if self._container['State']['Running'] \
            else self.STATUS_STOPPED

    @property
    def is_detached(self):
        attach_stdout = self._container['Config']['AttachStdout']
        attach_stderr = self._container['Config']['AttachStderr']
        detach = not (attach_stderr or attach_stdout)
        return detach

    @property
    def is_interactive(self):
        attach_stdin = self._container['Config']['AttachStdin']
        open_stdin = self._container['Config']['OpenStdin']
        interactive = attach_stdin and open_stdin
        return interactive

    @property
    def index(self):
        _, _, index = _parse_container_name(self.name)
        return index

    @property
    def type(self):
        _, process_type, _ = _parse_container_name(self.name)
        return process_type

    def rename(self, new_name):
        self.log.debug('{0} rename to {1}'.format(self.name, new_name))
        self._client.rename(self.id, new_name)
        self.reinspect()

    def start(self):
        binds = self._options.binds
        ports_binds = self._options.ports_binds
        detached_msg = 'detached' if self.is_detached else ''
        self.log.info('{0} start {1}'.format(self.name, detached_msg))
        self.log.debug('{0} start options: binds: {1}, ports_binds: {2}'
                       .format(self.name, binds, ports_binds))
        if self.is_detached:
            self._client.start(self.id, binds=binds, port_bindings=ports_binds)
        else:
            interactive = self.is_interactive
            pt = dockerpty.PseudoTerminal(self._client, self.id, interactive)
            pt.start(binds=binds, port_bindings=ports_binds)
        self.reinspect()

    def stop(self):
        self.log.info('{0} stop'.format(self.name))
        self._client.stop(self.id)
        retcode = self.wait()
        # self.reinspect()
        return retcode

    def kill(self, signal=None):
        self.log.info('{0} kill'.format(self.name))
        self._client.kill(self.id, signal)
        retcode = self.wait()
        # self.reinspect()
        return retcode

    def wait(self):
        self.log.info('{0} wait'.format(self.name))
        retcode = self._client.wait(self.id)
        self.reinspect()
        return retcode

    def attach(self, logs=False):
        self.log.info('{0} attach logs={1}'.format(self.name, logs))
        stream = self._client.attach(self.id, stdout=True, stderr=True,
                                     stream=True, logs=logs)
        self.reinspect()
        return stream

    def logs(self, tail='all'):
        self.log.info('{0} logs'.format(self.name))
        stream = self._client.logs(self.id, stdout=True, stderr=True,
                                   stream=True, tail=tail)
        self.reinspect()
        return stream

    def logs_text(self, tail='all', encoding='utf-8'):
        logs_stream = self.logs(tail)
        text = ''.join(x.decode(encoding) for x in logs_stream)
        logs_stream.close()
        return text

    def ports(self, proto='tcp'):
        # {'8000/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '49170'}]}
        ports = self._container['NetworkSettings']['Ports']
        result = {}
        for port, port_maps in ports.items():
            port, _proto = port.split('/') if '/' in port else (port, 'tcp')
            if _proto != proto:
                continue
            print(port, port_maps, type(port_maps), _proto)
            result[port] = [(v['HostIp'], v['HostPort']) for v in port_maps]
        return result
