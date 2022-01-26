from __future__ import annotations

import asyncio
import datetime
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field, replace
from decimal import Decimal
from typing import Any

import aiohttp
import aiohttp.web
import pytest
from yarl import URL

from neuro_admin_client import (
    Balance,
    Cluster,
    ClusterUser,
    ClusterUserRoleType,
    Org,
    OrgCluster,
    OrgUser,
    OrgUserRoleType,
    Quota,
    User,
)


@dataclass
class ApiAddress:
    host: str
    port: int


@dataclass(frozen=True)
class Debt:
    cluster_name: str
    user_name: str
    credits: Decimal


def _parse_bool(value: str) -> bool:
    value = value.lower()
    return value in ("1", "true", "yes")


@dataclass()
class AdminServer:
    address: ApiAddress | None = None

    users: list[User] = field(default_factory=list)
    clusters: list[Cluster] = field(default_factory=list)
    orgs: list[Org] = field(default_factory=list)
    cluster_users: list[ClusterUser] = field(default_factory=list)
    org_clusters: list[OrgCluster] = field(default_factory=list)
    org_users: list[OrgUser] = field(default_factory=list)
    debts: list[Debt] = field(default_factory=list)

    @property
    def url(self) -> URL:
        assert self.address
        return URL(f"http://{self.address.host}:{self.address.port}/api/v1/")

    def _serialize_user(self, user: User) -> dict[str, Any]:
        return {
            "name": user.name,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    def _serialize_user_cluster(self, user: ClusterUser) -> dict[str, Any]:
        res = self._serialize_cluster_user(user, False)
        res.pop("user_name")
        res["cluster_name"] = user.cluster_name
        return res

    async def handle_user_post(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        payload = await request.json()
        new_user = User(
            name=payload["name"],
            email=payload["email"],
            first_name=payload["first_name"],
            last_name=payload["last_name"],
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self.users.append(new_user)
        return aiohttp.web.json_response(self._serialize_user(new_user))

    async def handle_user_get(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        user_name = request.match_info["uname"]
        for user in self.users:
            if user.name == user_name:
                payload = self._serialize_user(user)
                if "clusters" in request.query.getall("include", []):
                    payload["clusters"] = [
                        self._serialize_user_cluster(cluster_user)
                        for cluster_user in self.cluster_users
                        if cluster_user.user_name == user_name
                    ]
                return aiohttp.web.json_response(payload)
        raise aiohttp.web.HTTPNotFound

    async def handle_user_list(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        resp = [self._serialize_user(user) for user in self.users]
        return aiohttp.web.json_response(resp)

    def _serialize_org(self, org: Org) -> dict[str, Any]:
        return {
            "name": org.name,
        }

    async def handle_org_post(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        payload = await request.json()
        new_org = Org(
            name=payload["name"],
        )
        self.orgs.append(new_org)
        return aiohttp.web.json_response(self._serialize_org(new_org))

    async def handle_org_get(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        org_name = request.match_info["oname"]
        for org in self.orgs:
            if org.name == org_name:
                return aiohttp.web.json_response(self._serialize_org(org))
        raise aiohttp.web.HTTPNotFound

    async def handle_org_delete(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        org_name = request.match_info["oname"]
        for idx, org in enumerate(self.orgs):
            if org.name == org_name:
                del self.orgs[idx]
                return aiohttp.web.json_response(self._serialize_org(org))
        raise aiohttp.web.HTTPNotFound

    async def handle_org_list(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        resp = [self._serialize_org(org) for org in self.orgs]
        return aiohttp.web.json_response(resp)

    def _serialize_cluster(self, cluster: Cluster) -> dict[str, Any]:
        resp: dict[str, Any] = {
            "name": cluster.name,
            "default_quota": {},
        }
        if cluster.default_credits:
            resp["default_credits"] = str(cluster.default_credits)
        if cluster.default_quota.total_running_jobs:
            resp["default_quota"][
                "total_running_jobs"
            ] = cluster.default_quota.total_running_jobs
        return resp

    def _int_or_none(self, value: str | None) -> int | None:
        if value:
            return int(value)
        return None

    async def handle_cluster_post(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        payload = await request.json()
        default_credits_raw = payload.get("default_credits")
        default_quota_raw = payload.get("default_quota", {})
        new_cluster = Cluster(
            name=payload["name"],
            default_credits=Decimal(default_credits_raw)
            if default_credits_raw
            else None,
            default_quota=Quota(
                total_running_jobs=self._int_or_none(
                    default_quota_raw.get("total_running_jobs")
                )
            ),
        )
        self.clusters.append(new_cluster)
        return aiohttp.web.json_response(self._serialize_cluster(new_cluster))

    async def handle_cluster_put(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        payload = await request.json()

        assert cluster_name == payload["name"]

        default_credits_raw = payload.get("default_credits")
        default_quota_raw = payload.get("default_quota", {})
        changed_cluster = Cluster(
            name=payload["name"],
            default_credits=Decimal(default_credits_raw)
            if default_credits_raw
            else None,
            default_quota=Quota(
                total_running_jobs=self._int_or_none(
                    default_quota_raw.get("total_running_jobs")
                )
            ),
        )
        self.clusters = [
            cluster for cluster in self.clusters if cluster.name != changed_cluster.name
        ]
        self.clusters.append(changed_cluster)
        return aiohttp.web.json_response(self._serialize_cluster(changed_cluster))

    async def handle_cluster_get(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        for cluster in self.clusters:
            if cluster.name == cluster_name:
                return aiohttp.web.json_response(self._serialize_cluster(cluster))
        raise aiohttp.web.HTTPNotFound

    async def handle_cluster_list(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        resp = [self._serialize_cluster(cluster) for cluster in self.clusters]
        return aiohttp.web.json_response(resp)

    async def handle_cluster_delete(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        for idx, cluster in enumerate(self.clusters):
            if cluster.name == cluster_name:
                del self.clusters[idx]
                return aiohttp.web.json_response(self._serialize_cluster(cluster))
        raise aiohttp.web.HTTPNotFound

    def _serialize_cluster_user(
        self, cluster_user: ClusterUser, with_info: bool
    ) -> dict[str, Any]:
        res: dict[str, Any] = {
            "user_name": cluster_user.user_name,
            "role": cluster_user.role.value,
            "org_name": cluster_user.org_name,
            "quota": {},
            "balance": {
                "spent_credits": str(cluster_user.balance.spent_credits),
            },
        }
        if cluster_user.quota.total_running_jobs is not None:
            res["quota"]["total_running_jobs"] = cluster_user.quota.total_running_jobs
        if cluster_user.balance.credits is not None:
            res["balance"]["credits"] = str(cluster_user.balance.credits)
        if with_info:
            user = next(
                user for user in self.users if user.name == cluster_user.user_name
            )
            res["user_info"] = self._serialize_user(user)
            res["user_info"].pop("name")
        return res

    async def handle_cluster_user_post(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        payload = await request.json()
        credits_raw = payload["balance"].get("credits")
        spend_credits_raw = payload["balance"].get("spend_credits_raw")
        new_cluster_user = ClusterUser(
            cluster_name=cluster_name,
            user_name=payload["user_name"],
            role=ClusterUserRoleType(payload["role"]),
            org_name=payload.get("org_name"),
            quota=Quota(total_running_jobs=payload["quota"].get("total_running_jobs")),
            balance=Balance(
                credits=Decimal(credits_raw) if credits_raw else None,
                spent_credits=Decimal(spend_credits_raw)
                if spend_credits_raw
                else Decimal(0),
            ),
        )
        self.cluster_users.append(new_cluster_user)
        return aiohttp.web.json_response(
            self._serialize_cluster_user(
                new_cluster_user,
                _parse_bool(request.query.get("with_user_info", "false")),
            )
        )

    async def handle_cluster_user_put(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        user_name = request.match_info["uname"]
        org_name = request.match_info.get("oname")
        payload = await request.json()
        credits_raw = payload["balance"].get("credits")
        spend_credits_raw = payload["balance"].get("spend_credits_raw")

        assert user_name == payload["user_name"]
        assert org_name == payload.get("org_name")

        new_cluster_user = ClusterUser(
            cluster_name=cluster_name,
            user_name=payload["user_name"],
            role=ClusterUserRoleType(payload["role"]),
            org_name=payload.get("org_name"),
            quota=Quota(total_running_jobs=payload["quota"].get("total_running_jobs")),
            balance=Balance(
                credits=Decimal(credits_raw) if credits_raw else None,
                spent_credits=Decimal(spend_credits_raw)
                if spend_credits_raw
                else Decimal(0),
            ),
        )
        assert new_cluster_user.user_name == user_name
        self.cluster_users = [
            user
            for user in self.cluster_users
            if user.cluster_name != cluster_name
            or user.user_name != user_name
            or user.org_name != org_name
        ]
        self.cluster_users.append(new_cluster_user)
        return aiohttp.web.json_response(
            self._serialize_cluster_user(
                new_cluster_user,
                _parse_bool(request.query.get("with_user_info", "false")),
            )
        )

    async def handle_cluster_user_patch_quota(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        user_name = request.match_info["uname"]
        org_name = request.match_info.get("oname")
        payload = await request.json()

        for index, user in enumerate(self.cluster_users):
            if (
                user.cluster_name == cluster_name
                and user.user_name == user_name
                and user.org_name == org_name
            ):
                quota = user.quota
                if "quota" in payload:
                    quota = replace(
                        quota,
                        total_running_jobs=payload["quota"].get("total_running_jobs"),
                    )
                if (
                    "additional_quota" in payload
                    and quota.total_running_jobs is not None
                ):
                    quota = replace(
                        quota,
                        total_running_jobs=quota.total_running_jobs
                        + payload["additional_quota"].get("total_running_jobs"),
                    )
                user = replace(user, quota=quota)
                self.cluster_users[index] = user
                return aiohttp.web.json_response(
                    self._serialize_cluster_user(
                        user,
                        _parse_bool(request.query.get("with_user_info", "false")),
                    )
                )
        raise aiohttp.web.HTTPNotFound

    async def handle_cluster_user_patch_balance(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        user_name = request.match_info["uname"]
        org_name = request.match_info.get("oname")
        payload = await request.json()

        for index, user in enumerate(self.cluster_users):
            if (
                user.cluster_name == cluster_name
                and user.user_name == user_name
                and user.org_name == org_name
            ):
                balance = user.balance
                if "credits" in payload:
                    credits = (
                        Decimal(payload["credits"]) if payload["credits"] else None
                    )
                    balance = replace(balance, credits=credits)
                if payload.get("additional_credits") and balance.credits is not None:
                    additional_credits = Decimal(payload["additional_credits"])
                    balance = replace(
                        balance, credits=balance.credits + additional_credits
                    )
                user = replace(user, balance=balance)
                self.cluster_users[index] = user
                return aiohttp.web.json_response(
                    self._serialize_cluster_user(
                        user,
                        _parse_bool(request.query.get("with_user_info", "false")),
                    )
                )
        raise aiohttp.web.HTTPNotFound

    async def handle_cluster_user_add_spending(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        user_name = request.match_info["uname"]
        org_name = request.match_info.get("oname")
        payload = await request.json()

        for index, user in enumerate(self.cluster_users):
            if (
                user.cluster_name == cluster_name
                and user.user_name == user_name
                and user.org_name == org_name
            ):
                balance = user.balance
                spending = Decimal(payload["spending"])
                balance = replace(
                    balance, spent_credits=balance.spent_credits + spending
                )
                if balance.credits:
                    balance = replace(balance, credits=balance.credits - spending)
                user = replace(user, balance=balance)
                self.cluster_users[index] = user
                return aiohttp.web.json_response(
                    self._serialize_cluster_user(
                        user,
                        _parse_bool(request.query.get("with_user_info", "false")),
                    )
                )
        raise aiohttp.web.HTTPNotFound

    async def handle_cluster_user_add_debt(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        payload = await request.json()
        self.debts.append(
            Debt(
                cluster_name=cluster_name,
                user_name=payload["user_name"],
                credits=Decimal(payload["credits"]),
            )
        )
        raise aiohttp.web.HTTPNoContent

    async def handle_cluster_user_get(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        user_name = request.match_info["uname"]
        org_name = request.match_info.get("oname")
        for cluster_user in self.cluster_users:
            if (
                cluster_user.cluster_name == cluster_name
                and cluster_user.user_name == user_name
                and cluster_user.org_name == org_name
            ):
                return aiohttp.web.json_response(
                    self._serialize_cluster_user(
                        cluster_user,
                        _parse_bool(request.query.get("with_user_info", "false")),
                    )
                )
        raise aiohttp.web.HTTPNotFound

    async def handle_cluster_user_delete(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        user_name = request.match_info["uname"]
        org_name = request.match_info.get("oname")
        for idx, cluster_user in enumerate(self.cluster_users):
            if (
                cluster_user.cluster_name == cluster_name
                and cluster_user.user_name == user_name
                and cluster_user.org_name == org_name
            ):
                del self.cluster_users[idx]
                raise aiohttp.web.HTTPNoContent
        raise aiohttp.web.HTTPNotFound

    async def handle_cluster_user_list(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        org_name = request.match_info.get("oname")
        resp = [
            self._serialize_cluster_user(
                cluster_user, _parse_bool(request.query.get("with_user_info", "false"))
            )
            for cluster_user in self.cluster_users
            if cluster_user.cluster_name == cluster_name
            and (org_name is None or cluster_user.org_name == org_name)
        ]
        return aiohttp.web.json_response(resp)

    def _serialize_org_user(self, org_user: OrgUser, with_info: bool) -> dict[str, Any]:
        res: dict[str, Any] = {
            "user_name": org_user.user_name,
            "role": org_user.role.value,
            "org_name": org_user.org_name,
        }
        if with_info:
            user = next(user for user in self.users if user.name == org_user.user_name)
            res["user_info"] = self._serialize_user(user)
            res["user_info"].pop("name")
        return res

    async def handle_org_user_post(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        org_name = request.match_info["oname"]
        payload = await request.json()
        new_org_user = OrgUser(
            org_name=org_name,
            user_name=payload["user_name"],
            role=OrgUserRoleType(payload["role"]),
        )
        self.org_users.append(new_org_user)
        return aiohttp.web.json_response(
            self._serialize_org_user(
                new_org_user,
                _parse_bool(request.query.get("with_user_info", "false")),
            )
        )

    async def handle_org_user_put(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        org_name = request.match_info["oname"]
        user_name = request.match_info["uname"]
        payload = await request.json()
        new_org_user = OrgUser(
            org_name=org_name,
            user_name=payload["user_name"],
            role=OrgUserRoleType(payload["role"]),
        )
        assert new_org_user.user_name == user_name
        self.org_users = [
            user
            for user in self.org_users
            if user.org_name != org_name or user.user_name != user_name
        ]
        self.org_users.append(new_org_user)
        return aiohttp.web.json_response(
            self._serialize_org_user(
                new_org_user,
                _parse_bool(request.query.get("with_user_info", "false")),
            )
        )

    async def handle_org_user_get(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        org_name = request.match_info["oname"]
        user_name = request.match_info["uname"]
        for org_user in self.org_users:
            if org_user.org_name == org_name and org_user.user_name == user_name:
                return aiohttp.web.json_response(
                    self._serialize_org_user(
                        org_user,
                        _parse_bool(request.query.get("with_user_info", "false")),
                    )
                )
        raise aiohttp.web.HTTPNotFound

    async def handle_org_user_delete(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        org_name = request.match_info["oname"]
        user_name = request.match_info["uname"]
        for idx, org_user in enumerate(self.org_users):
            if org_user.org_name == org_name and org_user.user_name == user_name:
                del self.org_users[idx]
                raise aiohttp.web.HTTPNoContent
        raise aiohttp.web.HTTPNotFound

    async def handle_org_user_list(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        org_name = request.match_info["oname"]
        resp = [
            self._serialize_org_user(
                org_user, _parse_bool(request.query.get("with_user_info", "false"))
            )
            for org_user in self.org_users
            if org_user.org_name == org_name
        ]
        return aiohttp.web.json_response(resp)

    def _serialize_org_cluster(self, org_cluster: OrgCluster) -> dict[str, Any]:
        res: dict[str, Any] = {
            "org_name": org_cluster.org_name,
            "quota": {},
            "balance": {
                "spent_credits": str(org_cluster.balance.spent_credits),
            },
            "default_quota": {},
        }
        if org_cluster.quota.total_running_jobs is not None:
            res["quota"]["total_running_jobs"] = org_cluster.quota.total_running_jobs
        if org_cluster.balance.credits is not None:
            res["balance"]["credits"] = str(org_cluster.balance.credits)
        if org_cluster.default_credits:
            res["default_credits"] = str(org_cluster.default_credits)
        if org_cluster.default_quota.total_running_jobs:
            res["default_quota"][
                "total_running_jobs"
            ] = org_cluster.default_quota.total_running_jobs
        if org_cluster.storage_size_mb is not None:
            res["storage_size_mb"] = org_cluster.storage_size_mb
        return res

    async def handle_org_cluster_post(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        payload = await request.json()
        credits_raw = payload.get("balance", {}).get("credits")
        default_credits_raw = payload.get("default_credits")
        spend_credits_raw = payload.get("balance", {}).get("spend_credits_raw")
        new_org_cluster = OrgCluster(
            cluster_name=cluster_name,
            org_name=payload["org_name"],
            quota=Quota(
                total_running_jobs=payload.get("quota", {}).get("total_running_jobs")
            ),
            balance=Balance(
                credits=Decimal(credits_raw) if credits_raw else None,
                spent_credits=Decimal(spend_credits_raw)
                if spend_credits_raw
                else Decimal(0),
            ),
            default_quota=Quota(
                total_running_jobs=payload.get("default_quota", {}).get(
                    "total_running_jobs"
                )
            ),
            default_credits=Decimal(default_credits_raw)
            if default_credits_raw
            else None,
            storage_size_mb=payload.get("storage_size_mb"),
        )
        self.org_clusters.append(new_org_cluster)
        return aiohttp.web.json_response(
            self._serialize_org_cluster(
                new_org_cluster,
            )
        )

    async def handle_org_cluster_put(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        org_name = request.match_info["oname"]
        payload = await request.json()
        credits_raw = payload.get("balance", {}).get("credits")
        default_credits_raw = payload.get("default_credits")
        spend_credits_raw = payload.get("balance", {}).get("spend_credits_raw")
        new_org_cluster = OrgCluster(
            cluster_name=cluster_name,
            org_name=payload["org_name"],
            quota=Quota(
                total_running_jobs=payload.get("quota", {}).get("total_running_jobs")
            ),
            balance=Balance(
                credits=Decimal(credits_raw) if credits_raw else None,
                spent_credits=Decimal(spend_credits_raw)
                if spend_credits_raw
                else Decimal(0),
            ),
            default_quota=Quota(
                total_running_jobs=payload.get("default_quota", {}).get(
                    "total_running_jobs"
                )
            ),
            default_credits=Decimal(default_credits_raw)
            if default_credits_raw
            else None,
        )
        assert new_org_cluster.org_name == org_name
        self.org_clusters = [
            user
            for user in self.org_clusters
            if user.cluster_name != cluster_name or user.org_name != org_name
        ]
        self.org_clusters.append(new_org_cluster)
        return aiohttp.web.json_response(
            self._serialize_org_cluster(
                new_org_cluster,
            )
        )

    async def handle_org_cluster_get(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        org_name = request.match_info["oname"]
        for org_cluster in self.org_clusters:
            if (
                org_cluster.cluster_name == cluster_name
                and org_cluster.org_name == org_name
            ):
                return aiohttp.web.json_response(
                    self._serialize_org_cluster(org_cluster)
                )
        raise aiohttp.web.HTTPNotFound

    async def handle_org_cluster_delete(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        org_name = request.match_info["oname"]
        for idx, org_cluster in enumerate(self.org_clusters):
            if (
                org_cluster.cluster_name == cluster_name
                and org_cluster.org_name == org_name
            ):
                del self.org_clusters[idx]
                raise aiohttp.web.HTTPNoContent
        raise aiohttp.web.HTTPNotFound

    async def handle_org_cluster_list(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        resp = [
            self._serialize_org_cluster(org_cluster)
            for org_cluster in self.org_clusters
            if org_cluster.cluster_name == cluster_name
        ]
        return aiohttp.web.json_response(resp)

    async def handle_org_cluster_patch_quota(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        org_name = request.match_info["oname"]
        payload = await request.json()

        for index, org_cluster in enumerate(self.org_clusters):
            if (
                org_cluster.cluster_name == cluster_name
                and org_cluster.org_name == org_name
            ):
                quota = org_cluster.quota
                if "quota" in payload:
                    quota = replace(
                        quota,
                        total_running_jobs=payload["quota"].get("total_running_jobs"),
                    )
                if (
                    "additional_quota" in payload
                    and quota.total_running_jobs is not None
                ):
                    quota = replace(
                        quota,
                        total_running_jobs=quota.total_running_jobs
                        + payload["additional_quota"].get("total_running_jobs"),
                    )
                org_cluster = replace(org_cluster, quota=quota)
                self.org_clusters[index] = org_cluster
                return aiohttp.web.json_response(
                    self._serialize_org_cluster(org_cluster)
                )
        raise aiohttp.web.HTTPNotFound

    async def handle_org_cluster_patch_balance(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        cluster_name = request.match_info["cname"]
        org_name = request.match_info["oname"]
        payload = await request.json()

        for index, org_cluster in enumerate(self.org_clusters):
            if (
                org_cluster.cluster_name == cluster_name
                and org_cluster.org_name == org_name
            ):
                balance = org_cluster.balance
                if "credits" in payload:
                    credits = (
                        Decimal(payload["credits"]) if payload["credits"] else None
                    )
                    balance = replace(balance, credits=credits)
                if payload.get("additional_credits") and balance.credits is not None:
                    additional_credits = Decimal(payload["additional_credits"])
                    balance = replace(
                        balance, credits=balance.credits + additional_credits
                    )
                org_cluster = replace(org_cluster, balance=balance)
                self.org_clusters[index] = org_cluster
                return aiohttp.web.json_response(
                    self._serialize_org_cluster(
                        org_cluster,
                    )
                )
        raise aiohttp.web.HTTPNotFound


@pytest.fixture
async def mock_admin_server(
    loop: asyncio.AbstractEventLoop,
) -> AsyncIterator[AdminServer]:
    admin_server = AdminServer()

    def _create_app() -> aiohttp.web.Application:
        app = aiohttp.web.Application()
        app.router.add_routes(
            (
                aiohttp.web.get(
                    "/api/v1/users",
                    admin_server.handle_user_list,
                ),
                aiohttp.web.post(
                    "/api/v1/users",
                    admin_server.handle_user_post,
                ),
                aiohttp.web.get(
                    "/api/v1/users/{uname}",
                    admin_server.handle_user_get,
                ),
                aiohttp.web.get(
                    "/api/v1/orgs",
                    admin_server.handle_org_list,
                ),
                aiohttp.web.post(
                    "/api/v1/orgs",
                    admin_server.handle_org_post,
                ),
                aiohttp.web.get(
                    "/api/v1/orgs/{oname}",
                    admin_server.handle_org_get,
                ),
                aiohttp.web.delete(
                    "/api/v1/orgs/{oname}",
                    admin_server.handle_org_delete,
                ),
                aiohttp.web.get(
                    "/api/v1/clusters",
                    admin_server.handle_cluster_list,
                ),
                aiohttp.web.post(
                    "/api/v1/clusters",
                    admin_server.handle_cluster_post,
                ),
                aiohttp.web.get(
                    "/api/v1/clusters/{cname}",
                    admin_server.handle_cluster_get,
                ),
                aiohttp.web.put(
                    "/api/v1/clusters/{cname}",
                    admin_server.handle_cluster_put,
                ),
                aiohttp.web.delete(
                    "/api/v1/clusters/{cname}",
                    admin_server.handle_cluster_delete,
                ),
                aiohttp.web.post(
                    "/api/v1/clusters/{cname}/users",
                    admin_server.handle_cluster_user_post,
                ),
                aiohttp.web.get(
                    "/api/v1/clusters/{cname}/users",
                    admin_server.handle_cluster_user_list,
                ),
                aiohttp.web.get(
                    "/api/v1/clusters/{cname}/users/{uname}",
                    admin_server.handle_cluster_user_get,
                ),
                aiohttp.web.put(
                    "/api/v1/clusters/{cname}/users/{uname}",
                    admin_server.handle_cluster_user_put,
                ),
                aiohttp.web.delete(
                    "/api/v1/clusters/{cname}/users/{uname}",
                    admin_server.handle_cluster_user_delete,
                ),
                aiohttp.web.patch(
                    "/api/v1/clusters/{cname}/users/{uname}/balance",
                    admin_server.handle_cluster_user_patch_balance,
                ),
                aiohttp.web.patch(
                    "/api/v1/clusters/{cname}/users/{uname}/quota",
                    admin_server.handle_cluster_user_patch_quota,
                ),
                aiohttp.web.post(
                    "/api/v1/clusters/{cname}/users/{uname}/spending",
                    admin_server.handle_cluster_user_add_spending,
                ),
                aiohttp.web.post(
                    "/api/v1/clusters/{cname}/debts",
                    admin_server.handle_cluster_user_add_debt,
                ),
                aiohttp.web.post(
                    "/api/v1/orgs/{oname}/users",
                    admin_server.handle_org_user_post,
                ),
                aiohttp.web.get(
                    "/api/v1/orgs/{oname}/users",
                    admin_server.handle_org_user_list,
                ),
                aiohttp.web.get(
                    "/api/v1/orgs/{oname}/users/{uname}",
                    admin_server.handle_org_user_get,
                ),
                aiohttp.web.put(
                    "/api/v1/orgs/{oname}/users/{uname}",
                    admin_server.handle_org_user_put,
                ),
                aiohttp.web.delete(
                    "/api/v1/orgs/{oname}/users/{uname}",
                    admin_server.handle_org_user_delete,
                ),
                aiohttp.web.post(
                    "/api/v1/clusters/{cname}/orgs",
                    admin_server.handle_org_cluster_post,
                ),
                aiohttp.web.get(
                    "/api/v1/clusters/{cname}/orgs",
                    admin_server.handle_org_cluster_list,
                ),
                aiohttp.web.get(
                    "/api/v1/clusters/{cname}/orgs/{oname}",
                    admin_server.handle_org_cluster_get,
                ),
                aiohttp.web.put(
                    "/api/v1/clusters/{cname}/orgs/{oname}",
                    admin_server.handle_org_cluster_put,
                ),
                aiohttp.web.delete(
                    "/api/v1/clusters/{cname}/orgs/{oname}",
                    admin_server.handle_org_cluster_delete,
                ),
                # org user endpoints:
                aiohttp.web.get(
                    "/api/v1/clusters/{cname}/orgs/{oname}/users",
                    admin_server.handle_cluster_user_list,
                ),
                aiohttp.web.get(
                    "/api/v1/clusters/{cname}/orgs/{oname}/users/{uname}",
                    admin_server.handle_cluster_user_get,
                ),
                aiohttp.web.put(
                    "/api/v1/clusters/{cname}/orgs/{oname}/users/{uname}",
                    admin_server.handle_cluster_user_put,
                ),
                aiohttp.web.delete(
                    "/api/v1/clusters/{cname}/orgs/{oname}/users/{uname}",
                    admin_server.handle_cluster_user_delete,
                ),
                aiohttp.web.patch(
                    "/api/v1/clusters/{cname}/orgs/{oname}/users/{uname}/balance",
                    admin_server.handle_cluster_user_patch_balance,
                ),
                aiohttp.web.patch(
                    "/api/v1/clusters/{cname}/orgs/{oname}/users/{uname}/quota",
                    admin_server.handle_cluster_user_patch_quota,
                ),
                aiohttp.web.post(
                    "/api/v1/clusters/{cname}/orgs/{oname}/users/{uname}/spending",
                    admin_server.handle_cluster_user_add_spending,
                ),
                # patch org quota endpoints:
                aiohttp.web.patch(
                    "/api/v1/clusters/{cname}/orgs/{oname}/balance",
                    admin_server.handle_org_cluster_patch_balance,
                ),
                aiohttp.web.patch(
                    "/api/v1/clusters/{cname}/orgs/{oname}/quota",
                    admin_server.handle_org_cluster_patch_quota,
                ),
            )
        )
        return app

    app = _create_app()
    runner = ApiRunner(app, port=8085)
    api_address = await runner.run()
    admin_server.address = api_address
    yield admin_server
    await runner.close()


@pytest.fixture
def admin_url(
    mock_admin_server: AdminServer,
) -> URL:
    return mock_admin_server.url


@asynccontextmanager
async def create_local_app_server(
    app: aiohttp.web.Application, port: int = 8080
) -> AsyncIterator[ApiAddress]:
    runner = aiohttp.web.AppRunner(app)
    try:
        await runner.setup()
        api_address = ApiAddress("0.0.0.0", port)
        site = aiohttp.web.TCPSite(runner, api_address.host, api_address.port)
        await site.start()
        yield api_address
    finally:
        await runner.shutdown()
        await runner.cleanup()


class ApiRunner:
    def __init__(self, app: aiohttp.web.Application, port: int) -> None:
        self._app = app
        self._port = port

        self._api_address_future: asyncio.Future[ApiAddress] = asyncio.Future()
        self._cleanup_future: asyncio.Future[None] = asyncio.Future()
        self._task: asyncio.Task[None] | None = None

    async def _run(self) -> None:
        async with create_local_app_server(self._app, port=self._port) as api_address:
            self._api_address_future.set_result(api_address)
            await self._cleanup_future

    async def run(self) -> ApiAddress:
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._run())
        return await self._api_address_future

    async def close(self) -> None:
        if self._task:
            task = self._task
            self._task = None
            self._cleanup_future.set_result(None)
            await task

    @property
    def closed(self) -> bool:
        return not bool(self._task)
