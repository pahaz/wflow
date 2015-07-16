from __future__ import print_function
import logging
import os

from wdeploy.core import deploy, make_runner
from wdeploy.project_builder_loader import ProjectBuilderNotFoundError
from wdeploy.project_info import ProjectInfo
from wutil.env_keys import PLATFORM_DATA_PATH_KEY
from wutil.env_keys import REPO_DIR_NAME_KEY, DNS_NAME_KEY
from wutil.execute3 import execute


__author__ = 'pahaz'
__plugin_root__ = os.path.dirname(__file__)
log = logging.getLogger('docker_buildstep_plugin')


def run(command, cwd, do_log=lambda x: log.debug(x.decode().strip())):
    log.debug("run '{0}'".format(command))
    execute(
        command,
        cwd=cwd,
        stderr_to_stdout=True,
        do_on_read_stdout=do_log,
        check_return_code_and_raise_error=False,
    )


def deploy_after_git_receive_pack_listener(manager, env):
    log.debug('deploy_after_git_receive_pack_listener env={0}'
              .format(env.as_dict()))
    dns_name = env[DNS_NAME_KEY]
    repo_dir_name = env[REPO_DIR_NAME_KEY]
    repos_root_path = env[PLATFORM_DATA_PATH_KEY]
    repo_local_path = os.path.join(repos_root_path, repo_dir_name)
    repo_source_copy_path = os.path.join(repo_local_path, "SOURCE")

    log.debug('deploy repo {0}'
              .format(repo_local_path))
    log.warning("----> deploy")

    log.debug('update repo/SOURCE dir')

    if not os.path.exists(repo_source_copy_path):
        run("git clone . SOURCE", repo_local_path)
    else:
        run("git stash", repo_source_copy_path)
        run("git pull --rebase -X theirs --all", repo_source_copy_path)
        # you can show stash list and make patches
        #'git stash show -p' # same as git stash show -p stash@{0}
        #'git stash list'

    environ = {}
    services = []
    settings = {}
    info = ProjectInfo(repos_root_path, repo_dir_name, environ, services)

    do_on_build_message = lambda x: log.warning(x.decode().rstrip())
    try:
        runner = deploy(info, settings, do_on_build_message)
        # runner = make_runner(info, settings)
    except ProjectBuilderNotFoundError:
        log.warning('----> Can`t find deployer for this project :(')
        return

    log.warning('----> {0} - created'.format(runner.latest_image))

    process_type = 'web'
    log.warning('----> scale({type}) to 1 container'.format(type=process_type))
    containers = runner.scale(process_type, count=1)
    runner.close()

    # TODO: normal work with ports!!

    export_ports = []
    for x in containers:
        x.start()
        ports = x.ports()
        log.info("ports: {0}".format(ports))
        export_addrs = [addr for k, p_map in ports.items() for addr in p_map]
        export_ports.extend(export_addrs)

    if len(export_ports):
        last_port = export_ports[-1][1]
    else:
        log.error("no public port")
        return 2

    manager.trigger_event('deploy', env, {
        # PLATFORM_DATA_PATH_KEY: repos_root_path,
        'APP': repo_dir_name,
        'PORT': last_port,
    })

