from __future__ import unicode_literals, print_function, generators, division
import logging

from wdeploy.builders.docker import _make_process_command, \
    _make_container_name, \
    _parse_image_name, _clean_image_name, check_image_name, \
    _clean_container_name, _parse_container_name
from wdeploy.builders.docker.container import DockerContainer
from wdeploy.builders.docker.utils import create_container, \
    _create_environment_volumes_ports, create_docker_client
from wdeploy.project_runner import BaseProjectRunner, LAST_IMAGE, \
    NoImagesError

from wdeploy.validators import check_process_type, check_index

__author__ = 'pahaz'


class DockerProjectRunner(BaseProjectRunner):
    log = logging.getLogger("docker.runner")

    def __init__(self, project_info, options):
        super(DockerProjectRunner, self).__init__(project_info, options)
        self._client = create_docker_client(options, self.log)
        self.discover()

    @property
    def containers(self):
        return self._containers

    @property
    def images(self):
        return self._images

    @property
    def latest_image(self):
        return self._latest_image

    def create(self, process_type, index, image=LAST_IMAGE, interactive=False):
        if image == LAST_IMAGE:
            image = self._latest_image

        check_process_type(process_type)
        check_index(index)
        check_image_name(image)
        command = _make_process_command(process_type)
        container_name = _make_container_name(image, process_type, index)

        self.log.info(
            'create new container: name={0}, command={1}, image={2}{3}'.format(
                container_name, command, image,
                ', interactive' if interactive else ''
            )
        )

        kwargs = dict(stdin_open=True, tty=True, detach=False) if interactive \
            else dict(detach=True)

        environment, volumes, ports = _create_environment_volumes_ports(
            self.info, self.options, runtime=True)
        container = create_container(
            self._client, image, command, name=container_name,
            environment=environment, volumes=volumes, ports=ports,
            log=self.log,
            **kwargs
        )

        self._append_container(container)
        return container

    def remove(self, container):
        if not isinstance(container, DockerContainer):
            raise TypeError('Invalid container type')
        self.log.info('remove {0} container'.format(container.name))
        container.stop()
        container.wait()
        self._client.remove_container(container.id)
        self._remove_container(container)
        container.invalidate()

    def scale(self, process_type, count=1, image=LAST_IMAGE):
        if image == LAST_IMAGE:
            image = self._latest_image

        check_process_type(process_type)
        if not isinstance(count, int) or count <= 0:
            raise TypeError('Invalid count. 0 < count required')
        check_image_name(image)

        found_indexes = dict()
        required_indexes = set(range(1, count + 1))

        self.log.info('containers scale {0} count={1}, image={2}'
                      .format(process_type, count, image))

        for container in self.containers:
            type = container.type
            index = container.index
            if index is None or type is None or type != process_type:
                continue

            if index in found_indexes:
                self.log.error("containers scale: found a two containers with "
                               "the same index! Remove one!")
                self.remove(container)
                continue

            found_indexes[index] = container

        for index in required_indexes:
            if index in found_indexes:
                self.log.debug('containers scale: {0} {1} - exist'
                               .format(process_type, index))
            else:
                self.log.debug('containers scale: {0} {1} - create'
                               .format(process_type, index))
                container = self.create(process_type, index, image=image)
                found_indexes[index] = container

        unnecessary_indexes = set(found_indexes.keys()) - required_indexes
        for index in unnecessary_indexes:
            self.log.debug('containers scale: {0} {1} - remove'
                           .format(process_type, index))
            container = found_indexes[index]
            self.remove(container)

        return [found_indexes[i] for i in required_indexes]

    def discover(self):
        self.log.info('discover images and containers')
        self._containers = tuple()
        self._images = tuple()
        self._discover_containers()
        self._discover_images()
        if self._latest_image is None:
            raise NoImagesError
        images_string = ', '.join(image for image in self._images)
        self.log.debug('discovered images: {0} (latest: {1})'
                       .format(images_string, self._latest_image))
        containers_string = ', '.join(c.name for c in self._containers)
        self.log.debug('discovered containers: {0}'.format(containers_string))

    def close(self):
        self._client.close()

    def __del__(self):
        self.close()

    def _append_container(self, container):
        if not isinstance(container, DockerContainer):
            raise TypeError('Invalid container type')
        self._containers = self._containers + (container,)

    def _remove_container(self, container):
        if not isinstance(container, DockerContainer):
            raise TypeError('Invalid container type')
        i = self._containers.index(container)
        self._containers = self._containers[:i] + self._containers[i + 1:]

    def _discover_containers(self):
        containers = []
        for container in self._client.containers(all=True, trunc=False):
            # {'Status': 'Exited (0) 4 hours ago', 'Created': 1430907716, 'Image': 'progrium/buildstep:latest', 'Ports': [], 'Command': "/bin/bash -c 'mkdir -p /app && tar -xC /app'", 'Names': ['/sad_archimedes'], 'SizeRw': 15971, 'SizeRootFs': 0, 'Id': 'a4b0ee8671898cf3973eff323a906163e0e4a882589dcffad8772fd39a7e9b53'}
            # {'Status': '', 'Created': 1430907811, 'Image': 'build__static__2015.04.28-17H-37M-24S:latest', 'Ports': [], 'Command': "/bin/bash -c '/start web'", 'Names': ['/build__static__2015.04.28-17H-37M-24S__web__1'], 'SizeRw': 0, 'SizeRootFs': 0, 'Id': 'befa5f7aff8dc5a914a22b6cb86f44cd47f7979a0b112e8d5820c14ad54393a4'}
            # {'Status': '', 'Created': 1431944647, 'Image': 'f77242520486', 'Ports': [], 'Command': "/bin/bash -c '/start scale-1-then-2'", 'Names': ['/build__test-runner__1__scale-1-then-2__1'], 'Id': '2f9d67915bea7101b0375d7c19b4013c8af79e93e3e08255abe4512ed46f43e6'}
            # If you create a new image with the same name,
            # in the field 'Image' is an incorrect value.
            for name in container['Names']:
                container_name = _clean_container_name(name)
                if not container_name:
                    continue

                image_name, process_type, index = _parse_container_name(name)
                project_name, version = _parse_image_name(image_name)
                if project_name != self.info.name:
                    continue

                wrapped_container = DockerContainer(self._client, container)
                containers.append(wrapped_container)
                break

        self._containers = tuple(containers)

    def _discover_images(self):
        images_set = set()
        for image in self._client.images():
            # {'Created': 1426871427, 'VirtualSize': 866374967, 'ParentId': '', 'RepoTags': ['progrium/buildstep:latest'], 'Id': '6ac26ca9d0316208049ef0017e6382ceea7e2448befae2342964b8a368073a4c', 'Size': 866374967}
            # {'Created': 1430908285, 'VirtualSize': 1086964550, 'ParentId': 'dd3209d84324f50a1800e94ab97c2392e082876743538d87a07897651764e837', 'RepoTags': ['build__test3__2015.05.06-10H-29M-14S:latest'], 'Id': '2549971a7c0bfcf22e640f00a353742df4d2b0542f592923c03800d0897eea90', 'Size': 220573605}
            # {'Created': 1430907717, 'VirtualSize': 866390938, 'ParentId': '6ac26ca9d0316208049ef0017e6382ceea7e2448befae2342964b8a368073a4c', 'RepoTags': ['<none>:<none>'], 'Id': '1f5e80b636e85e6499b6a5d6f625bce662536545fb2f9111a1171d4983444fe8', 'Size': 15971}
            # self.log.debug(image)
            for tag in image['RepoTags']:
                image_name = _clean_image_name(tag)
                if not image_name:
                    continue

                project_name, version = _parse_image_name(image_name)
                if project_name != self.info.name:
                    continue

                images_set.add(image_name)
                break

        self._images = images = tuple(sorted(images_set))
        self._latest_image = images[-1] if len(images) else None
