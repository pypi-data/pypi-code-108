from __future__ import annotations
from typing import List, Tuple
from enum import Enum

import click

import lunar


class CRUDMethod(Enum):
    CREATE = "CREATE"
    LIST = "LIST"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

    @classmethod
    def list_items(cls) -> List[CRUDMethod]:
        return [t for t in cls]

    @classmethod
    def list_values(cls) -> List[str]:
        return [t.value for t in cls]


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    pass


@click.command()
@click.option("-i", "--id", help="Unique identifier of a recommendation target")
@click.option("-c", "--channel-id", "channel_id", help="Unique identifier of a channel")
@click.option(
    "-p",
    "--params",
    help="Additional parameters for recommendation",
    type=click.Tuple([str, str]),
    multiple=True,
)
def recommend(id: str, channel_id: str, params: Tuple[Tuple[str, str]]):
    """
    Recommendation on lunar-rec

    Send a request to Lunar Recommendation API (`/v1/recommend/`).

    Return: dict
    """

    try:
        assert id is not None, "`id` value is necessary for recommendation"
        assert channel_id is not None, "`channel_id` value is necessary for recommendation"

        client = lunar.client("recommend")

        params = {param[0]: param[1] for param in params}
        res = client.recommend(id=id, channel_id=channel_id, params=params)
        print("Recommendation value:")
        print(res)
    except Exception as e:
        print(f"Error: {str(e)}")


@click.command()
@click.argument("method", type=click.Choice(CRUDMethod.list_values(), case_sensitive=False))
@click.option("-i", "--id", help="Unique identifier of a channel")
@click.option("-e", "--experiment-id", "experiment_id", help="Unique identifier of an experiment assigned")
@click.option("-p", "--partial", is_flag=True, help="Partial update or not (default: False)")
def channel(method: str, id: str, experiment_id: str, partial: bool):
    """
    Channels on lunar-rec

    Send a request to Lunar Recommendation API (`/v1/channels/`).

    Return: dict or list(dict)
    """

    try:
        client = lunar.client("channel")

        if method == CRUDMethod.CREATE.value:
            assert id is not None, "`id` value is necessary to create a channel"
            assert experiment_id is not None, "`experiment-id` value is necessary to create a channel"
            channel = client.create_channel(id=id, experiment_id=experiment_id)
            print("Created:")
            print(channel.dict())

        elif method == CRUDMethod.LIST.value:
            result = [channel.id for channel in client.list_channels()]
            print(f"Total {len(result)} channels")
            print(f"Channels: {result}")

        elif method == CRUDMethod.READ.value:
            assert id is not None, "`id` value is necessary to read a channel"
            print(client.get_channel(id=id).dict())

        elif method == CRUDMethod.UPDATE.value:
            assert id is not None, "`id` value is necessary to update a channel"

            if partial:
                updated_channel = client.update_channel_partial(id=id, experiment_id=experiment_id)
                print("Updated:")
                print(updated_channel.dict())
                return

            updated_channel = client.update_channel(id=id, experiment_id=experiment_id)
            print("Updated:")
            print(updated_channel.dict())

        elif method == CRUDMethod.DELETE.value:
            assert id is not None, "`id` value is necessary to delete a channel"
            try:
                channel = client.get_channel(id=id)
            except Exception as e:
                print(str(e))
                return

            delete_or_not = input(f"Are you sure you want to delete a channel `{id}`? [y/N] ") or "N"
            assert delete_or_not.upper() in ["Y", "N"], "Enter `Y` or `N`"

            if delete_or_not.upper() == "Y":
                client.delete_channel(id=id)
                print(f"Channel `{id}` is deleted")
            else:
                print("DELETE CLI is canceled")

    except Exception as e:
        print(f"Error: {str(e)}")


@click.command()
@click.argument("method", type=click.Choice(CRUDMethod.list_values(), case_sensitive=False))
@click.option("-i", "--id", help="Unique identifier of a channel")
@click.option("-b", "--buckets", help="Bucket list", type=click.Tuple([str, int]), multiple=True)
@click.option("-s", "--bucketing-seed", "bucketing_seed", help="Random seed for bucketing", default="")
@click.option("-p", "--partial", is_flag=True, help="Partial update or not (default: False)")
def experiment(method: str, id: str, buckets: List[Tuple[str, str]], bucketing_seed: str, partial: bool):
    """
    Experiments on lunar-rec

    Send a request to Lunar Recommendation API (`/v1/experiemnts/`).

    Return: dict or list(dict)
    """

    try:
        client = lunar.client("experiment")

        if method == CRUDMethod.CREATE.value:
            assert id is not None, "`id` value is necessary to create a experiment"
            assert buckets is not None, "`buckets` value is necessary to create a experiment"

            buckets = [{"name": bucket[0], "ratio": bucket[1]} for bucket in buckets]
            try:
                experiment = client.create_experiment(id=id, buckets=buckets, bucketing_seed=bucketing_seed)
                print("Created:")
                print(experiment.dict())
            except lunar.LunarError as e:
                print(f"Error: {str(e)}")

        elif method == CRUDMethod.LIST.value:
            result = [experiment.id for experiment in client.list_experiments()]
            print(f"Total {len(result)} experiments")
            print(f"Experiments: {result}")

        elif method == CRUDMethod.READ.value:
            assert id is not None, "`id` value is necessary to read an experiment"

            print(client.get_experiment(id=id).dict())

        elif method == CRUDMethod.UPDATE.value:
            assert id is not None, "`id` value is necessary to update an experiment"

            if buckets:
                buckets = [{"name": bucket[0], "ratio": bucket[1]} for bucket in buckets]

            if partial:
                updated_experiment = client.update_experiment_partial(
                    id=id, buckets=buckets, bucketing_seed=bucketing_seed
                )
                print("Updated:")
                print(updated_experiment.dict())
                return

            assert buckets is not None, "`buckets` value is necessary to update a experiment"

            updated_experiment = client.update_experiment(id=id, buckets=buckets, bucketing_seed=bucketing_seed)
            print("Updated:")
            print(updated_experiment.dict())

        elif method == CRUDMethod.DELETE.value:
            assert id is not None, "`id` value is necessary to delete an experiment"
            try:
                experiment = client.get_experiment(id=id)
            except Exception as e:
                print(str(e))
                return

            delete_or_not = input(f"Are you sure you want to delete an experiment `{id}`? [y/N] ") or "N"
            assert delete_or_not.upper() in ["Y", "N"], "Enter `Y` or `N`"

            if delete_or_not.upper() == "Y":
                client.delete_experiment(id=id)
                print(f"Experiment `{id}` is deleted")
            else:
                print("DELETE CLI is canceled")

    except Exception as e:
        print(f"Error: {str(e)}")


