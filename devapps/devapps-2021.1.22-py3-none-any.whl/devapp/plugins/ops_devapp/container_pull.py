#!/usr/bin/env python
"""
Pulling Container Filesystems from Registries.

dpull: Pull oci image layers from an oci registry.
This is a working literal translation of the jq based moby-download frozen image tool.
"""
# Could be done far smaller.
from devapp import gevent_patched
import hashlib
import json
import os
import shutil
from copy import deepcopy
from functools import partial

import requests
from devapp.app import FLG, app, run_app


class Flags:
    autoshort = ''

    class dir:
        n = 'Target dir'
        d = './images'

    class repo:
        n = 'Examples: dockerio://alpine:latest (dockerio is default), axc2://alpine:latest, ax://alpine:latest, busybox (without tag it implies :latest)'
        d = 'busybox:latest'


manifestJsonEntries = []
registries = {
    'dockerio': {
        'authService': 'registry.docker.io',
        'authBase': 'https://auth.docker.io',
        'registryBase': 'https://registry-1.docker.io',
        'mani': 'application/vnd.docker.distribution.manifest',
    }
}
this_archi = 'amd64'

registries['axc2'] = d = dict(registries['dockerio'])
d['registryBase'] = 'https://axc2.mycompany.com'

registries['axint'] = d = dict(registries['dockerio'])
d['registryBase'] = 'https://artifacts-internal.mycompany.com/docker-internal'

registries['ax'] = d = dict(registries['dockerio'])
d['registryBase'] = 'https://artifacts.mycompany.com/docker-internal'
d['authBase'] = 'https://artifacts.mycompany.com/docker-internal'


def set_registry_urls_global(reg='dockerio'):
    """restricing a single dpull process to one registry, will fix on demand"""
    m = registries[reg]
    for k in m.keys():
        globals()[k] = m[k]


ctx = {'token': None, 'D': None, 'image': None}
# doNotGenerateManifestJson = False


def log(msg, **kw):
    app.log.info(msg, **kw)


def dbg(msg, **kw):
    app.log.debug(msg, **kw)


def die(msg, **kw):
    app.die(msg, **kw)


def run_in(cmd, d):
    h = os.getcwd()
    os.chdir(d)
    log('Running cmd', cmd=cmd, dir=d)
    r = not os.system(cmd)
    if not r:
        die('Failed', cmd=cmd)
    os.chdir(h)


def showj(msg, res, **kw):
    dbg(msg, res=deepcopy(res), **kw)


def G(url, headers={}):
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        die('failed', url=url, status=res.status_code, tx=res.text)
    res = res.text
    if res and res[0] in ('{', '['):
        res = json.loads(res)
        showj('Result', res=res, url=url)
    return res


def get_token(image):
    b = authBase + '/token?service='
    h = G(''.join((b, authService, '&scope=repository:', image, ':pull')))
    log('have token', token=h['token'][:10] + '...')
    ctx['token'] = h['token']


headers = lambda: {
    'Authorization': 'Bearer %(token)s' % ctx,
    'User-Agent': 'curl/7.64.0',
}


def get_mani(image, digest):
    h = headers()
    a = []
    for k in '.v2+json', '.list.v2+json', '.v1+json':
        a.append(mani + k)
    h['Accept'] = ', '.join(a)
    res = G(registryBase + '/v2/%s/manifests/%s' % (image, digest), headers=h)
    return res


