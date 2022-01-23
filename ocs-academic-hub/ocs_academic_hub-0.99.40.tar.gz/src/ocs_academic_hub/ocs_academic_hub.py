#
from .util import timer
import configparser
from dateutil.parser import parse
from datetime import datetime, timedelta
import requests
from requests.structures import CaseInsensitiveDict
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import io
import json
import os
import numpy as np
import pandas as pd
from typeguard import typechecked
from typing import List, Union
import pkg_resources
import urllib3
import backoff
import logging
from math import nan

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


from ocs_sample_library_preview import OCSClient, DataView, SdsError

GRAPHQL_ENDPOINT = "https://data.academic.osisoft.com/graphql"
MAX_STORED_DV_ROWS = 2000000
UXIE_CONSTANT = 100 * 1000
HUB_KEY_BLOB = "https://academichub.blob.core.windows.net/hub/keys/"
HUB_CLIENT_CONFIG = HUB_KEY_BLOB + "config.txt"

hub_db_namespaces = CaseInsensitiveDict({})

ocstype2hub = {
    "PI-Digital": "Category",
    "PI-String": "String",
    "PI-Timestamp": "Timestamp",
    "PI-Int16": "Integer",
    "PI-Int32": "Integer",
}

resource_package = __name__
resource_path = "/".join((".", "hub_datasets.json"))
default_hub_data = pkg_resources.resource_filename(resource_package, resource_path)


def asset_id_fix(gqlh):
    for i, database in enumerate(gqlh["Database"]):
        for j, asset in enumerate(database["asset_with_dv"]):
            if asset.get("asset_id", None) is None:
                asset["asset_id"] = asset["name"]
            else:
                asset["name"] = asset["asset_id"]
    return gqlh


def initialize_hub_data(data_file):
    global hub_db_namespaces
    with open(data_file) as f:
        gqlh = json.loads(f.read())
    db_index = CaseInsensitiveDict({})
    hub_db_namespaces.clear()
    for i, database in enumerate(gqlh["Database"]):
        db_index[database["asset_db"]] = i
        hub_db_namespaces[database["name"]] = database["namespace"]
    return asset_id_fix(gqlh), gqlh["Database"][0]["asset_db"], db_index


def assets_and_metadata(gqlh, db_index, current_db):
    assets_info = gqlh["Database"][db_index[current_db]]["asset_with_dv"]
    asset_key = "name"
    assets = sorted([i[asset_key].lower() for i in assets_info])
    dv_column_key = {}
    for i in assets_info:
        for dv in i["has_dataview"]:
            dv_column_key[dv["id"]] = dv.get("ocs_column_key", None)
    metaf = lambda x: {} if x is None else eval(x)
    metadata = {
        assets_info[j][asset_key]: metaf(assets_info[j]["asset_metadata"])
        for j in range(len(assets_info))
    }
    for key in metadata.keys():
        d = metadata[key]
        d.update({"Asset_Id": key})
    return assets, metadata, dv_column_key


class SdsError50x(Exception):
    pass


class GraphQLError409(Exception):
    pass


def get_config(url, client_secret=""):
    if len(client_secret):
        client_secret = f"\nClientSecret = {client_secret}\n"
    reply = requests.get(url)
    if reply.status_code != 200:
        raise SdsError("@ ### authorization denied ###")
    return io.StringIO(reply.text + client_secret)