@click.command()
@click.option("-d", "--dataset-id", "dataset_id", help="Unique identifier of a dataset")
@click.option("-i", "--id", help="Unique identifier of a target")
@click.option(
    "-a",
    "--attributes",
    help="Attributes to get from datasets",
    multiple=True,
)
def data(id: str, dataset_id: str, attributes: Tuple[str]):
    """
    Data on lunar-data

    Send a request to Lunar Data API (`/v1/data/`).

    Return: dict
    """

    try:
        assert dataset_id is not None, "`dataset-id` value is necessary for data"
        assert id is not None, "`id` value is necessary for data"

        client = lunar.client("data")

        res = client.get_data(dataset_id=dataset_id, id=id, attributes=list(attributes))

        print("Data value:")
        print(res)
    except Exception as e:
        print(f"Error: {str(e)}")


@click.command()
@click.argument("method", type=click.Choice(CRUDMethod.list_values(), case_sensitive=False))
@click.option("-i", "--id", help="Unique identifier of a dataset")
@click.option("-d", "--data-type", "data_type", help="Dataset Type", default="dynamodb")
@click.option("-t", "--tables", help="Dataset parameter for `tables`", multiple=True)
@click.option("-m", "--main-table", "main_table", help="Dataset parameter for `main_table`", default="")
@click.option("-p", "--partial", is_flag=True, help="Partial update or not (default: False)")
def dataset(method: str, id: str, data_type: str, tables: str, main_table: Tuple[str], partial: bool):
    """
    Datasets on lunar-data

    Send a request to Lunar Data API (`/v1/datasets/`).

    Return: dict or list(dict)
    """

    try:
        client = lunar.client("dataset")

        if method == CRUDMethod.CREATE.value:
            assert id is not None, "`id` value is necessary to create a dataset"
            assert data_type is not None, "`data-type` value is necessary to create a dataset"
            assert tables is not None, "`tables` value is necessary to create a dataset"
            assert main_table is not None, "`main-table` value is necessary to create a dataset"

            try:
                params = {"tables": list(tables), "main_table": main_table}
                dataset = client.create_dataset(id=id, data_type=data_type, params=params)
                print("Created:")
                print(dataset.dict())
            except lunar.LunarError as e:
                print(f"Error: {str(e)}")

        elif method == CRUDMethod.LIST.value:
            result = [dataset.id for dataset in client.list_datasets()]
            print(f"Total {len(result)} datasets")
            print(f"Datasets: {result}")

        elif method == CRUDMethod.READ.value:
            assert id is not None, "`id` value is necessary to read a dataset"

            print(client.get_dataset(id=id).dict())

        elif method == CRUDMethod.UPDATE.value:
            assert id is not None, "`id` value is necessary to update a dataset"

            if partial:
                params = {}
                if tables:
                    params["tables"] = list(tables)
                if main_table:
                    params["main_table"] = main_table

                updated_dataset = client.update_dataset_partial(id=id, data_type=data_type, params=params)
                print("Updated:")
                print(updated_dataset.dict())
                return

            assert data_type is not None, "`data-type` value is necessary to update a dataset"
            assert tables is not None, "`tables` value is necessary to update a dataset"
            assert main_table is not None, "`main-table` value is necessary to update a dataset"

            params = {"tables": list(tables), "main_table": main_table}

            updated_dataset = client.update_dataset(id=id, data_type=data_type, params=params)
            print("Updated:")
            print(updated_dataset.dict())

        elif method == CRUDMethod.DELETE.value:
            assert id is not None, "`id` value is necessary to delete a dataset"
            try:
                dataset = client.get_dataset(id=id)
            except Exception as e:
                print(str(e))
                return

            delete_or_not = input(f"Are you sure you want to delete a dataset `{id}`? [y/N] ") or "N"
            assert delete_or_not.upper() in ["Y", "N"], "Enter `Y` or `N`"

            if delete_or_not.upper() == "Y":
                client.delete_dataset(id=id)
                print(f"Dataset `{id}` is deleted")
            else:
                print("DELETE CLI is canceled")

    except Exception as e:
        print(f"Error: {str(e)}")


def main():
    """
    CLI(Command Line Interface) for lunar services

    For the details, use -h(--h) option on `lunar` command
    """

    # lunar-rec API
    cli.add_command(channel)
    cli.add_command(experiment)
    cli.add_command(recommend)

    # lunar-data API
    cli.add_command(data)
    cli.add_command(dataset)
    cli()


if __name__ == "__main__":
    main()
