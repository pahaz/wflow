from __future__ import unicode_literals, print_function, generators, division
import logging
import sys
from docker import Client

import docker.errors
from wdeploy.builders.docker import DOCKER_CLIENT_BASE_URL, \
    DOCKER_CLIENT_VERSION

from wdeploy.builders.docker.container import DockerContainerOptions, \
    DockerContainer
from wdeploy.builders.docker.options import DOCKER_BASE_URL, DOCKER_VERSION
from wdeploy.builders.docker.spec_utils import parse_volume_spec, \
    convert_volumes_specs_to_binds, parse_port_spec, \
    convert_ports_specs_to_port_binds
from wdeploy.builders.docker.stream_utils import stream_output

__author__ = 'pahaz'
ENV_APP_PATH_KEY = 'APP_PATH'
ENV_ENV_PATH_KEY = 'ENV_PATH'
ENV_BUILD_PATH_KEY = 'BUILD_PATH'
ENV_CACHE_PATH_KEY = 'CACHE_PATH'
ENV_IMPORT_PATH_KEY = 'IMPORT_PATH'
ENV_BUILDPACK_PATH_KEY = 'BUILDPACK_PATH'
ENV_DATA_PATH_KEY = 'DATA_PATH'
ENV_PORT_KEY = 'PORT'
default_logger = logging.getLogger("docker.utils")


class RunContainerError(Exception):
    pass


def remove_exit_containers(client):
    for c in client.containers(all=True):
        status = c['Status']
        id_ = c['Id']
        if not status or status.startswith('Exit'):
            client.remove_container(id_)


def remove_none_images(client):
    for i in client.images(all=True):
        tags = i['RepoTags']
        id_ = i['Id']
        try:
            if any('<none>' in t for t in tags):
                client.remove_image(id_, force=True)
        except docker.errors.APIError as e:
            pass


def create_container(client, image_id, command, environment=None,
                     volumes=None, ports=None, name=None,
                     stdin_open=False, tty=False, detach=True,
                     log=None):
    """
    :return: DockerContainer
    """
    log = log if log else default_logger

    log_msg = 'create new container: environment: {0} volumes: {1} ' \
              'ports: {2}'.format(environment, volumes, ports)
    log.debug(log_msg)

    if volumes is None:
        volumes = []
    if environment is None:
        environment = {}
    if ports is None:
        ports = []

    cmd = _docker_run_command(image_id, command, environment, volumes, ports,
                              name, stdin_open, tty, detach)
    log.debug('debug docker command: ' + cmd)

    volumes_specs = [parse_volume_spec(v) for v in volumes]
    binds = convert_volumes_specs_to_binds(volumes_specs)
    internal_volumes = [v.container for v in volumes_specs]

    ports_specs = [parse_port_spec(p) for p in ports]
    port_binds = convert_ports_specs_to_port_binds(ports_specs)
    internal_ports = [(p.port, p.protocol) for p in ports_specs]

    kwargs = dict(
        image=image_id,
        command=command,
        environment=environment,
        volumes=internal_volumes,
        name=name,
        ports=internal_ports,
        stdin_open=stdin_open, tty=tty, detach=detach
    )

    try:
        container = client.create_container(**kwargs)
    except docker.errors.APIError as e:
        if e.response.status_code == 404 and e.explanation and \
                        'No such image' in str(e.explanation):
            log_msg = 'Container image not exists. Try pulling ... ' \
                      '(docker pull {0})'.format(image_id)
            log.warning(log_msg)

            output = client.pull(image_id, stream=True)
            stream_output(output, sys.stderr)
            container = client.create_container(**kwargs)
        else:
            raise

    id = container['Id']
    warnings = container['Warnings']
    log.info('new container created: id={0}'.format(id))

    if warnings:
        log.warning('new container warnings: {0}, id={1}'.format(warnings, id))

    options = DockerContainerOptions(binds=binds, ports_binds=port_binds)
    return DockerContainer(client, container['Id'], options)


def container_start_and_attach(client, container, do_on_message,
                               log=None, raise_if_bad_retcode=True):
    log = log if log else default_logger
    if not isinstance(container, DockerContainer):
        raise TypeError('Invalid container type. DockerContainer required.')

    log.info('start container: id={0}'.format(container.id))
    container.start()

    if container.is_detached:
        log.info('attach container: id={0}'.format(container.id))

        stream = container.attach(logs=True)
        try:
            if do_on_message and callable(do_on_message):
                for x in stream:
                    log.debug('container message: {0}'.format(x))
                    do_on_message(x)
        except Exception as e:
            e_msg = 'do_on_message raise error: {0}'.format(e)
            log.error(e_msg)
            log.debug(e_msg, exc_info=True)
            raise
        finally:
            stream.close()

    retcode = container.wait()
    if retcode != 0:
        e_msg = 'container retcode error #{0}'.format(retcode)
        log.error(e_msg)
        if raise_if_bad_retcode:
            raise RunContainerError(e_msg)
    return retcode


