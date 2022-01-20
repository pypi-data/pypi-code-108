import os
import time
import logging
import awswrangler as wr
import boto3
import python_graphql_client
import pandas as pd
import requests
from datetime import datetime
from typing import Optional, Dict, List

from requests.auth import AuthBase
from sumatra.auth import SDKKeyAuth, CognitoJwtAuth
from sumatra.config import CONFIG

logger = logging.getLogger("sumatra.client")


def parse_timestamp_columns(df, columns):
    df = df.copy()
    for col in columns:
        df[col] = pd.to_datetime(df[col], unit="ns")
        if df[col].dt.tz is None:
            df[col] = df[col].dt.tz_localize("UTC")
        df[col] = df[col].dt.tz_convert(CONFIG.timezone)
    return df


def tz_convert_timestamp_columns(df):
    df = df.copy()
    for col in df.columns:
        if hasattr(df[col], "dt"):
            df[col] = df[col].dt.tz_localize("UTC").dt.tz_convert(CONFIG.timezone)
    return df


def _load_scowl_files(dir: str) -> Dict[str, str]:
    scowls = {}
    for fname in os.listdir(dir):
        if fname.endswith(".scowl"):
            scowl = open(os.path.join(dir, fname)).read()
            scowls[fname] = scowl
    return scowls


