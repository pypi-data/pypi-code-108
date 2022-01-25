# Copyright (C) 2021-2022  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
import random
import time

import pytest

from swh.perfecthash import Shard


def test_all(tmpdir):
    f = f"{tmpdir}/shard"
    open(f, "w").close()
    os.truncate(f, 10 * 1024 * 1024)

    s = Shard(f).create(2)
    keyA = b"A" * Shard.key_len()
    objectA = b"AAAA"
    s.write(keyA, objectA)
    keyB = b"B" * Shard.key_len()
    objectB = b"BBBB"
    s.write(keyB, objectB)
    s.save()
    del s

    s = Shard(f).load()
    assert s.lookup(keyA) == objectA
    assert s.lookup(keyB) == objectB
    del s


@pytest.fixture
def payload(request):
    size = request.config.getoption("--shard-size")
    path = request.config.getoption("--shard-path")
    if not os.path.exists(path) or os.path.getsize(path) != size * 1024 * 1024:
        os.system(f"dd if=/dev/urandom of={path} count={size} bs=1024k")
    return path


#
# PYTHONMALLOC=malloc valgrind --tool=memcheck .tox/py3/bin/pytest \
#    -k test_build_speed swh/perfecthash/tests/test_hash.py |& tee /tmp/v
#
def test_build_speed(request, tmpdir, payload):
    start = time.time()
    os.system(f"cp {payload} {tmpdir}/shard")
    baseline = time.time() - start
    write_duration, build_duration, _ = shard_build(request, tmpdir, payload)
    duration = write_duration + build_duration
    print(
        f"baseline {baseline}, "
        f"write_duration {write_duration}, "
        f"build_duration {build_duration}, "
        f"total_duration {duration}"
    )
    #
    # According to the docs/benchmarks.rst analysis, the duration is
    # below 5 times the baseline time This assertion is here to ensure
    # we do not not regress in the future...
    #
    assert duration < baseline * 5


def test_lookup_speed(request, tmpdir, payload):
    _, _, objects = shard_build(request, tmpdir, payload)
    for i in range(request.config.getoption("--shard-count")):
        os.system(f"cp {tmpdir}/shard {tmpdir}/shard{i}")
    start = time.time()
    shard_lookups(request, tmpdir, objects)
    duration = time.time() - start

    lookups = request.config.getoption("--lookups")
    key_per_sec = lookups / duration
    print(f"key lookups speed = {key_per_sec:.2f}/s")


def shard_lookups(request, tmpdir, objects):
    shard_path = f"{tmpdir}/shard"
    shards = []
    for i in range(request.config.getoption("--shard-count")):
        shards.append(Shard(f"{shard_path}{i}").load())
    lookups = request.config.getoption("--lookups")
    count = 0
    while True:
        for key, object_size in objects.items():
            if count >= lookups:
                return
            for shard in shards:
                object = shard.lookup(key)
                assert len(object) == object_size
                count += 1


def shard_build(request, tmpdir, payload):
    shard_size = request.config.getoption("--shard-size") * 1024 * 1024
    shard_path = f"{tmpdir}/shard"
    open(shard_path, "w").close()
    os.truncate(shard_path, shard_size * 2)

    object_max_size = request.config.getoption("--object-max-size")
    objects = {}
    count = 0
    size = 0
    with open(payload, "rb") as f:
        while True:
            key = f.read(Shard.key_len())
            if len(key) < Shard.key_len():
                break
            assert key not in objects
            object = f.read(random.randrange(512, object_max_size))
            if len(object) < 512:
                break
            objects[key] = len(object)
            size += len(object)
            count += 1

    print(f"number of objects = {count}, total size = {size}")
    assert size < shard_size
    start = time.time()
    shard = Shard(shard_path).create(len(objects))

    count = 0
    size = 0
    with open(payload, "rb") as f:
        while True:
            key = f.read(Shard.key_len())
            if len(key) < Shard.key_len():
                break
            if key not in objects:
                break
            object = f.read(objects[key])
            assert len(object) == objects[key]
            count += 1
            size += len(object)
            assert shard.write(key, object) >= 0, (
                f"object count {count}/{len(objects)}, "
                f"size {size}, "
                f"object size {len(object)}"
            )
    write_duration = time.time() - start
    start = time.time()
    shard.save()
    build_duration = time.time() - start
    return write_duration, build_duration, objects
