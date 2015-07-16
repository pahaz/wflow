from .event import deploy_after_git_receive_pack_listener

__author__ = 'pahaz'


def load(command_manager, event_manager, env):
    event_manager.add_event_listener(
        'git-receive-pack', deploy_after_git_receive_pack_listener
    )