class Client:
    def __init__(
        self,
        instance: Optional[str] = None,
        branch: Optional[str] = None,
    ):
        if instance:
            CONFIG.instance = instance
        if CONFIG.sdk_key:
            auth: AuthBase = SDKKeyAuth()
            endpoint = CONFIG.sdk_graphql_url
        else:
            auth = CognitoJwtAuth()
            endpoint = CONFIG.console_graphql_url

        self.branch = branch or CONFIG.default_branch
        self._tenant = None

        self._gql_client = python_graphql_client.GraphqlClient(
            auth=auth, endpoint=endpoint
        )

    @property
    def tenant(self):
        if self._tenant is None:
            self._tenant = self._fetch_tenant()
        return self._tenant

    def _fetch_tenant(self):
        logger.debug("Fetching tenant")
        query = """
            query Tenant {
                tenant {
                    key
                }
            }
        """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["tenant"]["key"]

    def get_branch(self, branch: Optional[str] = None) -> pd.Series:
        branch = branch or self.branch
        logger.info(f"Getting branch {branch}")
        query = """
            query BranchScowl($id: String!) { 
              branch(id: $id) { id, hash, events, creator, lastUpdated, error } 
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": branch})

        if "errors" in ret:
            raise Exception(f"Error: {ret['errors'][0]['message']}")

        branch = ret["data"]["branch"]
        row = {
            "name": branch["id"],
            "creator": branch["creator"],
            "update_ts": branch["lastUpdated"],
            "event_types": branch["events"],
        }

        if "error" in branch and branch["error"]:
            row["error"] = branch["error"]

        return row

    def clone_branch(self, dest: str, branch: Optional[str] = None) -> str:
        branch = branch or self.branch
        logger.info(f"Cloning branch {branch} to {dest}")
        query = """
            mutation CloneBranch($id: String!, $sourceId: String!) {
                cloneBranch(id: $id, sourceId: $sourceId) { id, creator, lastUpdated, scowl }
              }
        """

        ret = self._gql_client.execute(
            query=query, variables={"id": dest, "sourceId": branch}
        )

        if "errors" in ret:
            raise Exception(f"Error: {ret['errors'][0]['message']}")

        destId = ret["data"]["cloneBranch"]["id"]
        return destId

    def put_branch_object(
        self, key: str, scowl: str, branch: Optional[str] = None
    ) -> str:
        branch = branch or self.branch
        logger.info(f"Putting branch object {key} to branch {branch}")
        query = """
              mutation PutBranchObject($branchId: String!, $key: String!, $scowl: String!) {
                putBranchObject(branchId: $branchId, key: $key, scowl: $scowl) { key }
              }
        """

        ret = self._gql_client.execute(
            query=query, variables={"branchId": branch, "key": key, "scowl": scowl}
        )

        if "errors" in ret:
            raise Exception(f"Error: {ret['errors'][0]['message']}")

        key = ret["data"]["putBranchObject"]["key"]
        return key

    def create_branch_from_scowl(self, scowl: str, branch: Optional[str] = None) -> str:
        branch = branch or self.branch
        logger.info(f"Creating branch '{branch}' from scowl")
        try:
            self.delete_branch(branch)
        except:
            pass

        self.put_branch_object("main.scowl", scowl, branch)

        b = self.get_branch(branch)
        if "error" in b:
            raise Exception(b["error"])

        return b["name"]

    def create_branch_from_dir(
        self, scowl_dir: Optional[str] = None, branch: Optional[str] = None
    ) -> str:
        scowl_dir = scowl_dir or CONFIG.scowl_dir
        branch = branch or self.branch
        logger.info(f"Creating branch '{branch}' from dir '{scowl_dir}'")

        try:
            self.delete_branch(branch)
        except:
            pass

        scowls = _load_scowl_files(scowl_dir)
        if not scowls:
            raise Exception(
                f"Unable to push local dir. '{scowl_dir}' has no .scowl files."
            )

        for key in scowls:
            self.put_branch_object(key, scowls[key], branch)

        b = self.get_branch(branch)
        if "error" in b:
            raise Exception(b["error"])

        return b["name"]

    def publish_dir(self, scowl_dir: Optional[str] = None) -> None:
        scowl_dir = scowl_dir or CONFIG.scowl_dir
        logger.info(f"Publishing dir '{scowl_dir}' to LIVE.")
        branch = "main"
        self.create_branch_from_dir(scowl_dir, branch)
        self.publish_branch(branch)

    def publish_branch(self, branch: Optional[str] = None) -> None:
        branch = branch or self.branch
        logger.info(f"Publishing '{branch}' branch to LIVE.")
        query = """
            mutation PublishBranch($id: String!) {
                publish(id: $id) {
                    id
                }
            }
        """
        ret = self._gql_client.execute(query=query, variables={"id": branch})

        if "errors" in ret:
            raise Exception(
                f"Error publishing branch '{branch}': {ret['errors'][0]['message']}"
            )

    def publish_scowl(self, scowl: str) -> None:
        logger.info("Publishing scowl to LIVE.")
        branch = "main"
        self.create_branch_from_scowl(scowl, branch)
        self.publish_branch(branch)

    def diff_branch_with_live(self, branch: Optional[str] = None) -> Dict:
        branch = branch or self.branch
        logger.info(f"Diffing '{branch}' branch against LIVE.")
        query = """
            query Branch($id: String!) {
                branch(id: $id) {
                liveDiff {
                    eventsAdded
                    eventsDeleted
                    topologyDiffs {
                        eventType
                        featuresDeleted
                        featuresAdded
                        featuresRedefined
                        featuresDirtied
                    }
                    warnings
                }
              }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": branch})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["branch"]["liveDiff"]

    def get_branches(self) -> pd.DataFrame:
        logger.debug(f"Getting branches")
        query = """
            query BranchList {
                branches {
                    id
                    events
                    error
                    creator
                    lastUpdated
                }
            }
        """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        rows = []
        for branch in ret["data"]["branches"]:
            row = {
                "name": branch["id"],
                "creator": branch["creator"],
                "update_ts": branch["lastUpdated"],
                "event_types": branch["events"],
            }
            if branch["error"]:
                row["error"] = branch["error"]

            rows.append(row)
        if not rows:
            return pd.DataFrame(columns=["name", "creator", "update_ts", "event_types"])
        df = pd.DataFrame(rows)
        df = parse_timestamp_columns(df, ["update_ts"])
        return df.sort_values(["creator", "update_ts"], ascending=False).set_index(
            "name"
        )

    def get_live_scowl(self):
        query = """
            query LiveScowl {
                liveBranch { scowl }
            }
        """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        scowl = ret["data"]["liveBranch"]["scowl"]
        return scowl

    def delete_branch(self, branch: Optional[str] = None) -> str:
        branch = branch or self.branch
        logger.info(f"Deleting branch '{branch}'.")
        query = """
            mutation DeleteBranch($id: String!) {
                deleteBranch(id: $id) {
                    id
                }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": branch})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])
        return branch

    def get_timelines(self):
        logger.debug(f"Getting timelines")
        query = """
            query TimelineList {
                timelines { id, createUser, createTime, metadata { start, end, count, events }, source, state, error }
            }
        """
        ret = self._gql_client.execute(query)
        rows = []
        for timeline in ret["data"]["timelines"]:
            status = timeline["state"]
            row = {
                "name": timeline["id"],
                "creator": timeline["createUser"],
                "create_ts": timeline["createTime"],
                "event_types": timeline["metadata"]["events"],
                "event_count": timeline["metadata"]["count"],
                "start_ts": timeline["metadata"]["start"]
                if timeline["metadata"]["start"] != "0001-01-01T00:00:00Z"
                else "",
                "end_ts": timeline["metadata"]["end"]
                if timeline["metadata"]["end"] != "0001-01-01T00:00:00Z"
                else "",
                "source": timeline["source"],
                "status": status,
                "error": timeline["error"],
            }
            rows.append(row)
        if not rows:
            return pd.DataFrame(
                columns=[
                    "name",
                    "creator",
                    "create_ts",
                    "event_types",
                    "event_count",
                    "start_ts",
                    "end_ts",
                    "source",
                    "status",
                    "error",
                ]
            )
        df = pd.DataFrame(rows)
        df = parse_timestamp_columns(df, ["create_ts", "start_ts", "end_ts"])
        return df.sort_values(["creator", "create_ts"], ascending=False).set_index(
            "name"
        )

    def get_timeline(self, timeline: str) -> pd.Series:
        logger.debug(f"Getting timeline '{timeline}'")
        timelines = self.get_timelines()
        if timeline in timelines.index:
            return timelines.loc[timeline]
        raise Exception(f"Timeline '{timeline}' not found.")

    def delete_timeline(self, timeline: str) -> str:
        logger.info(f"Deleting timeline '{timeline}'.")
        query = """
            mutation DeleteTimeline($id: String!) {
                deleteTimeline(id: $id) {
                    id
                }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": timeline})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])
        return timeline

    def infer_schema_from_timeline(self, timeline: str) -> str:
        query = """
            query TimelineScowl($id: String!) {
                timeline(id: $id) { id, scowl }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": timeline})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])
        return ret["data"]["timeline"]["scowl"]

    def create_timeline_from_dataframes(self, df_dict, timeline, timestamp_column=None):
        jsonl = ""
        for event_type, df in df_dict.items():
            jsonl += self._df_to_jsonl(df, event_type, timestamp_column)
        return self.create_timeline_from_jsonl(jsonl, timeline)

    def create_timeline_from_jsonl(self, jsonl, timeline):
        query = """
            mutation SaveTimelineMutation($id: String!,
                                          $filename: String!) {
                saveTimeline(id: $id, source: "file", state: "new") {
                    uploadUrl(name: $filename)
                }
            }
        """

        ret = self._gql_client.execute(
            query=query, variables={"id": timeline, "filename": "sdk.jsonl"}
        )
        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        url = ret["data"]["saveTimeline"]["uploadUrl"]

        if not jsonl.endswith("\n"):
            jsonl += "\n"
        http_response = requests.put(url, data=jsonl)
        if http_response.status_code != 200:
            raise Exception(http_response.error)

        query = """
            mutation SaveTimelineMutation($id: String!) {
                saveTimeline(id: $id, source: "file", state: "processing") {
                    id
                }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": timeline})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        retry_count = 0
        while retry_count < 60:
            tl = self.get_timeline(timeline)
            if tl.status == "processing":
                time.sleep(5.0)
                retry_count += 1
            else:
                break

        return tl.name

    def _df_to_jsonl(self, df, event_type, timestamp_column=None):
        df = df.copy()
        df["_type"] = event_type
        if timestamp_column:
            df.rename(columns={timestamp_column: "_time"}, inplace=True)
        if "_time" not in df.columns:
            df["_time"] = datetime.utcnow()
        df.sort_values("_time", inplace=True)
        jsonl = df.to_json(orient="records", lines=True, date_format="iso")
        if not jsonl.endswith("\n"):
            jsonl += "\n"
        return jsonl

    def materialize(self, timeline: str, branch: Optional[str] = None):
        return self.materialize_many([timeline], branch)

    def materialize_many(self, timelines: List[str], branch: Optional[str] = None):
        branch = branch or self.branch
        query = """
            mutation Materialize($timelines: [String], $branch: String!) {
                materialize(timelines: $timelines, branch: $branch) { id }
            }
        """

        ret = self._gql_client.execute(
            query=query, variables={"timelines": timelines, "branch": branch}
        )

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return Materialization(self, ret["data"]["materialize"]["id"])

    def get_models(self):
        query = """
                    query ModelList {
                        models { id, name, version, creator }
                    }
                """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        rows = []
        for model in ret["data"]["models"]:
            row = {
                "id": model["id"],
                "name": model["name"],
                "version": model["version"],
                "creator": model["creator"],
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        return df.sort_values(
            ["creator", "name", "version"], ascending=False
        ).set_index("id")

    def put_model(self, name, version, file):
        query = """
                    mutation PutModel($name: String!, $version: String!) {
                        putModel (name: $name, version: $version) { id, name, version, uploadUri }
                    }
                """

        ret = self._gql_client.execute(
            query=query, variables={"name": name, "version": version}
        )
        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        uploadUri = ret["data"]["putModel"]["uploadUri"]

        with open(file, "rb") as f:
            files = {"file": (file, f)}
            http_response = requests.put(uploadUri, files=files)
            if http_response.status_code != 200:
                raise Exception(http_response.error)

        return ret["data"]["putModel"]["id"]

    def version(self):
        query = """
            query Version {
                version
            }
        """

        ret = self._gql_client.execute(query=query)
        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["version"]

    def get_session(self):
        query = """
                    query TempCredentials {
                        tenant { credentials }
                    }
                """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        creds = ret["data"]["tenant"]["credentials"]

        return boto3.Session(
            aws_access_key_id=creds["AccessKeyID"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

    @property
    def s3_client(self):
        return self._s3_client


class Materialization:
    def __init__(self, client, id):
        self._client = client
        self.id = id
        self._mtr = None

    def __repr__(self):
        return f"Materialization(id='{self.id}')"

    def _get_materialization(self):
        query = """
            query Materialization($id: String!) {
                materialization(id: $id) { id, timelines, branch, hash, state, path }
            }
        """

        ret = self._client._gql_client.execute(query=query, variables={"id": self.id})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["materialization"]

    def _wait_for_processing(self):
        RETRIES = 60
        DELAY = 5.0
        retry_count = 0
        while retry_count < RETRIES:
            if self.status != "processing":
                return
            time.sleep(DELAY)
            retry_count += 1
        if self.status == "processing":
            raise Exception(f"Timed out after {DELAY * RETRIES} seconds")

    @property
    def status(self):
        self._mtr = self._get_materialization()
        return self._mtr["state"]

    @property
    def timelines(self):
        self._wait_for_processing()
        return self._mtr["timelines"]

    @property
    def branch(self):
        self._wait_for_processing()
        return self._mtr["branch"]

    @property
    def hash(self):
        self._wait_for_processing()
        return self._mtr["hash"]

    @property
    def path(self):
        self._wait_for_processing()
        return self._mtr["path"]

    def get_events(self, event_type, features=[]):
        self._wait_for_processing()
        session = self._client.get_session()

        if not features:
            df = wr.s3.read_parquet(
                boto3_session=session,
                path=f"{self.path}/{event_type}.parquet",
                use_threads=8,
            )
        else:
            cols = ["_id", "_type", "_time"]
            cols.extend(features)
            df = wr.s3.read_parquet(
                boto3_session=session,
                path=f"{self.path}/{event_type}.parquet",
                columns=cols,
                use_threads=8,
            )

        df = tz_convert_timestamp_columns(df)
        return df.set_index("_id")

    def get_errors(self, event_type, features=[]):
        self._wait_for_processing()
        session = self._client.get_session()

        path = f"{self.path}/{event_type}.errors.parquet"
        cols = ["_id", "_type", "_time"]
        cols.extend(features)

        try:
            if not features:
                df = wr.s3.read_parquet(
                    boto3_session=session,
                    path=path,
                    ignore_empty=True,
                )
            else:
                df = wr.s3.read_parquet(
                    boto3_session=session,
                    path=path,
                    columns=cols,
                    ignore_empty=True,
                )
        except Exception as e:
            logger.debug(e)
            return pd.DataFrame(columns=cols)

        df = tz_convert_timestamp_columns(df)
        return df.set_index("_id")
