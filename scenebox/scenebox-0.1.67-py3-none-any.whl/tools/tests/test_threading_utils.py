from concurrent.futures.thread import ThreadPoolExecutor

from shared.external.tools.threading_utils import create_exception_map


def test_create_exception_map():
    def threaded_process(i):
        if i == 4:
            i / 0.0
        elif i == 40:
            raise TypeError
        else:
            return None

    nums = [i for i in range(100)]
    with ThreadPoolExecutor(max_workers=1) as executor:
        future_res = {
            executor.submit(
                threaded_process,
                i=num): num for num in nums}
        id_exception_map = create_exception_map(future_map=future_res)

    assert isinstance(id_exception_map[4], ZeroDivisionError)
    assert isinstance(id_exception_map[40], TypeError)
