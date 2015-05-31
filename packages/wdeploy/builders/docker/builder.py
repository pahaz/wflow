from __future__ import unicode_literals, print_function, generators, division

import logging
import time

from ...project_builder import BaseProjectBuilder
from wdeploy.builders.docker import BUILDSTEP_IMAGE, _make_image_name
from wdeploy.builders.docker.options import DOCKER_BUILDSTEP_IMAGE
from wdeploy.builders.docker.runner import DockerProjectRunner
from wdeploy.builders.docker.utils import \
    _create_environment_volumes_ports, create_container, \
    container_start_and_attach, create_docker_client

__author__ = 'pahaz'


class DockerProjectBuilder(BaseProjectBuilder):
    log = logging.getLogger("docker.builder")

    def __init__(self, project_info, options):
        super(DockerProjectBuilder, self).__init__(project_info, options)
        self._client = create_docker_client(options, self.log)
        self._buildstep_image = options.get(
            DOCKER_BUILDSTEP_IMAGE, BUILDSTEP_IMAGE)

    @classmethod
    def make_ProjectBuilder_or_None(cls, project_info, options):
        return cls(project_info, options)

    def make_project_runner(self):
        return DockerProjectRunner(self._info, self._options)

    def build(self, do_on_build_message=None):
        COMMIT_MSG = "build container"
        NEW_IMAGE_NAME = self.make_image_name()
        container = None

        try:
            self.log.info('create new image: {0}'.format(NEW_IMAGE_NAME))

            self.log.debug('starting build process')

            envs, vols, ports = _create_environment_volumes_ports(
                self.info, self.options)

            container = create_container(
                self._client, self._buildstep_image, "/build",
                environment=envs,
                volumes=vols,
                ports=ports,
                log=self.log,
            )

            container_start_and_attach(
                self._client, container, do_on_build_message,
                log=self.log,
            )

            image = self._client.commit(container.id, NEW_IMAGE_NAME,
                                        message=COMMIT_MSG)
            image_id = image['Id']

            self.log.debug('image build: id={0}'.format(image_id))

        finally:
            self.log.debug('cleaning intermediate containers')

            # NOTE: containers with build error not cleaned! clean only correct
            # built containers!

            if container:
                self._client.remove_container(container.id)
                container.invalidate()

            self.log.debug('intermediate containers cleaned')

        # build_path = os.path.join(self.info.builds_path, image_name)
        # execute('docker save -o {0} {1}'.format(build_path, image_name))
        return self.make_project_runner()

    def make_image_name(self):
        return _make_image_name(
            self.info.name,
            time.strftime("%Y.%m.%d.%Hh.%Mm.%Ss")
        )

    def close(self):
        self._client.close()

    def __del__(self):
        self.close()