def fetch_blob(digest, fn):
    h = headers()
    ctx['bdigest'] = digest
    u = registryBase + '/v2/%(image)s/blobs/%(bdigest)s' % ctx
    log('Getting blob', url=u)
    r = requests.get(u, headers=h, stream=True)
    with open(fn, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    return fn


def sha256sum(s):
    return hashlib.sha256(bytes(s, 'utf-8')).hexdigest()


def write(fn, s):
    if isinstance(s, (tuple, list, dict)):
        showj('Result', res=s)
        s = json.dumps(s, indent=4, sort_keys=True)
    with open(fn, 'wb') as fd:
        fd.write(bytes(s, 'utf8'))


def read(fn):
    with open(fn) as fd:
        s = fd.read()
        try:
            return json.loads(s)
        except:
            return s


def handle_single_manifest_v2(manifest):
    mj = manifest
    digest = mj['config']['digest']
    img_id = digest.replace('sha256:', '')
    fn_config = '%s.json' % img_id
    fetch_blob(digest, ctx['D'] + '/' + fn_config)
    layer_fs = mj['layers']
    log('Downloading', img_id=ctx['imageIdentifier'], layers=len(layer_fs))
    layer_tars = []
    layer_id = ''
    for i in layer_fs:
        lay_media_type = i['mediaType']
        lay_digest = i['digest']
        # save the previous layer's ID
        parent_id = layer_id
        # create a new fake layer ID based on this layer's digest and the previous layer's fake ID
        layer_id = sha256sum(parent_id + '\n' + lay_digest + '\n')
        # this accounts for the possibility that an image contains the same layer twice (and thus has a duplicate digest value)
        d = ctx['D'] + '/' + layer_id
        os.system('mkdir -p "%s"' % d)
        write(d + '/VERSION', '1.0\n')
        layer_tars.append(layer_id + '/layer.tar')
        if not os.path.exists(d + '/json'):
            # fmt:off
            add = {
                'id': layer_id,
                'created': '0001-01-01T00:00:00Z',
                'container_config': {
                    'Hostname'     : '',
                    'Domainname'   : '',
                    'User'         : '',
                    'AttachStdin'  : False,
                    'AttachStdout' : False,
                    'AttachStderr' : False,
                    'Tty'          : False,
                    'OpenStdin'    : False,
                    'StdinOnce'    : False,
                    'Env'          : None,
                    'Cmd'          : None,
                    'Image'        : '',
                    'Volumes'      : None,
                    'WorkingDir'   : '',
                    'Entrypoint'   : None,
                    'OnBuild'      : None,
                    'Labels'       : None,
                },
            }
            # fmt:on
            write(d + '/json', add)
        mt = 'application/vnd.docker.image.rootfs.diff.tar.gzip'
        if lay_media_type == mt:
            lay_tar = d + '/layer.tar'
            if os.path.exists(lay_tar):
                log('Skipping, already exists', layer=lay_tar)
                continue
            fetch_blob(lay_digest, lay_tar)

    # change "$imageId" to be the ID of the last layer we added (needed for old-style "repositories" file which is created later -- specifically for older D
    # munge the top layer image manifest to have the appropriate image configuration for older daemons
    image_id = layer_id
    fn = '/'.join((ctx['D'], image_id, 'json'))
    m = read(fn)
    img_old_cfg = {'id': m['id']}
    p = m.get('parent')
    if p:
        img_old_cfg['parent'] = p
    m = read(ctx['D'] + '/' + fn_config)
    m.pop('history', 0)
    m.pop('rootfs', 0)
    m.update(img_old_cfg)
    write(fn, m)
    manifestJsonEntries.append(
        {
            'Config': fn_config,
            'RepoTags': [ctx['image'].replace('libaray/', '') + ':' + ctx['tag']],
            'Layers': layer_tars,
        }
    )
    return image_id


def do_v1():
    M = ctx['manifestJson']
    fs_layers = [m['blobSum'] for m in M['fsLayers']]
    # imageIdentifier uses schemaVersion= %(schemaVersion)shhhhhh
    # this script cannot (currently) recreate the 'image config' to put in a
    # 'manifest.json' (thus any schemaVersion 2+ images will be imported in
    # the old way, and their 'docker history' will suffer)
    histories = M['history']
    history = [json.loads(histories[i]['v1Compatibility']) for i in range(len(histories))]
    log('History', history=history)
    image_id = history[0]['id']
    log(
        'Downloading', imageIdentifier=ctx['imageIdentifier'], layers=len(history),
    )
    nr = 0
    for h in history:
        layer_id = h['id']
        d = ctx['D'] + '/' + layer_id
        os.system('mkdir -p "%s"' % d)
        write(d + '/VERSION', '1.0\n')
        write(d + '/json', h)
        if os.path.exists(d + '/layer.tar'):
            log('Skipping, exists', layer=d)
        else:
            fetch_blob(fs_layers[nr], d + '/layer.tar')
        nr += 1
    return image_id


def do_v2():
    M = ctx['manifestJson']
    mediaType = M.get('mediaType')
    if mediaType == mani + '.v2+json':
        img_id = handle_single_manifest_v2(M)
    elif mediaType == mani + '.list.v2+json':
        manifests = M['manifests']
        layerFS = manifests
        found = []
        for l in layerFS:
            if not l['platform']['architecture'] == this_archi:
                continue
            found.append(1)
            digest = l['digest']
            sub_mani = get_mani(ctx['image'], digest)
            img_id = handle_single_manifest_v2(sub_mani)
        if not found:
            die('No manifest found for architecture', archi=this_archi)
    else:
        die('Unknown manifest media type', mediaType=mediaType)
    return img_id


def run():
    # FLG.log_dev_fmt_coljson = ['res']
    D = FLG.dir
    if not os.path.exists(D):
        os.system('mkdir -p "%s"' % D)
    run = partial(run_in, d=D)
    run('rm -f tags-*.tmp', d=D)
    repo = FLG.repo
    if not '://' in repo:
        repo = 'dockerio://' + repo
    if not len(repo.split(':')) == 3:
        repo += ':latest'
    app.info('Repo taken', repo=repo)
    reg, repo = repo.split('://')
    set_registry_urls_global(reg)
    image, imageTag = repo.split(':', 1)
    tag, digest = (imageTag + '@').split('@')[:2]
    if not digest:
        digest = tag
    # no digest yet
    oimg = image
    if not '/' in image:
        image = 'library/' + image

    imageFile = image.replace('/', '_')
    get_token(image)
    manifestJson = get_mani(image, digest)
    imageIdentifier = '%s:%s@%s' % (image, tag, digest)
    schemaVersion = manifestJson['schemaVersion']
    ctx.update(**locals())

    if schemaVersion == 2:
        img_id = do_v2()
    else:
        img_id = do_v1()

    R = ctx['D'] + '/repositories'
    r = read(R) if os.path.exists(R) else {}
    r.setdefault(oimg, {}).update({ctx['tag']: img_id})
    write(R, r)
    write(ctx['D'] + '/manifestJson', manifestJsonEntries)
    log('Success', docker_load_cmd="tar -cC '%s' . | docker load" % D)


main = lambda: run_app(
    run,
    flags=Flags,
    kw_log=dict(
        log_dev_fmt_coljson=['res'], censor=(['res', 'token'], ['res', 'access_token']),
    ),
)


if __name__ == '__main__':
    main()
