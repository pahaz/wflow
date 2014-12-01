from .secure import secure_filename
from .serialize import unpack

__author__ = 'pahaz'


class ParseError(Exception):
    pass


def parse_repo(repo):
    """Parse repo string.

        context = {
                'repo_dir_name': repo,
                'repo_dns': repo,
        }

    :raise ParseError:
    :param repo: string (ex: "/qwer" or "/!nFfwfwW2aw")
    :return: parsed context
    """
    repo = repo.lstrip('/')

    if repo.startswith('!'):
        repo = repo[1:]
        context = unpack(repo)
        if 'repo_dir_name' not in context:
            raise ParseError('unpacked repo don`t contain repo_dir_name')
        if 'repo_dns' not in context:
            raise ParseError('unpacked repo don`t contain repo_dns')
    else:
        context = {
            'repo_dir_name': repo,
            'repo_dns': repo,
        }

    repo_dir_name = context['repo_dir_name']
    if "/" in repo_dir_name:
        raise ParseError('invalid repo_dir_name string "/" unexpected')

    if secure_filename(repo_dir_name) != repo_dir_name:
        raise ParseError('repo_dir_name security problem')

    return context
