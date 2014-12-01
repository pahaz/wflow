from __future__ import unicode_literals
import base64
import gzip
try:
    import simplejson as json
except ImportError:
    import json

__author__ = 'pahaz'


def pack(dict_):
    return base64.b64encode(gzip.compress(
        json.dumps(dict_).encode('utf-8')
    ), b'-+')


def unpack(data_):
    return json.loads(gzip.decompress(
        base64.b64decode(data_, b'-+')
    ).decode('utf-8'))


if __name__ == "__main__":
    d = {
        'some': [1, 2, 3, "qwппe'"],
        'one': 2,
        'k': "awdawdwd.ei, awdad*.awdawdu"
    }
    print(json.dumps(d))
    print(json.dumps(d).encode('utf-8'))
    print(gzip.compress(json.dumps(d).encode('utf-8')))
    print(base64.b32encode(gzip.compress(json.dumps(d).encode('utf-8'))))
    z = base64.b32encode(gzip.compress(json.dumps(d).encode('utf-8')))
    print(base64.b32decode(z))
    print(gzip.decompress(base64.b32decode(z)))
    print(json.loads(gzip.decompress(base64.b32decode(z)).decode('utf-8')))
    print(pack(d))
    print(unpack(pack(d))['some'][3] == d['some'][3])