class HubClient(OCSClient):
    @typechecked
    def __init__(
        self,
        hub_data: str = "hub_datasets.json",
        client_key: str = "",
        options: List[str] = [],
        debug: bool = False,
    ):
        if debug:
            logging.getLogger("backoff").addHandler(logging.StreamHandler())
        config_filename = os.environ.get("HUB_CONFIG_FILE", None)
        config_file = None
        if config_filename is None:
            if len(client_key) > 0 or os.environ.get("HUB_CLIENT_KEY", None):
                print(
                    "@ --- OSIsoft authorization required to run hosted notebook (Collab/Binder/etc) ---"
                )
                config_file = get_config(
                    HUB_CLIENT_CONFIG,
                    client_secret=client_key
                    if len(client_key)
                    else os.environ.get("HUB_CLIENT_KEY"),
                )
            else:
                config_filename = "config.txt" if os.path.exists("config.txt") else None
        try:
            if config_filename is None and config_file is None:
                super().__init__(
                    "v1",
                    "65292b6c-ec16-414a-b583-ce7ae04046d4",
                    "https://dat-b.osisoft.com",
                    "422e6002-9c5a-4651-b986-c7295bcf376c",
                )
            else:
                config = configparser.ConfigParser()
                if config_filename:
                    print(f"> configuration file: {config_filename}")
                    config.read(config_filename)
                else:
                    config.read_file(config_file)
                super().__init__(
                    config.get("Access", "ApiVersion"),
                    config.get("Access", "Tenant"),
                    config.get("Access", "Resource"),
                    config.get("Credentials", "ClientId"),
                    config.get("Credentials", "ClientSecret"),
                )
                print("@ --- authorization granted ---")

            self.__options = options
            self.__debug = debug
            data_file = hub_data if os.path.isfile(hub_data) else default_hub_data
            if data_file != default_hub_data:
                print(f"@ Hub data file: {data_file}")
            self.__gqlh, self.__current_db, self.__db_index = initialize_hub_data(
                data_file
            )
            self.__current_db_index = 0
            (
                self.__assets,
                self.__assets_metadata,
                self.__dv_column_key,
            ) = assets_and_metadata(self.__gqlh, self.__db_index, self.__current_db)
            self.__dataview_next_page = None

        except SdsError as e:
            raise Exception("{}".format(e)) from None

    def gqlh(self):
        return self.__gqlh

    @typechecked
    def asset_metadata(self, asset: str):
        if asset.lower() not in self.__assets:
            print(
                f"@@ error: asset {asset} not in dataset asset list, check hub.assets()"
            )
            return
        return self.__assets_metadata[asset]

    def all_assets_metadata(self):
        metadata = [
            self.__assets_metadata[key] for key in self.__assets_metadata.keys()
        ]
        return pd.DataFrame(metadata).sort_values(by=["Asset_Id"])

    @typechecked
    def datasets(self, first="") -> List[str]:
        data_sets = list(hub_db_namespaces.keys())
        data_sets.sort(key=lambda s: s == first, reverse=True)
        return data_sets

    @typechecked
    def current_dataset(self) -> str:
        return self.__gqlh["Database"][self.__current_db_index]["name"]

    @typechecked
    def dataset_version(self) -> str:
        version = self.__gqlh["Database"][self.__current_db_index].get(
            "version", "not available"
        )
        status = self.__gqlh["Database"][self.__current_db_index].get(
            "status", "-not set-"
        )
        return f"{version} (status: {status})"

    @typechecked
    def set_dataset(self, dataset: str):
        try:
            hub_db_namespaces[dataset]
        except KeyError:
            print(f"@@ Dataset {dataset} does not exist, please check hub.datasets()")
            return
        for j in range(len(self.__gqlh["Database"])):
            if self.__gqlh["Database"][j]["name"] == dataset:
                self.__current_db_index = j
                self.__current_db = self.__gqlh["Database"][j]["asset_db"]
                (
                    self.__assets,
                    self.__assets_metadata,
                    self.__dv_column_key,
                ) = assets_and_metadata(self.__gqlh, self.__db_index, self.__current_db)
                break

    @typechecked
    def namespace_of(self, dataset: str):
        try:
            return hub_db_namespaces[dataset]
        except KeyError:
            print(f"@@ Dataset {dataset} does not exist, please check hub.datasets()")

    @typechecked
    def assets(self, filter: str = ""):
        df = pd.DataFrame(columns=("Asset_Id", "Description"))
        asset_description = {
            i["name"]: i["description"]
            for i in self.__gqlh["Database"][self.__db_index[self.__current_db]][
                "asset_with_dv"
            ]
            if filter.lower() in i["name"].lower()
        }
        sorted_assets = sorted(list(asset_description.keys()))
        for i, asset in enumerate(sorted_assets):
            df.loc[i] = [asset, asset_description[asset]]
        return df

    @typechecked
    def asset_dataviews(
        self, filter: str = "default", asset: str = "", multiple_asset: bool = False
    ) -> Union[None, List[str]]:
        if len(asset) > 0:
            if asset.lower() not in self.__assets:
                print(
                    f"@@ error: asset {asset} not in dataset asset list, check hub.assets()"
                )
                return
        if not multiple_asset:
            len_test = lambda l: len(l) == 1
        else:
            len_test = lambda l: len(l) > 1
        if asset == "":
            asset_test = lambda x, y: True
        else:
            asset_test = lambda asset, asset_list: asset.lower() in [
                i.lower() for i in asset_list
            ]

        dataviews = []
        for j in self.__gqlh["Database"][self.__db_index[self.__current_db]][
            "asset_with_dv"
        ]:
            if len(asset) > 0 and j["name"].lower() == asset.lower():
                dataviews = j["has_dataview"]
                break
            else:
                dataviews.extend(j["has_dataview"])

        return sorted(
            list(
                set(
                    [
                        i["id"]
                        for i in dataviews
                        if (
                            filter.lower() in i["id"]
                            or filter.lower() in i["description"].lower()
                        )
                        and asset_test(asset, i["asset_id"])
                        and len_test(i["asset_id"])
                    ]
                )
            )
        )

    def __asdict(self, item_metadata):
        return {i["Name"]: i["Value"] for i in item_metadata}

    @backoff.on_exception(
        backoff.expo, SdsError, max_tries=6, jitter=backoff.full_jitter
    )
    @typechecked
    def dataview_definition(
        self,
        namespace_id: str,
        dataview_id: str,
        stream_id: bool = False,
        version: str = "",
    ):
        columns = [
            "Asset_Id",
            "Column_Name",
            "Stream_Type",
            "Stream_UOM",
            "OCS_Stream_Name",
        ]
        if stream_id:
            columns += ["OCS_Stream_Id"]
        df = pd.DataFrame(columns=columns)

        data_items = super().DataViews.getResolvedDataItems(
            namespace_id, dataview_id, "Asset_value?count=1000&cache=refresh"
        )
        v2_column_key = self.__dv_column_key.get(dataview_id, None)
        column_key = (
            "column_name" if v2_column_key is None else f"{v2_column_key}|column"
        )
        for i, item in enumerate(data_items.Items):
            item_meta = CaseInsensitiveDict(self.__asdict(item.Metadata))
            column_values = [
                item_meta["asset_id"],
                item_meta[column_key],
                ocstype2hub.get(item.TypeId, "Float"),
                item_meta.get("engunits", "-n/a-").replace("Â", ""),
                item.Name,
            ]
            if stream_id:
                column_values += [item.Id]
            df.loc[i] = column_values
        return df.sort_values(["Column_Name", "Asset_Id"])

    @backoff.on_exception(
        backoff.expo, SdsError, max_tries=6, jitter=backoff.full_jitter
    )
    def dataview_columns(self, namespace_id: str, dataview_id: str):
        data_items = super().DataViews.getResolvedDataItems(
            namespace_id, dataview_id, "Asset_value?count=1000"
        )
        digital_items = super().DataViews.getResolvedDataItems(
            namespace_id, dataview_id, "Asset_digital?count=1000"
        )
        return len(data_items.Items) + len(digital_items.Items) + 1

    def __process_digital_states(self, df):
        ds_columns = [col for col in list(df.columns) if col[-4:] == "__ds"]
        if len(ds_columns) > 0:
            for ds_col in ds_columns:
                val_col = ds_col[:-4]
                index = df[val_col].index[df[val_col].apply(np.isnan)]
                df.loc[index, [ds_col]] = ""
            df = df.drop(columns=[ds_col[:-4] for ds_col in ds_columns])
            df = df.rename(columns={ds_col: ds_col[:-4] for ds_col in ds_columns})
        return df

    def __get_data_interpolated(
        self,
        namespace_id,
        dataview_id,
        form,
        start_index,
        end_index,
        interval,
        count,
        next_page,
    ):
        count_arg = {} if count is None else {"count": count}
        return super().DataViews.getDataInterpolated(
            namespace_id,
            dataview_id,
            # count=count,
            form=form,
            startIndex=start_index,
            endIndex=end_index,
            interval=interval,
            url=next_page,
            **count_arg,
        )

    def __get_data_stored(
        self,
        namespace_id,
        dataview_id,
        form,  # not used
        start_index,
        end_index,
        interval,  # not used
        count,
        next_page,
    ):
        count_arg = {} if count is None else {"count": count}
        return super().DataViews.getDataStored(
            namespace_id,
            dataview_id,
            startIndex=start_index,
            endIndex=end_index,
            url=next_page,
            **count_arg,
        )

    @typechecked
    def remaining_data(self) -> bool:
        return False if self.__dataview_next_page is None else True

    @backoff.on_exception(
        backoff.expo, SdsError50x, max_tries=6, jitter=backoff.full_jitter
    )
    @timer
    @typechecked
    def dataview_interpolated_pd(
        self,
        namespace_id: str,
        dataview_id: str,
        start_index: str,
        end_index: str,
        interval: str,
        count: int = None,
        sub_second_interval: bool = False,
        verbose: bool = False,
        stored: bool = False,
    ):
        return self.dataview_get_data_pd(
            namespace_id,
            dataview_id,
            start_index,
            end_index,
            interval,
            count,
            sub_second_interval,
            verbose,
            stored,
        )

    def dataview_get_data_pd(
        self,
        namespace_id: str,
        dataview_id: str,
        start_index: str,
        end_index: str,
        interval: str,
        count: int = None,
        sub_second_interval: bool = False,
        verbose: bool = False,
        stored: bool = False,
        resume: bool = False,
        max_stored_rows=MAX_STORED_DV_ROWS,
    ):
        df = pd.DataFrame()
        next_page = None
        if not resume:
            if not sub_second_interval and not stored:
                try:
                    datetime.strptime(interval, "%H:%M:%S")
                except ValueError as e:
                    print(f"@Error: interval has invalid format: {e}")
                    return df
            try:
                parse(end_index)
                parse(start_index)
            except ValueError as e:
                print(f"@Error: start_index and/or end_index has invalid format: {e}")
                return df
            if verbose:
                summary = f"<@dataview_interpolated_pd/{dataview_id}/{start_index}/{end_index}/{interval}  t={datetime.now().isoformat()}"
                print(summary)

        else:
            if not self.remaining_data():
                print(f"@Error: no remaining data for stored dataview id {dataview_id}")
                return df
            next_page = self.__dataview_next_page

        dataview_f = self.__get_data_stored if stored else self.__get_data_interpolated
        # when GraphQL interface is in place
        # self.__get_data_interpolated_gql
        # if "cache" in self.__options

        dataview_id = self.remap_campus_dataview_id(dataview_id)

        while True:
            try:
                # print(f"[{next_page}]", end="")
                csv_or_json, next_page, _ = dataview_f(
                    namespace_id=namespace_id,
                    dataview_id=dataview_id,
                    count=count,
                    form="csvh",
                    start_index=start_index,
                    end_index=end_index,
                    interval=interval,
                    next_page=next_page,
                )
                # print(f"[{len(csv)}, {type(csv)}, {str(csv)}]", end="")
                if not stored:
                    df = df.append(
                        pd.read_csv(
                            io.StringIO(csv_or_json), parse_dates=["Timestamp"]
                        ),
                        ignore_index=True,
                    )
                else:
                    df = df.append(pd.read_json(json.dumps(csv_or_json)))
                    if len(df) >= max_stored_rows:
                        self.__dataview_next_page = next_page
                        print()
                        break

                if next_page is None:
                    print()
                    self.__dataview_next_page = None
                    break
                print("+", end="", flush=True)
            except SdsError as e:
                if not any(
                    ss in str(e) for ss in ["408:", "503:", "504:", "409:", "502:"]
                ):
                    raise e
                if "409:" in str(e):
                    print("#", end="")
                    continue
                if "408:" not in str(e):
                    print(f"[restart-{str(e)[3:6]}]", end="")
                    raise SdsError50x
                df = pd.DataFrame()
                next_page = None
                if count is None:
                    count = UXIE_CONSTANT // self.dataview_columns(
                        namespace_id, dataview_id
                    )
                count = count // 2
                print(f"@({count})", end="")
                if count < 40:
                    raise e

        return self.__process_digital_states(df)

    @backoff.on_exception(
        backoff.expo, SdsError50x, max_tries=6, jitter=backoff.full_jitter
    )
    @timer
    @typechecked
    def dataview_stored_pd(
        self,
        namespace_id: str,
        dataview_id: str,
        start_index: str,
        end_index: str,
        count: int = None,
        resume: bool = False,
        max_rows=MAX_STORED_DV_ROWS,
    ):
        try:
            result = self.dataview_get_data_pd(
                namespace_id,
                dataview_id + "_narrow",
                start_index,
                end_index,
                "",
                count=count,
                stored=True,
                resume=resume,
                max_stored_rows=max_rows,
            )
        except SdsError as e:
            if "404" in str(e):
                print(
                    f"### Error: data view with Id {dataview_id} has no version for stored data.\n"
                    "###  If data view id is correct, contact Hub support if stored data is required instead of interpolated."
                )
                return
            else:
                raise e
        return result

    def request(self, method, url, params=None, data=None, headers=None, **kwargs):
        print(dir(self))
        return self._OCSClient__baseClient.request(
            method, url, params, data, headers, **kwargs
        )

    # EXPERIMENTAL

    def remap_campus_dataview_id(self, dv_id):
        if "campus.building-" in dv_id:
            if not any(
                ss in dv_id for ss in ["-electricity", "-chilled_water", "-steam"]
            ):
                return dv_id + "-electricity"
        return dv_id

    def get_token(self):
        return self._OCSClient__baseClient._BaseClient__getToken()

    def refresh_datasets(
        self,
        hub_data="hub_datasets.json",
        additional_status="production",
        base_url="https://academichub.blob.core.windows.net/hub/datasets/",
        experimental=False,
        **kwargs,
    ):
        if experimental:
            self.refresh_datasets_experimental(hub_data, additional_status, **kwargs)
        else:
            db_file = f"{hub_data.replace('.json', '')}-{additional_status}.json"
            db = requests.get(base_url + db_file)
            if db.status_code == 200:
                with open(hub_data, "w") as f:
                    f.write(json.dumps(db.json(), indent=2))

            else:
                print(
                    f"!!! Error getting data file {db_file} at {base_url}: datasets info not updated, please retry"
                )
                return

        print(f"@ Hub data file: {hub_data}")
        self.__gqlh, self.__current_db, self.__db_index = initialize_hub_data(hub_data)
        print(f"@ Current dataset: {self.current_dataset()}")

    def refresh_datasets_experimental(
        self,
        hub_data="hub_datasets.json",
        additional_status="production",
        endpoint=GRAPHQL_ENDPOINT,
    ):
        db_query = """
query Database($status: String) {
  Database(filter: { OR: [{ status: "production" }, { status: $status }] }, orderBy: name_asc) {
    name
    asset_db
    description
    informationURL
    status
    namespace
    version
    id
    asset_with_dv(orderBy: name_asc) {
      name
      asset_id
      description
      asset_metadata
      has_dataview(filter: { ocs_sync: true }, orderBy: name_asc) {
        name
        description
        id
        asset_id
        columns
        ocs_column_key
      }
    }
  }
}
            """
        db = self.graphql_query(
            db_query, variable_values={"status": additional_status}, endpoint=endpoint
        )
        with open(hub_data, "w") as f:
            f.write(json.dumps(db, indent=2))

    def graphql_query(
        self, query_string, variable_values=None, endpoint=GRAPHQL_ENDPOINT
    ):
        sample_transport = RequestsHTTPTransport(
            url=endpoint,
            headers={"Authorization": f"Bearer {self.get_token()}"},
            verify=False,
            retries=3,
        )
        client = Client(transport=sample_transport, fetch_schema_from_transport=True)
        query = gql(query_string)
        if variable_values is None:
            variable_values = {}
        return client.execute(query, variable_values=variable_values)