def _create_environment_volumes_ports(info, options, runtime=False, log=None):
    log = log if log else default_logger
    # TODO: refactor this! take default options from options
    # P5000 = '5000'
    # DEFAULT_PORT = options.get('DOCKER_CONTAINER_DEFAULT_PORT', P5000)
    # DEFAULT_PORT = str(DEFAULT_PORT)
    # try:
    #     check_port(DEFAULT_PORT)
    # except ValidationError:
    #     if log:
    #         log.debug('invalid DEFAULT_PORT value! Use default {0}'
    #                   .format(P5000))
    #
    # environment = {'PORT': DEFAULT_PORT}
    # environment.update(self.info.environment)
    #
    # try:
    #     check_port(environment['PORT'])
    # except ValidationError:
    #     self.log.warning('       !     WARNING: invalid $PORT value! '
    #                      'Use default {0}'.format(DEFAULT_PORT))
    # return environment
    #

    # APP_PATH=/app                    # Application path during runtime
    # ENV_PATH=/tmp/env                # Path to files for base environment
    # BUILD_PATH=/tmp/build            # Working directory during builds
    # CACHE_PATH=/tmp/cache            # Buildpack cache location
    # IMPORT_PATH=/tmp/app             # Mounted path to copy to app path
    # BUILDPACK_PATH=/tmp/buildpacks   # Path to installed buildpacks

    # DATA_PATH=/data                  # Application media data, like cache

    environment = {
        ENV_DATA_PATH_KEY: '/data',
        ENV_APP_PATH_KEY: '/app',
        ENV_ENV_PATH_KEY: '/app/.profile.d',
        ENV_BUILD_PATH_KEY: '/tmp/build',
        ENV_CACHE_PATH_KEY: '/tmp/cache',
        ENV_IMPORT_PATH_KEY: '/tmp/app',
        ENV_BUILDPACK_PATH_KEY: '/tmp/buildpacks',
        ENV_PORT_KEY: '5000',
        # 'TRACE': '1',
        'DOCKER_BUILD': '1',
        'USER': 'root',  # TODO: fix it! (now required for python-buildpack)
        # see: https://github.com/heroku/heroku-buildpack-python/issues/224
    }

    environment.update(info.environment)

    CACHE_PATH = environment[ENV_CACHE_PATH_KEY]
    IMPORT_PATH = environment[ENV_IMPORT_PATH_KEY]
    DATA_PATH = environment[ENV_DATA_PATH_KEY]
    PORT = environment[ENV_PORT_KEY]

    volumes = []

    if runtime:
        volumes.append('{0}:{1}:rw'.format(info.data_path, DATA_PATH))
    else:
        volumes.append('{0}:{1}:ro'.format(info.source_path, IMPORT_PATH))
        volumes.append('{0}:{1}:rw'.format(info.cache_path, CACHE_PATH))

    ports = [
        PORT,
    ]

    return environment, volumes, ports


def _docker_run_command(image, command, environment=None,
                        volumes=None, ports=None, name=None,
                        stdin_open=False, tty=False, detach=True):
    if volumes is None:
        volumes = []
    if environment is None:
        environment = {}
    if ports is None:
        ports = []

    e = ' '.join('-e "{0}={1}"'.format(k, v) for k, v in environment.items())
    v = ' '.join('-v "{0}"'.format(v) for v in volumes)
    p = ' '.join('-p "{0}"'.format(p) for p in ports)
    docker_run = 'docker run {v} {e} {p} '.format(e=e, v=v, p=p)
    if name:
        docker_run += '--name="{0}" '.format(name)
    if stdin_open:
        docker_run += '-i '
    if detach:
        docker_run += '-d '
    if tty:
        docker_run += '-t '
    docker_run += "{image} {command}".format(image=image, command=command)
    return docker_run


def create_docker_client(options=None, log=None):
    log = log if log else default_logger
    options = options if options else {}
    base_url = options.get(DOCKER_BASE_URL, DOCKER_CLIENT_BASE_URL)
    version = options.get(DOCKER_VERSION, DOCKER_CLIENT_VERSION)
    log.debug('client init: base_url={0}, version={1}'
              .format(base_url, version))

    try:
        client = Client(base_url=base_url, version=version)
    except docker.errors.DockerException as e:
        log.error('client init error: {0}'.format(e))
        raise
    return client
