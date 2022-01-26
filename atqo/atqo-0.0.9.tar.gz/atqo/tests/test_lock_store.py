from atqo.lock_stores import FileLockStore


def test_lock_store():

    lock_store = FileLockStore("")

    lock = lock_store.acquire("__some__")

    lock.release()
