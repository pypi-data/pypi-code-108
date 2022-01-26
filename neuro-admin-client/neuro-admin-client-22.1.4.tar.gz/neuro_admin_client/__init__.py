from __future__ import annotations

import abc
from abc import abstractmethod
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import Any, overload

import aiohttp
from multidict import CIMultiDict
from typing_extensions import Literal
from yarl import URL

from neuro_admin_client.entities import (
    Balance,
    Cluster,
    ClusterUser,
    ClusterUserRoleType,
    ClusterUserWithInfo,
    Org,
    OrgCluster,
    OrgUser,
    OrgUserRoleType,
    OrgUserWithInfo,
    Quota,
    User,
    UserInfo,
)


def _to_query_bool(flag: bool) -> str:
    return str(flag).lower()


class AdminClientABC(abc.ABC):
    async def __aenter__(self) -> "AdminClientABC":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass

    async def aclose(self) -> None:
        pass

    @abstractmethod
    async def list_users(self) -> list[User]:
        ...

    @abstractmethod
    async def get_user(self, name: str) -> User:
        ...

    @abstractmethod
    async def get_user_with_clusters(self, name: str) -> tuple[User, list[ClusterUser]]:
        ...

    @abstractmethod
    async def create_user(
        self,
        name: str,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        ...

    @abstractmethod
    async def update_user(
        self,
        user: User,
    ) -> None:
        ...

    @abstractmethod
    async def list_clusters(self) -> list[Cluster]:
        ...

    @abstractmethod
    async def get_cluster(self, name: str) -> Cluster:
        ...

    @abstractmethod
    async def create_cluster(
        self,
        name: str,
        default_credits: Decimal | None = None,
        default_quota: Quota = Quota(),
    ) -> Cluster:
        ...

    @abstractmethod
    async def update_cluster(
        self,
        cluster: Cluster,
    ) -> None:
        ...

    @abstractmethod
    async def delete_cluster(self, name: str) -> Cluster:
        ...

    @overload
    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: Literal[True],
        org_name: str | None = None,
    ) -> list[ClusterUserWithInfo]:
        ...

    @overload
    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: Literal[False] = ...,
        org_name: str | None = None,
    ) -> list[ClusterUser]:
        ...

    @abstractmethod
    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> list[ClusterUser] | list[ClusterUserWithInfo]:
        ...

    @overload
    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: Literal[True] = ...,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: Literal[False] = ...,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    @abstractmethod
    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        ...

    @overload
    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        with_user_info: Literal[True],
        quota: Quota | None = None,
        balance: Balance | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        with_user_info: Literal[False] = ...,
        quota: Quota | None = None,
        balance: Balance | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        quota: Quota | None = None,
        balance: Balance | None = None,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: Literal[True]
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: Literal[False] = ...
    ) -> ClusterUser:
        ...

    @abstractmethod
    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: bool = False
    ) -> ClusterUser | ClusterUserWithInfo:
        ...

    @abstractmethod
    async def delete_cluster_user(
        self, cluster_name: str, user_name: str, org_name: str | None = None
    ) -> None:
        ...

    @overload
    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    @abstractmethod
    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    @abstractmethod
    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    @abstractmethod
    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    @abstractmethod
    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        ...

    @overload
    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    @abstractmethod
    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        ...

    @abstractmethod
    async def create_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
        quota: Quota = Quota(),
        balance: Balance = Balance(),
        default_quota: Quota = Quota(),
        default_credits: Decimal | None = None,
        storage_size_mb: int | None = None,
    ) -> OrgCluster:
        ...

    @abstractmethod
    async def list_org_clusters(self, cluster_name: str) -> list[OrgCluster]:
        ...

    @abstractmethod
    async def get_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
    ) -> OrgCluster:
        ...

    @abstractmethod
    async def update_org_cluster(self, org_cluster: OrgCluster) -> None:
        ...

    @abstractmethod
    async def delete_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
    ) -> None:
        ...

    @abstractmethod
    async def update_org_cluster_quota(
        self,
        cluster_name: str,
        org_name: str,
        quota: Quota,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        ...

    @abstractmethod
    async def update_org_cluster_quota_by_delta(
        self,
        cluster_name: str,
        org_name: str,
        delta: Quota,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        ...

    @abstractmethod
    async def update_org_cluster_balance(
        self,
        cluster_name: str,
        org_name: str,
        credits: Decimal | None,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        ...

    @abstractmethod
    async def update_org_cluster_balance_by_delta(
        self,
        cluster_name: str,
        org_name: str,
        delta: Decimal,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        ...

    @abstractmethod
    async def list_orgs(self) -> list[Org]:
        ...

    @abstractmethod
    async def get_org(self, name: str) -> Org:
        ...

    @abstractmethod
    async def create_org(
        self,
        name: str,
    ) -> Org:
        ...

    @abstractmethod
    async def delete_org(self, name: str) -> Org:
        ...

    #  org user

    @overload
    async def list_org_users(
        self, org_name: str, with_user_info: Literal[True]
    ) -> list[OrgUserWithInfo]:
        ...

    @overload
    async def list_org_users(
        self, org_name: str, with_user_info: Literal[False] = ...
    ) -> list[OrgUser]:
        ...

    @abstractmethod
    async def list_org_users(
        self, org_name: str, with_user_info: bool = False
    ) -> list[OrgUser] | list[OrgUserWithInfo]:
        ...

    @overload
    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: Literal[True]
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: Literal[False] = ...
    ) -> OrgUser:
        ...

    @abstractmethod
    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: bool = False
    ) -> OrgUser | OrgUserWithInfo:
        ...

    @overload
    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: Literal[True],
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: Literal[False] = ...,
    ) -> OrgUser:
        ...

    @abstractmethod
    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: bool = False,
    ) -> OrgUser | OrgUserWithInfo:
        ...

    @overload
    async def update_org_user(
        self, org_user: OrgUser, with_user_info: Literal[True]
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def update_org_user(
        self, org_user: OrgUser, with_user_info: Literal[False] = ...
    ) -> OrgUser:
        ...

    @abstractmethod
    async def update_org_user(
        self, org_user: OrgUser, with_user_info: bool = False
    ) -> OrgUser | OrgUserWithInfo:
        ...

    @abstractmethod
    async def delete_org_user(self, org_name: str, user_name: str) -> None:
        ...

    # OLD API:

    @abstractmethod
    async def add_debt(
        self,
        cluster_name: str,
        username: str,
        credits: Decimal,
        idempotency_key: str,
    ) -> None:
        ...


class AdminClientBase:
    @abc.abstractmethod
    def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: Mapping[str, str] | None = None,
    ) -> AbstractAsyncContextManager[aiohttp.ClientResponse]:
        pass

    def _parse_user_payload(self, payload: dict[str, Any]) -> User:
        created_at = payload.get("created_at")
        return User(
            name=payload["name"],
            email=payload["email"],
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            created_at=datetime.fromisoformat(created_at) if created_at else None,
        )

    def _parse_user_info_payload(self, payload: dict[str, Any]) -> UserInfo:
        created_at = payload.get("created_at")
        return UserInfo(
            email=payload["email"],
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            created_at=datetime.fromisoformat(created_at) if created_at else None,
        )

    def _parse_user_cluster_payload(
        self, payload: dict[str, Any], user_name: str
    ) -> ClusterUser:
        return ClusterUser(
            user_name=user_name,
            role=ClusterUserRoleType(payload["role"]),
            quota=self._parse_quota(payload.get("quota")),
            balance=self._parse_balance(payload.get("balance")),
            org_name=payload.get("org_name"),
            cluster_name=payload["cluster_name"],
        )

    async def list_users(self) -> list[User]:
        async with self._request("GET", "users") as resp:
            resp.raise_for_status()
            users_raw = await resp.json()
            users = [self._parse_user_payload(raw_user) for raw_user in users_raw]
        return users

    async def get_user(self, name: str) -> User:
        async with self._request("GET", f"users/{name}") as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_user_payload(raw_user)

    async def get_user_with_clusters(self, name: str) -> tuple[User, list[ClusterUser]]:
        async with self._request(
            "GET", f"users/{name}", params={"include": "clusters"}
        ) as resp:
            resp.raise_for_status()
            payload = await resp.json()
            user = self._parse_user_payload(payload)
            clusters = [
                self._parse_user_cluster_payload(user_cluster_raw, user.name)
                for user_cluster_raw in payload["clusters"]
            ]
        return user, clusters

    async def create_user(
        self,
        name: str,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        payload = {
            "name": name,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
        async with self._request("POST", "users", json=payload) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_user_payload(raw_user)

    async def update_user(
        self,
        user: User,
    ) -> None:
        payload = {
            "name": user.name,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        async with self._request("PUT", f"users/{user.name}", json=payload) as resp:
            resp.raise_for_status()

    def _parse_cluster_payload(self, payload: dict[str, Any]) -> Cluster:
        return Cluster(
            name=payload["name"],
            default_credits=Decimal(payload["default_credits"])
            if payload.get("default_credits")
            else None,
            default_quota=self._parse_quota(payload.get("default_quota")),
        )

    async def list_clusters(self) -> list[Cluster]:
        async with self._request("GET", "clusters") as resp:
            resp.raise_for_status()
            clusters_raw = await resp.json()
            clusters = [
                self._parse_cluster_payload(raw_user) for raw_user in clusters_raw
            ]
        return clusters

    async def get_cluster(self, name: str) -> Cluster:
        async with self._request("GET", f"clusters/{name}") as resp:
            resp.raise_for_status()
            raw_cluster = await resp.json()
            return self._parse_cluster_payload(raw_cluster)

    async def create_cluster(
        self,
        name: str,
        default_credits: Decimal | None = None,
        default_quota: Quota = Quota(),
    ) -> Cluster:
        payload: dict[str, Any] = {
            "name": name,
            "default_quota": {},
        }
        if default_credits:
            payload["default_credits"] = str(default_credits)
        if default_quota.total_running_jobs:
            payload["default_quota"]["total_running_jobs"] = str(
                default_quota.total_running_jobs
            )
        async with self._request("POST", "clusters", json=payload) as resp:
            resp.raise_for_status()
            raw_cluster = await resp.json()
            return self._parse_cluster_payload(raw_cluster)

    async def update_cluster(
        self,
        cluster: Cluster,
    ) -> None:
        payload: dict[str, Any] = {
            "name": cluster.name,
        }
        if cluster.default_credits:
            payload["default_credits"] = str(cluster.default_credits)
        if cluster.default_quota.total_running_jobs:
            payload["default_quota"] = {
                "total_running_jobs": str(cluster.default_quota.total_running_jobs)
            }
        async with self._request(
            "PUT", f"clusters/{cluster.name}", json=payload
        ) as resp:
            resp.raise_for_status()

    async def delete_cluster(self, name: str) -> Cluster:
        async with self._request("DELETE", f"clusters/{name}") as resp:
            resp.raise_for_status()
            raw_cluster = await resp.json()
            return self._parse_cluster_payload(raw_cluster)

    def _parse_quota(self, payload: dict[str, Any] | None) -> Quota:
        if payload is None:
            return Quota()
        return Quota(total_running_jobs=payload.get("total_running_jobs"))

    def _parse_balance(self, payload: dict[str, Any] | None) -> Balance:
        if payload is None:
            return Balance()
        return Balance(
            spent_credits=Decimal(payload["spent_credits"]),
            credits=Decimal(payload["credits"]) if payload.get("credits") else None,
        )

    def _parse_cluster_user(
        self, cluster_name: str, payload: dict[str, Any]
    ) -> ClusterUser | ClusterUserWithInfo:
        cluster_user = ClusterUser(
            user_name=payload["user_name"],
            role=ClusterUserRoleType(payload["role"]),
            quota=self._parse_quota(payload.get("quota")),
            balance=self._parse_balance(payload.get("balance")),
            org_name=payload.get("org_name"),
            cluster_name=cluster_name,
        )
        if "user_info" in payload:
            user_info = self._parse_user_info_payload(payload["user_info"])
            cluster_user = cluster_user.add_info(user_info)
        return cluster_user

    @overload
    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: Literal[True],
        org_name: str | None = None,
    ) -> list[ClusterUserWithInfo]:
        ...

    @overload
    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: Literal[False] = ...,
        org_name: str | None = None,
    ) -> list[ClusterUser]:
        ...

    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> list[ClusterUser] | list[ClusterUserWithInfo]:
        if org_name:
            url = f"clusters/{cluster_name}/orgs/{org_name}/users"
        else:
            url = f"clusters/{cluster_name}/users"
        async with self._request(
            "GET",
            url,
            params={"with_user_info": _to_query_bool(with_user_info)},
        ) as resp:
            resp.raise_for_status()
            clusters_raw = await resp.json()
            clusters = [
                self._parse_cluster_user(cluster_name, raw_user)
                for raw_user in clusters_raw
            ]
        return clusters

    @overload
    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: Literal[True] = ...,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: Literal[False] = ...,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        if org_name:
            url = f"clusters/{cluster_name}/orgs/{org_name}/users/{user_name}"
        else:
            url = f"clusters/{cluster_name}/users/{user_name}"
        async with self._request(
            "GET",
            url,
            params={"with_user_info": _to_query_bool(with_user_info)},
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_cluster_user(cluster_name, raw_user)

    def _quota_to_payload(self, quota: Quota) -> dict[str, Any]:
        res = {}
        if quota.total_running_jobs is not None:
            res["total_running_jobs"] = quota.total_running_jobs
        return res

    def _balance_to_payload(self, balance: Balance) -> dict[str, Any]:
        res = {}
        if balance.credits is not None:
            res["credits"] = str(balance.credits)
        if balance.spent_credits is not None:
            res["spent_credits"] = str(balance.spent_credits)
        return res

    @overload
    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        with_user_info: Literal[True],
        quota: Quota | None = None,
        balance: Balance | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        with_user_info: Literal[False] = ...,
        quota: Quota | None = None,
        balance: Balance | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        quota: Quota | None = None,
        balance: Balance | None = None,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        payload: dict[str, Any] = {"user_name": user_name, "role": role.value}
        if org_name:
            payload["org_name"] = org_name
        if quota:
            payload["quota"] = self._quota_to_payload(quota)
        if balance:
            payload["balance"] = self._balance_to_payload(balance)

        async with self._request(
            "POST",
            f"clusters/{cluster_name}/users",
            json=payload,
            params={"with_user_info": _to_query_bool(with_user_info)},
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_cluster_user(cluster_name, raw_user)

    @overload
    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: Literal[True]
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: Literal[False] = ...
    ) -> ClusterUser:
        ...

    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: bool = False
    ) -> ClusterUser | ClusterUserWithInfo:
        payload: dict[str, Any] = {
            "user_name": cluster_user.user_name,
            "role": cluster_user.role.value,
            "quota": {},
            "balance": {},
        }
        if cluster_user.org_name:
            payload["org_name"] = cluster_user.org_name
        if cluster_user.quota.total_running_jobs is not None:
            payload["quota"][
                "total_running_jobs"
            ] = cluster_user.quota.total_running_jobs
        if cluster_user.balance.credits is not None:
            payload["balance"]["credits"] = str(cluster_user.balance.credits)
        if cluster_user.balance.spent_credits is not None:
            payload["balance"]["spent_credits"] = str(
                cluster_user.balance.spent_credits
            )
        if cluster_user.org_name:
            url = (
                f"clusters/{cluster_user.cluster_name}/orgs/"
                f"{cluster_user.org_name}/users/{cluster_user.user_name}"
            )
        else:
            url = f"clusters/{cluster_user.cluster_name}/users/{cluster_user.user_name}"

        async with self._request(
            "PUT",
            url,
            json=payload,
            params={"with_user_info": _to_query_bool(with_user_info)},
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_cluster_user(cluster_user.cluster_name, raw_user)

    async def delete_cluster_user(
        self, cluster_name: str, user_name: str, org_name: str | None = None
    ) -> None:
        if org_name:
            url = f"clusters/{cluster_name}/orgs/{org_name}/users/{user_name}"
        else:
            url = f"clusters/{cluster_name}/users/{user_name}"
        async with self._request(
            "DELETE",
            url,
        ) as resp:
            resp.raise_for_status()

    @overload
    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        payload = {"quota": {"total_running_jobs": quota.total_running_jobs}}
        params = {
            "with_user_info": _to_query_bool(with_user_info),
        }
        if payload["quota"]["total_running_jobs"] is None:
            # Server do not support None in payload
            payload["quota"].pop("total_running_jobs")
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        if org_name:
            url = f"clusters/{cluster_name}/orgs/{org_name}/users/{user_name}/quota"
        else:
            url = f"clusters/{cluster_name}/users/{user_name}/quota"
        async with self._request(
            "PATCH",
            url,
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_cluster_user(cluster_name, raw_user)

    @overload
    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        payload = {"additional_quota": {"total_running_jobs": delta.total_running_jobs}}
        params = {
            "with_user_info": _to_query_bool(with_user_info),
        }
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        if org_name:
            url = f"clusters/{cluster_name}/orgs/{org_name}/users/{user_name}/quota"
        else:
            url = f"clusters/{cluster_name}/users/{user_name}/quota"
        async with self._request(
            "PATCH",
            url,
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_cluster_user(cluster_name, raw_user)

    @overload
    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        payload = {
            "credits": str(credits) if credits else None,
        }
        params = {
            "with_user_info": _to_query_bool(with_user_info),
        }
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        if org_name:
            url = f"clusters/{cluster_name}/orgs/{org_name}/users/{user_name}/balance"
        else:
            url = f"clusters/{cluster_name}/users/{user_name}/balance"
        async with self._request(
            "PATCH",
            url,
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_cluster_user(cluster_name, raw_user)

    @overload
    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        payload = {"additional_credits": str(delta)}
        params = {
            "with_user_info": _to_query_bool(with_user_info),
        }
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        if org_name:
            url = f"clusters/{cluster_name}/orgs/{org_name}/users/{user_name}/balance"
        else:
            url = f"clusters/{cluster_name}/users/{user_name}/balance"
        async with self._request(
            "PATCH",
            url,
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_cluster_user(cluster_name, raw_user)

    @overload
    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        payload = {"spending": str(amount)}
        params = {
            "with_user_info": _to_query_bool(with_user_info),
        }
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        if org_name:
            url = f"clusters/{cluster_name}/orgs/{org_name}/users/{user_name}/spending"
        else:
            url = f"clusters/{cluster_name}/users/{user_name}/spending"
        async with self._request(
            "POST",
            url,
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_cluster_user(cluster_name, raw_user)

    def _parse_org_cluster(
        self, cluster_name: str, payload: dict[str, Any]
    ) -> OrgCluster:
        return OrgCluster(
            cluster_name=cluster_name,
            org_name=payload["org_name"],
            balance=self._parse_balance(payload.get("balance")),
            quota=self._parse_quota(payload.get("quota")),
            default_credits=Decimal(payload["default_credits"])
            if payload.get("default_credits")
            else None,
            default_quota=self._parse_quota(payload.get("default_quota")),
            storage_size_mb=payload.get("storage_size_mb"),
        )

    async def create_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
        quota: Quota = Quota(),
        balance: Balance = Balance(),
        default_quota: Quota = Quota(),
        default_credits: Decimal | None = None,
        storage_size_mb: int | None = None,
    ) -> OrgCluster:
        payload: dict[str, Any] = {
            "org_name": org_name,
            "quota": {},
            "balance": {},
            "default_quota": {},
        }
        if quota.total_running_jobs is not None:
            payload["quota"]["total_running_jobs"] = quota.total_running_jobs
        if balance.credits is not None:
            payload["balance"]["credits"] = str(balance.credits)
        if balance.spent_credits is not None:
            payload["balance"]["spent_credits"] = str(balance.spent_credits)
        if default_credits:
            payload["default_credits"] = str(default_credits)
        if default_quota.total_running_jobs is not None:
            payload["default_quota"][
                "total_running_jobs"
            ] = default_quota.total_running_jobs
        if storage_size_mb is not None:
            payload["storage_size_mb"] = storage_size_mb
        async with self._request(
            "POST",
            f"clusters/{cluster_name}/orgs",
            json=payload,
        ) as resp:
            resp.raise_for_status()
            payload = await resp.json()
            return self._parse_org_cluster(cluster_name, payload)

    async def list_org_clusters(self, cluster_name: str) -> list[OrgCluster]:
        async with self._request(
            "GET",
            f"clusters/{cluster_name}/orgs",
        ) as resp:
            resp.raise_for_status()
            raw_list = await resp.json()
            clusters = [
                self._parse_org_cluster(cluster_name, entry) for entry in raw_list
            ]
        return clusters

    async def get_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
    ) -> OrgCluster:
        async with self._request(
            "GET",
            f"clusters/{cluster_name}/orgs/{org_name}",
        ) as resp:
            resp.raise_for_status()
            raw_data = await resp.json()
            return self._parse_org_cluster(cluster_name, raw_data)

    async def update_org_cluster(self, org_cluster: OrgCluster) -> None:
        payload: dict[str, Any] = {
            "org_name": org_cluster.org_name,
            "quota": {},
            "balance": {},
            "default_quota": {},
        }
        if org_cluster.quota.total_running_jobs is not None:
            payload["quota"][
                "total_running_jobs"
            ] = org_cluster.quota.total_running_jobs
        if org_cluster.balance.credits is not None:
            payload["balance"]["credits"] = str(org_cluster.balance.credits)
        if org_cluster.balance.spent_credits is not None:
            payload["balance"]["spent_credits"] = str(org_cluster.balance.spent_credits)
        if org_cluster.default_credits:
            payload["default_credits"] = str(org_cluster.default_credits)
        if org_cluster.default_quota.total_running_jobs is not None:
            payload["default_quota"][
                "total_running_jobs"
            ] = org_cluster.default_quota.total_running_jobs
        async with self._request(
            "PUT",
            f"clusters/{org_cluster.cluster_name}/orgs/{org_cluster.org_name}",
            json=payload,
        ) as resp:
            resp.raise_for_status()

    async def delete_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
    ) -> None:
        async with self._request(
            "DELETE",
            f"clusters/{cluster_name}/orgs/{org_name}",
        ) as resp:
            resp.raise_for_status()

    async def update_org_cluster_quota(
        self,
        cluster_name: str,
        org_name: str,
        quota: Quota,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        payload = {"quota": {"total_running_jobs": quota.total_running_jobs}}
        params = {}
        if payload["quota"]["total_running_jobs"] is None:
            # Server do not support None in payload
            payload["quota"].pop("total_running_jobs")
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        async with self._request(
            "PATCH",
            f"clusters/{cluster_name}/orgs/{org_name}/quota",
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_org_cluster = await resp.json()
            return self._parse_org_cluster(cluster_name, raw_org_cluster)

    async def update_org_cluster_quota_by_delta(
        self,
        cluster_name: str,
        org_name: str,
        delta: Quota,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        payload = {"additional_quota": {"total_running_jobs": delta.total_running_jobs}}
        params = {}
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        async with self._request(
            "PATCH",
            f"clusters/{cluster_name}/orgs/{org_name}/quota",
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_org_cluster = await resp.json()
            return self._parse_org_cluster(cluster_name, raw_org_cluster)

    async def update_org_cluster_balance(
        self,
        cluster_name: str,
        org_name: str,
        credits: Decimal | None,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        payload = {
            "credits": str(credits) if credits else None,
        }
        params = {}
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        async with self._request(
            "PATCH",
            f"clusters/{cluster_name}/orgs/{org_name}/balance",
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_org_cluster = await resp.json()
            return self._parse_org_cluster(cluster_name, raw_org_cluster)

    async def update_org_cluster_balance_by_delta(
        self,
        cluster_name: str,
        org_name: str,
        delta: Decimal,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        payload = {"additional_credits": str(delta)}
        params = {}
        if idempotency_key:
            params["idempotency_key"] = idempotency_key
        async with self._request(
            "PATCH",
            f"clusters/{cluster_name}/orgs/{org_name}/balance",
            json=payload,
            params=params,
        ) as resp:
            resp.raise_for_status()
            raw_org_cluster = await resp.json()
            return self._parse_org_cluster(cluster_name, raw_org_cluster)

    def _parse_org_payload(self, payload: dict[str, Any]) -> Org:
        return Org(
            name=payload["name"],
        )

    async def list_orgs(self) -> list[Org]:
        async with self._request("GET", "orgs") as resp:
            resp.raise_for_status()
            orgs_raw = await resp.json()
            orgs = [self._parse_org_payload(raw_user) for raw_user in orgs_raw]
        return orgs

    async def get_org(self, name: str) -> Org:
        async with self._request("GET", f"orgs/{name}") as resp:
            resp.raise_for_status()
            raw_org = await resp.json()
            return self._parse_org_payload(raw_org)

    async def create_org(
        self,
        name: str,
    ) -> Org:
        payload = {
            "name": name,
        }
        async with self._request("POST", "orgs", json=payload) as resp:
            resp.raise_for_status()
            raw_org = await resp.json()
            return self._parse_org_payload(raw_org)

    async def delete_org(self, name: str) -> Org:
        async with self._request("DELETE", f"orgs/{name}") as resp:
            resp.raise_for_status()
            raw_org = await resp.json()
            return self._parse_org_payload(raw_org)

    #  org user

    def _parse_org_user(
        self, org_name: str, payload: dict[str, Any]
    ) -> OrgUser | OrgUserWithInfo:
        org_user = OrgUser(
            user_name=payload["user_name"],
            role=OrgUserRoleType(payload["role"]),
            org_name=org_name,
        )
        if "user_info" in payload:
            user_info = self._parse_user_info_payload(payload["user_info"])
            org_user = org_user.add_info(user_info)
        return org_user

    @overload
    async def list_org_users(
        self, org_name: str, with_user_info: Literal[True]
    ) -> list[OrgUserWithInfo]:
        ...

    @overload
    async def list_org_users(
        self, org_name: str, with_user_info: Literal[False] = ...
    ) -> list[OrgUser]:
        ...

    async def list_org_users(
        self, org_name: str, with_user_info: bool = False
    ) -> list[OrgUser] | list[OrgUserWithInfo]:
        async with self._request(
            "GET",
            f"orgs/{org_name}/users",
            params={"with_user_info": _to_query_bool(with_user_info)},
        ) as resp:
            resp.raise_for_status()
            orgs_raw = await resp.json()
            orgs = [self._parse_org_user(org_name, raw_user) for raw_user in orgs_raw]
        return orgs

    @overload
    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: Literal[True]
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: Literal[False] = ...
    ) -> OrgUser:
        ...

    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: bool = False
    ) -> OrgUser | OrgUserWithInfo:
        async with self._request(
            "GET",
            f"orgs/{org_name}/users/{user_name}",
            params={"with_user_info": _to_query_bool(with_user_info)},
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_org_user(org_name, raw_user)

    @overload
    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: Literal[True],
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: Literal[False] = ...,
    ) -> OrgUser:
        ...

    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: bool = False,
    ) -> OrgUser | OrgUserWithInfo:
        payload = {
            "user_name": user_name,
            "role": role.value,
        }

        async with self._request(
            "POST",
            f"orgs/{org_name}/users",
            json=payload,
            params={"with_user_info": _to_query_bool(with_user_info)},
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_org_user(org_name, raw_user)

    @overload
    async def update_org_user(
        self, org_user: OrgUser, with_user_info: Literal[True]
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def update_org_user(
        self, org_user: OrgUser, with_user_info: Literal[False] = ...
    ) -> OrgUser:
        ...

    async def update_org_user(
        self, org_user: OrgUser, with_user_info: bool = False
    ) -> OrgUser | OrgUserWithInfo:
        payload = {
            "user_name": org_user.user_name,
            "role": org_user.role.value,
        }

        async with self._request(
            "PUT",
            f"orgs/{org_user.org_name}/users/{org_user.user_name}",
            json=payload,
            params={"with_user_info": _to_query_bool(with_user_info)},
        ) as resp:
            resp.raise_for_status()
            raw_user = await resp.json()
            return self._parse_org_user(org_user.org_name, raw_user)

    async def delete_org_user(self, org_name: str, user_name: str) -> None:
        async with self._request(
            "DELETE",
            f"orgs/{org_name}/users/{user_name}",
        ) as resp:
            resp.raise_for_status()

    # OLD API:

    async def add_debt(
        self,
        cluster_name: str,
        username: str,
        credits: Decimal,
        idempotency_key: str,
    ) -> None:
        payload = {"user_name": username, "credits": str(credits)}
        async with self._request(
            "POST",
            f"clusters/{cluster_name}/debts",
            json=payload,
            params={"idempotency_key": idempotency_key},
        ) as response:
            response.raise_for_status()


class AdminClient(AdminClientBase, AdminClientABC):
    def __new__(
        cls,
        *,
        base_url: URL | None,
        service_token: str | None = None,
        conn_timeout_s: int = 300,
        read_timeout_s: int = 100,
        conn_pool_size: int = 100,
        trace_configs: Sequence[aiohttp.TraceConfig] = (),
    ) -> Any:
        if base_url is None:
            return AdminClientDummy()
        return super().__new__(cls)

    def __init__(
        self,
        *,
        base_url: URL | None,
        service_token: str | None = None,
        conn_timeout_s: int = 300,
        read_timeout_s: int = 100,
        conn_pool_size: int = 100,
        trace_configs: Sequence[aiohttp.TraceConfig] = (),
    ):
        if base_url is not None and not base_url:
            raise ValueError(
                "url argument should be http URL or None for secure-less configurations"
            )
        self._base_url = base_url
        self._service_token = service_token
        self._conn_timeout_s = conn_timeout_s
        self._read_timeout_s = read_timeout_s
        self._conn_pool_size = conn_pool_size
        self._trace_configs = trace_configs
        self._client: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "AdminClient":
        self._init()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if not self._client:
            return
        await self._client.close()
        del self._client

    def _init(self) -> None:
        if self._client:
            return
        if not self._base_url:
            return
        connector = aiohttp.TCPConnector(limit=self._conn_pool_size)
        timeout = aiohttp.ClientTimeout(
            connect=self._conn_timeout_s, total=self._read_timeout_s
        )
        self._client = aiohttp.ClientSession(
            headers=self._generate_headers(self._service_token),
            connector=connector,
            timeout=timeout,
            trace_configs=list(self._trace_configs),
        )

    def _generate_headers(self, token: str | None = None) -> CIMultiDict[str]:
        headers: CIMultiDict[str] = CIMultiDict()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @asynccontextmanager
    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> AsyncIterator[aiohttp.ClientResponse]:
        assert self._client
        assert self._base_url
        url = self._base_url / path
        async with self._client.request(method, url, **kwargs) as response:
            response.raise_for_status()
            yield response


class AdminClientDummy(AdminClientABC):
    DUMMY_USER = User(
        name="user",
        email="email@example.com",
    )
    DUMMY_CLUSTER = Cluster(name="default", default_credits=None, default_quota=Quota())
    DUMMY_CLUSTER_USER = ClusterUserWithInfo(
        cluster_name="default",
        user_name="user",
        role=ClusterUserRoleType.ADMIN,
        quota=Quota(),
        balance=Balance(),
        org_name=None,
        user_info=UserInfo(email="email@examle.com"),
    )
    DUMMY_ORG = Org(
        name="org",
    )
    DUMMY_ORG_CLUSTER = OrgCluster(
        org_name="org",
        cluster_name="default",
        balance=Balance(),
        quota=Quota(),
        storage_size_mb=1024,
    )
    DUMMY_ORG_USER = OrgUserWithInfo(
        org_name="org",
        user_name="user",
        role=OrgUserRoleType.ADMIN,
        user_info=UserInfo(email="email@examle.com"),
    )

    async def __aenter__(self) -> "AdminClientDummy":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass

    async def aclose(self) -> None:
        pass

    async def list_users(self) -> list[User]:
        return [self.DUMMY_USER]

    async def get_user(self, name: str) -> User:
        return self.DUMMY_USER

    async def get_user_with_clusters(self, name: str) -> tuple[User, list[ClusterUser]]:
        return self.DUMMY_USER, [self.DUMMY_CLUSTER_USER]

    async def create_user(
        self,
        name: str,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        return self.DUMMY_USER

    async def update_user(
        self,
        user: User,
    ) -> None:
        pass

    async def list_clusters(self) -> list[Cluster]:
        return [self.DUMMY_CLUSTER]

    async def get_cluster(self, name: str) -> Cluster:
        return self.DUMMY_CLUSTER

    async def create_cluster(
        self,
        name: str,
        default_credits: Decimal | None = None,
        default_quota: Quota = Quota(),
    ) -> Cluster:
        return self.DUMMY_CLUSTER

    async def update_cluster(
        self,
        cluster: Cluster,
    ) -> None:
        pass

    async def delete_cluster(self, name: str) -> Cluster:
        pass

    @overload
    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: Literal[True],
        org_name: str | None = None,
    ) -> list[ClusterUserWithInfo]:
        ...

    @overload
    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: Literal[False] = ...,
        org_name: str | None = None,
    ) -> list[ClusterUser]:
        ...

    async def list_cluster_users(
        self,
        cluster_name: str,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> list[ClusterUser] | list[ClusterUserWithInfo]:
        return [self.DUMMY_CLUSTER_USER]

    @overload
    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: Literal[True] = ...,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: Literal[False] = ...,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def get_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        return self.DUMMY_CLUSTER_USER

    @overload
    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        with_user_info: Literal[True],
        quota: Quota | None = None,
        balance: Balance | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        with_user_info: Literal[False] = ...,
        quota: Quota | None = None,
        balance: Balance | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def create_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        role: ClusterUserRoleType,
        *,
        quota: Quota | None = None,
        balance: Balance | None = None,
        with_user_info: bool = False,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        return self.DUMMY_CLUSTER_USER

    @overload
    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: Literal[True]
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: Literal[False] = ...
    ) -> ClusterUser:
        ...

    async def update_cluster_user(
        self, cluster_user: ClusterUser, with_user_info: bool = False
    ) -> ClusterUser | ClusterUserWithInfo:
        return self.DUMMY_CLUSTER_USER

    async def delete_cluster_user(
        self, cluster_name: str, user_name: str, org_name: str | None = None
    ) -> None:
        pass

    @overload
    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def update_cluster_user_quota(
        self,
        cluster_name: str,
        user_name: str,
        quota: Quota,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        return self.DUMMY_CLUSTER_USER

    @overload
    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def update_cluster_user_quota_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Quota,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        return self.DUMMY_CLUSTER_USER

    @overload
    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def update_cluster_user_balance(
        self,
        cluster_name: str,
        user_name: str,
        credits: Decimal | None,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        return self.DUMMY_CLUSTER_USER

    @overload
    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def update_cluster_user_balance_by_delta(
        self,
        cluster_name: str,
        user_name: str,
        delta: Decimal,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        return self.DUMMY_CLUSTER_USER

    @overload
    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: Literal[True],
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUserWithInfo:
        ...

    @overload
    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: Literal[False] = ...,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser:
        ...

    async def charge_cluster_user(
        self,
        cluster_name: str,
        user_name: str,
        amount: Decimal,
        *,
        with_user_info: bool = False,
        idempotency_key: str | None = None,
        org_name: str | None = None,
    ) -> ClusterUser | ClusterUserWithInfo:
        return self.DUMMY_CLUSTER_USER

    async def create_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
        quota: Quota = Quota(),
        balance: Balance = Balance(),
        default_quota: Quota = Quota(),
        default_credits: Decimal | None = None,
        storage_size_mb: int | None = None,
    ) -> OrgCluster:
        return self.DUMMY_ORG_CLUSTER

    async def list_org_clusters(self, cluster_name: str) -> list[OrgCluster]:
        return [self.DUMMY_ORG_CLUSTER]

    async def get_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
    ) -> OrgCluster:
        return self.DUMMY_ORG_CLUSTER

    async def update_org_cluster(self, org_cluster: OrgCluster) -> None:
        pass

    async def delete_org_cluster(
        self,
        cluster_name: str,
        org_name: str,
    ) -> None:
        pass

    async def update_org_cluster_quota(
        self,
        cluster_name: str,
        org_name: str,
        quota: Quota,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        return self.DUMMY_ORG_CLUSTER

    async def update_org_cluster_quota_by_delta(
        self,
        cluster_name: str,
        org_name: str,
        delta: Quota,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        return self.DUMMY_ORG_CLUSTER

    async def update_org_cluster_balance(
        self,
        cluster_name: str,
        org_name: str,
        credits: Decimal | None,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        return self.DUMMY_ORG_CLUSTER

    async def update_org_cluster_balance_by_delta(
        self,
        cluster_name: str,
        org_name: str,
        delta: Decimal,
        *,
        idempotency_key: str | None = None,
    ) -> OrgCluster:
        return self.DUMMY_ORG_CLUSTER

    async def list_orgs(self) -> list[Org]:
        return [self.DUMMY_ORG]

    async def get_org(self, name: str) -> Org:
        return self.DUMMY_ORG

    async def create_org(
        self,
        name: str,
    ) -> Org:
        return self.DUMMY_ORG

    async def delete_org(self, name: str) -> Org:
        pass

    #  org user

    @overload
    async def list_org_users(
        self, org_name: str, with_user_info: Literal[True]
    ) -> list[OrgUserWithInfo]:
        ...

    @overload
    async def list_org_users(
        self, org_name: str, with_user_info: Literal[False] = ...
    ) -> list[OrgUser]:
        ...

    async def list_org_users(
        self, org_name: str, with_user_info: bool = False
    ) -> list[OrgUser] | list[OrgUserWithInfo]:
        return [self.DUMMY_ORG_USER]

    @overload
    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: Literal[True]
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: Literal[False] = ...
    ) -> OrgUser:
        ...

    async def get_org_user(
        self, org_name: str, user_name: str, with_user_info: bool = False
    ) -> OrgUser | OrgUserWithInfo:
        return self.DUMMY_ORG_USER

    @overload
    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: Literal[True],
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: Literal[False] = ...,
    ) -> OrgUser:
        ...

    async def create_org_user(
        self,
        org_name: str,
        user_name: str,
        role: OrgUserRoleType,
        with_user_info: bool = False,
    ) -> OrgUser | OrgUserWithInfo:
        return self.DUMMY_ORG_USER

    @overload
    async def update_org_user(
        self, org_user: OrgUser, with_user_info: Literal[True]
    ) -> OrgUserWithInfo:
        ...

    @overload
    async def update_org_user(
        self, org_user: OrgUser, with_user_info: Literal[False] = ...
    ) -> OrgUser:
        ...

    async def update_org_user(
        self, org_user: OrgUser, with_user_info: bool = False
    ) -> OrgUser | OrgUserWithInfo:
        return self.DUMMY_ORG_USER

    async def delete_org_user(self, org_name: str, user_name: str) -> None:
        pass

    async def add_debt(
        self,
        cluster_name: str,
        username: str,
        credits: Decimal,
        idempotency_key: str,
    ) -> None:
        pass
