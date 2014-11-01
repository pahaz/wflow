__author__ = 'pahaz'


def read_content(path):
    with open(path) as f:
        content = f.read().strip()
    return content


def write_content(path, content):
    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
