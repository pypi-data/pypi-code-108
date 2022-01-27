# pylint: skip-file
import asyncio
import time
import os

import unimatrix.lib.test

from unimatrix.ext import cache
from unimatrix.ext import model


@unimatrix.lib.test.needs('redis')
class RedisTestCase(unimatrix.lib.test.AsyncTestCase):
    __test__ = True

    async def setUp(self):
        self.prefix = bytes.hex(os.urandom(16))
        cache.connections.add('default', {
            'backend': 'redis',
            'host': 'localhost',
            'port': 6379,
            'database': 2,
            'prefix': self.prefix,
        })
        await cache.connections.connect()

    async def tearDown(self):
        await cache.purge('default')
        await cache.connections.destroy()

    async def test_lock_acquire(self):
        lock = cache.Lock(bytes.hex(os.urandom(4)))
        await lock.acquire()
        self.assertTrue(lock.locked())

    async def test_lock_blocks(self):
        k = bytes.hex(os.urandom(4))
        lock1 = cache.Lock(k)
        lock2 = cache.Lock(k)
        self.invocations = []

        async def f1():
            await lock1.acquire()
            self.invocations.append(1)
            await asyncio.sleep(1)
            self.t1 = time.time()
            await lock1.release()

        async def f2():
            await lock2.acquire()
            self.invocations.append(2)
            self.t2 = time.time()
            await lock2.release()

        futures = [f1()]
        await asyncio.sleep(0.1)
        futures.append(f2())
        await asyncio.gather(*futures)
        self.assertEqual([1, 2], self.invocations)

    async def test_lock_acquire_timeout(self):
        k = bytes.hex(os.urandom(4))
        lock1 = cache.Lock(k)
        lock2 = cache.Lock(k, interval=0.1)
        self.assertTrue(await lock1.acquire())
        self.assertFalse(await lock2.acquire(0.1))
        self.assertTrue(lock1.locked())
        self.assertTrue(not lock2.locked())

    async def test_lock_release(self):
        k = bytes.hex(os.urandom(4))
        lock1 = cache.Lock(k)
        await lock1.acquire()
        await lock1.release()
        self.assertTrue(not lock1.locked())

    async def test_lock_release_automatic(self):
        k = bytes.hex(os.urandom(4))
        lock1 = cache.Lock(k, expires=100)
        lock2 = cache.Lock(k)
        await lock1.acquire()
        await asyncio.sleep(0.1)
        self.assertTrue(await lock2.acquire(0.1))

    async def test_lock_release_raises_if_not_locked(self):
        k = bytes.hex(os.urandom(4))
        lock1 = cache.Lock(k)
        with self.assertRaises(RuntimeError):
            await lock1.release()

    async def test_ratelimit_simple(self):
        key = bytes.hex(os.urandom(4))
        ttl = 1
        now = int(time.time())

        # First attempt, ratelimit key is set.
        async with cache.ratelimit(key=key, ttl=ttl):
            pass

        # Second attempt, ratelimit is enforced.
        try:
            async with cache.ratelimit(key=key, ttl=ttl):
                self.fail("Ratelimit not enforced.")
        except cache.Backoff as e:
            await asyncio.sleep(e.seconds)

        # Third attempt, ratelimit is not enforced.
        async with cache.ratelimit(key=key, ttl=ttl):
            pass

    async def test_filter(self):
        await cache.set('sub-1-whitelist', 'foo')
        await cache.set('sub-1-ips', 'bar')
        keys = []
        async for k in await cache.filter(f'sub-1*'):
            keys.append(k)
        self.assertEqual(len(keys), 2, keys)

    async def test_filter_versioned(self):
        await cache.set('sub-1-whitelist', 'foo')
        await cache.set('sub-1-ips', 'bar')
        await cache.set('sub-1-foo', 'bar', version=2)
        keys = []
        async for k in await cache.filter(f'sub-1*'):
            keys.append(k)
        self.assertEqual(len(keys), 2, keys)

    async def test_set(self):
        k = 'foo'
        await cache.set(k, 'bar')
        self.assertEqual(await cache.get(k), b'bar')

    async def test_set_versioned(self):
        k = 'foo'
        await cache.set(k, 'bar')
        await cache.set(k, 'baz', version=2)
        await cache.set(k, 'taz', version=3)
        self.assertEqual(await cache.get(k), b'bar')
        self.assertEqual(await cache.get(k, version=2), b'baz')
        self.assertEqual(await cache.get(k, version=3), b'taz')

    async def test_set_counter(self):
        self.assertEqual(await cache.add('counter'), 1)
        self.assertEqual(await cache.add('counter'), 2)
        self.assertEqual(await cache.add('counter'), 3)
        self.assertEqual(await cache.add('counter', 2), 5)

        await cache.delete('counter')
        self.assertEqual(await cache.add('counter'), 1)

    async def test_set_counter_expires(self):
        self.assertEqual(await cache.add('counter', expires=500), 1)
        await asyncio.sleep(1)
        self.assertEqual(await cache.add('counter', expires=500), 1)

    async def test_set_expires(self):
        k = 'foo'
        await cache.set(k, 'bar', expires=1000)
        self.assertEqual(await cache.get(k), b'bar')
        await asyncio.sleep(1)
        self.assertEqual(await cache.get(k), None)

    async def test_set_no_overwrite_existing(self):
        k = bytes.hex(os.urandom(4))
        await cache.set(k, 'foo', overwrite=False)
        await cache.set(k, 'bar', overwrite=False)
        self.assertNotEqual(
            await cache.set(k, 'bar', overwrite=False),
            'bar'
        )
        self.assertEqual(await cache.get(k), b'foo')

    async def test_set_no_overwrite_existing_expires(self):
        k = bytes.hex(os.urandom(4))
        await cache.set(k, 'foo', overwrite=False, expires=1000)
        await cache.set(k, 'bar', overwrite=False, expires=1000)
        self.assertEqual(await cache.get(k), b'foo')
        await asyncio.sleep(1)
        self.assertTrue(await cache.get(k) is None)

    async def test_del(self):
        k = 'foo'
        await cache.set(k, 'bar')
        await cache.delete(k)
        self.assertEqual(await cache.get(k), None)

    async def test_backoff_is_enforced(self):
        key = 'backoff-' + os.urandom(4).hex()

        # Attempts: 1
        try:
            async with cache.backoff(key):
                raise NotImplementedError
        except NotImplementedError:
            pass

        # Attempts: 2
        model.CanonicalException().as_dict()
        try:
            async with cache.backoff(key):
                raise model.CanonicalException()
        except model.CanonicalException as e:
            dto = e.as_dict()
            self.assertEqual(dto['backoff']['attempts'], 2)
        except cache.Backoff as e:
            self.fail("Backoff raised on first failure.")

        # Wait until the second attempt expires.
        try:
            async with cache.backoff(key):
                self.fail("Backoff must be raised.")
        except cache.Backoff as e:
            backoff = e
        self.assertTrue(backoff is not None)
        self.assertEqual(backoff.seconds, 2)
        self.assertEqual(backoff.attempts, 2)
        await asyncio.sleep(backoff.seconds)

        # Attempts: 3
        try:
            async with cache.backoff(key):
                raise model.CanonicalException()
        except model.CanonicalException as e:
            self.assertEqual(e.backoff['attempts'], 3)

        try:
            async with cache.backoff(key):
                self.fail("Backoff must be raised.")
        except cache.Backoff as e:
            backoff = e
        self.assertTrue(backoff is not None)
        self.assertEqual(backoff.seconds, 4)
        self.assertEqual(backoff.attempts, 3)
        await asyncio.sleep(backoff.seconds)
        async with cache.backoff(key):
            pass

        # Check if the key is removed
        self.assertTrue(await cache.get(key) is None)
        self.assertTrue(await cache.get(f'{key}-expires') is None)
