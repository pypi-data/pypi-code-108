import asyncio
from typing import Any, Awaitable

from ecgai_training_data_physionet.models import EcgRecord
from ecgai_training_data_physionet.ptbxl import PtbXl


async def run_sequence(*functions: Awaitable[Any]) -> None:
    for function in functions:
        await function


async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)


async def main():
    lst = list(range(1, 100))
    record_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    tasks = [get_record("data", i) for i in lst]
    await run_parallel(*tasks)


async def get_records_list() -> list[str]:
    """
    Returns all records from a database on physionet
    Returns:
        list[str]:

    """
    NotImplementedError()


# noinspection PyTypeChecker


async def get_record(record_path_name: str, record_id: int) -> EcgRecord:
    sut = PtbXl(data_location=record_path_name)
    # record_task = asyncio.create_task(sut.get_record(record_path_name=record_path_name))
    record_task = sut.get_record(record_id=record_id)
    result = await record_task
    print(result.record_name)


if __name__ == "__main__":
    asyncio.run(main())
