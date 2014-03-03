import os
import tarfile
import tempfile
import hashlib
import subprocess
import pipes

from pyramid.response import FileIter
from pyramid.view import view_config

from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPForbidden,
)

@view_config(route_name='index', renderer='index.mako')
def index(request):
    def build_index(path):
        index  = []
        prefix = len(path)

        for root, dirs, files in os.walk(path):
            for file in files:
                path = os.path.join(root, file)

                with open(path, 'rb') as fp:
                    checksum = hash_file(fp)

                index.append({
                    'path':     path[1:][prefix:],
                    'checksum': checksum,
                })

        return index

    return {
        'index': build_index(request.registry.settings['repo.path']),
    }

@view_config(route_name='packages', renderer='index.mako')
def packages(request):
    def build_index(path):
        index  = []
        prefix = len(path)

        for package in os.listdir(path):
            path     = os.path.join(path, package)
            checksum = hash_directory(path)

            index.append({
                'path':     path[1:][prefix:],
                'checksum': checksum,
            })

        return index

    return {
        'index': build_index(request.registry.settings['repo.path']),
    }

@view_config(route_name='download')
def download(request):
    package   = request.matchdict['package']
    repo_path = request.registry.settings['repo.path']
    file_path = os.path.join(repo_path, package)
    file_path = os.path.abspath(file_path)

    if not file_path.startswith(repo_path):
        raise HTTPForbidden()

    fp = tempfile.NamedTemporaryFile('w+b', dir='/tmp', delete=True)

    with tarfile.open(fileobj=fp, mode='w:gz') as tar:
        tar.add(file_path, arcname='')

    fp.seek(0)

    checksum = hash_file(fp)

    fp.seek(0)

    response                       = request.response
    response.content_type          = 'application/x-gzip'
    response.content_disposition   = 'attachment; filename={}.tar.gz'.format(package)
    response.app_iter              = FileIter(fp)
    response.headers['X-Checksum'] = checksum

    return response

def hash_file(fp, blocksize=65536):
    """ Produces an MD5 hash for the open file pointer ``fp`` """

    hasher = hashlib.md5()
    buf    = fp.read(blocksize)

    while len(buf) > 0:
        hasher.update(buf)

        buf = fp.read(blocksize)

    return hasher.hexdigest()

def hash_directory(path):
    """ Return an MD5 hash of the given ``path`` """

    # can't beat the shell
    return subprocess.check_output("find '{}' -type f | xargs md5sum | cut -d' ' -f1 | sort | md5sum | cut -d' ' -f1".format(pipes.quote(path)), shell=True).strip()
