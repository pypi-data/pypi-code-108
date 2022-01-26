import datetime
from dataclasses import replace
from decimal import Decimal

import pytest
from aiohttp import ClientResponseError

from neuro_admin_client import (
    AdminClient,
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

from .conftest import AdminServer


class TestAdminClient:
    async def test_client_no_url_no_errors(self) -> None:
        async with AdminClient(base_url=None) as client:
            await client.get_user("name")
            await client.get_org("org")
            await client.get_cluster("cluster")
            await client.get_cluster_user("cluster", "name")

    async def test_create_user(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_user(name="name", email="email")

        assert len(mock_admin_server.users) == 1
        created_user = mock_admin_server.users[0]
        assert created_user.name == "name"
        assert created_user.email == "email"

    async def test_create_user_first_name_last_name(
        self, mock_admin_server: AdminServer
    ) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_user(
                name="name",
                email="email",
                first_name="first_name",
                last_name="last_name",
            )

        assert len(mock_admin_server.users) == 1
        created_user = mock_admin_server.users[0]
        assert created_user.name == "name"
        assert created_user.email == "email"

        assert created_user.first_name == "first_name"
        assert created_user.last_name == "last_name"

    async def test_list_users(self, mock_admin_server: AdminServer) -> None:
        date = datetime.datetime.now(datetime.timezone.utc)

        mock_admin_server.users = [
            User(
                name="name",
                email="email",
            ),
            User(
                name="name2",
                email="email2",
                first_name="first_name",
                last_name="last_name",
                created_at=date,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            users = await client.list_users()

        assert len(users) == 2
        assert set(users) == set(mock_admin_server.users)

    async def test_get_user(self, mock_admin_server: AdminServer) -> None:
        date = datetime.datetime.now(datetime.timezone.utc)

        mock_admin_server.users = [
            User(
                name="name",
                email="email",
            ),
            User(
                name="name2",
                email="email2",
                first_name="first_name",
                last_name="last_name",
                created_at=date,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            user = await client.get_user(name="name")
            assert user == mock_admin_server.users[0]

            user = await client.get_user(name="name2")
            assert user == mock_admin_server.users[1]

    async def test_get_user_with_clusters(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster1",
                default_credits=None,
                default_quota=Quota(),
            ),
            Cluster(
                name="cluster2",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster1",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
            ClusterUser(
                user_name="test1",
                cluster_name="cluster2",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            user, cluster_users = await client.get_user_with_clusters(name="test1")
            assert user == mock_admin_server.users[0]
            assert set(cluster_users) == set(mock_admin_server.cluster_users)

    async def test_create_org(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_org(name="name")

        assert len(mock_admin_server.orgs) == 1
        created_org = mock_admin_server.orgs[0]
        assert created_org.name == "name"

    async def test_list_orgs(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.orgs = [
            Org(
                name="name",
            ),
            Org(
                name="name2",
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            orgs = await client.list_orgs()

        assert len(orgs) == 2
        assert set(orgs) == set(mock_admin_server.orgs)

    async def test_get_org(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.orgs = [
            Org(
                name="name",
            ),
            Org(
                name="name2",
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            org = await client.get_org(name="name")
            assert org == mock_admin_server.orgs[0]

            org = await client.get_org(name="name2")
            assert org == mock_admin_server.orgs[1]

    async def test_delete_org(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.orgs = [
            Org(
                name="name",
            ),
            Org(
                name="name2",
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            org = await client.delete_org(name="name")
            assert org.name == "name"

            with pytest.raises(ClientResponseError):
                org = await client.get_org(name="name")

            assert len(mock_admin_server.orgs) == 1

            org = await client.get_org(name="name2")
            assert org == mock_admin_server.orgs[0]

    async def test_create_cluster(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name="name")

        assert len(mock_admin_server.clusters) == 1
        created_cluster = mock_admin_server.clusters[0]
        assert created_cluster.name == "name"

    async def test_create_cluster_with_defaults(
        self, mock_admin_server: AdminServer
    ) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(
                name="name",
                default_credits=Decimal(20),
                default_quota=Quota(total_running_jobs=42),
            )

        assert len(mock_admin_server.clusters) == 1
        created_cluster = mock_admin_server.clusters[0]
        assert created_cluster.name == "name"
        assert created_cluster.default_credits == Decimal(20)
        assert created_cluster.default_quota == Quota(total_running_jobs=42)

    async def test_update_cluster(self, mock_admin_server: AdminServer) -> None:
        cluster = Cluster(
            name="name",
            default_credits=Decimal(20),
            default_quota=Quota(total_running_jobs=42),
        )

        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name=cluster.name)
            await client.update_cluster(cluster)

        assert len(mock_admin_server.clusters) == 1
        created_cluster = mock_admin_server.clusters[0]
        assert created_cluster == cluster

    async def test_list_clusters(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.clusters = [
            Cluster(
                name="name",
                default_credits=None,
                default_quota=Quota(),
            ),
            Cluster(
                name="name2",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            clusters = await client.list_clusters()

        assert len(clusters) == 2
        assert set(clusters) == set(mock_admin_server.clusters)

    async def test_get_cluster(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.clusters = [
            Cluster(
                name="name",
                default_credits=None,
                default_quota=Quota(),
            ),
            Cluster(
                name="name2",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster = await client.get_cluster(name="name")
            assert cluster == mock_admin_server.clusters[0]

            cluster = await client.get_cluster(name="name2")
            assert cluster == mock_admin_server.clusters[1]

    async def test_delete_cluster(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.clusters = [
            Cluster(
                name="name",
                default_credits=None,
                default_quota=Quota(),
            ),
            Cluster(
                name="name2",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:

            cluster = await client.delete_cluster(name="name")
            assert cluster.name == "name"

            with pytest.raises(ClientResponseError):
                cluster = await client.get_cluster(name="name")

            assert len(mock_admin_server.clusters) == 1

            cluster = await client.get_cluster(name="name2")
            assert cluster == mock_admin_server.clusters[0]

    async def test_create_cluster_user(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name="test")
            await client.create_user(name="test_user", email="email")
            res_user_with_info = await client.create_cluster_user(
                cluster_name="test",
                user_name="test_user",
                role=ClusterUserRoleType.USER,
                balance=Balance(credits=Decimal(20)),
                quota=Quota(total_running_jobs=12),
                with_user_info=True,
            )
            res_user = await client.get_cluster_user(
                cluster_name="test", user_name="test_user"
            )

        assert res_user.cluster_name == "test"
        assert res_user.user_name == "test_user"
        assert res_user.role == ClusterUserRoleType.USER
        assert res_user.quota.total_running_jobs == 12
        assert res_user.balance.credits == Decimal(20)
        assert res_user_with_info.user_info.email == "email"

        assert mock_admin_server.cluster_users == [res_user]

    async def test_update_cluster_user(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name="test")
            await client.create_user(name="test_user", email="email")
            res_user = await client.create_cluster_user(
                cluster_name="test",
                user_name="test_user",
                role=ClusterUserRoleType.USER,
                balance=Balance(credits=Decimal(20)),
                quota=Quota(total_running_jobs=12),
            )
            res_user = replace(res_user, role=ClusterUserRoleType.ADMIN)
            res_user = await client.update_cluster_user(res_user)

        assert res_user.role == ClusterUserRoleType.ADMIN
        assert mock_admin_server.cluster_users == [res_user]

    async def test_create_cluster_user_with_org(
        self, mock_admin_server: AdminServer
    ) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name="test")
            await client.create_user(name="test_user", email="email")
            res_user_with_info = await client.create_cluster_user(
                cluster_name="test",
                user_name="test_user",
                role=ClusterUserRoleType.USER,
                balance=Balance(credits=Decimal(20)),
                quota=Quota(total_running_jobs=12),
                with_user_info=True,
                org_name="some_org",
            )
            res_user = await client.get_cluster_user(
                cluster_name="test",
                user_name="test_user",
                org_name="some_org",
            )

        assert res_user.cluster_name == "test"
        assert res_user.user_name == "test_user"
        assert res_user.org_name == "some_org"
        assert res_user.role == ClusterUserRoleType.USER
        assert res_user.quota.total_running_jobs == 12
        assert res_user.balance.credits == Decimal(20)
        assert res_user_with_info.user_info.email == "email"

        assert mock_admin_server.cluster_users == [res_user]

    async def test_update_cluster_user_with_org(
        self, mock_admin_server: AdminServer
    ) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name="test")
            await client.create_user(name="test_user", email="email")
            res_user = await client.create_cluster_user(
                cluster_name="test",
                user_name="test_user",
                role=ClusterUserRoleType.USER,
                balance=Balance(credits=Decimal(20)),
                quota=Quota(total_running_jobs=12),
                org_name="some_org",
            )
            res_user = replace(res_user, role=ClusterUserRoleType.ADMIN)
            res_user = await client.update_cluster_user(res_user)

        assert res_user.role == ClusterUserRoleType.ADMIN
        assert mock_admin_server.cluster_users == [res_user]

    async def test_list_clusters_user(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
            User(
                name="test2",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
            ClusterUser(
                user_name="test2",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_users = await client.list_cluster_users("cluster")

        assert len(cluster_users) == 2
        assert set(cluster_users) == set(mock_admin_server.cluster_users)

    async def test_list_clusters_user_with_org(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
            User(
                name="test2",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
            ClusterUser(
                user_name="test2",
                cluster_name="cluster",
                org_name="org1",
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_users = await client.list_cluster_users("cluster", org_name="org1")

        assert len(cluster_users) == 1
        assert set(cluster_users) == {mock_admin_server.cluster_users[1]}

    async def test_get_cluster_user(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
            User(
                name="test2",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
            ClusterUser(
                user_name="test2",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_user = await client.get_cluster_user(
                cluster_name="cluster", user_name="test1"
            )
            assert cluster_user == mock_admin_server.cluster_users[0]

            cluster_user = await client.get_cluster_user(
                cluster_name="cluster", user_name="test2"
            )
            assert cluster_user == mock_admin_server.cluster_users[1]

    async def test_delete_cluster_user(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
            User(
                name="test2",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
            ClusterUser(
                user_name="test2",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.delete_cluster_user(cluster_name="cluster", user_name="test1")
            assert len(mock_admin_server.cluster_users) == 1
            assert mock_admin_server.cluster_users[0].user_name == "test2"

    async def test_delete_cluster_user_with_org(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name="org",
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(),
                role=ClusterUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.delete_cluster_user(
                cluster_name="cluster", user_name="test1", org_name="org"
            )
            assert len(mock_admin_server.cluster_users) == 1
            assert mock_admin_server.cluster_users[0].user_name == "test1"
            assert mock_admin_server.cluster_users[0].cluster_name == "cluster"
            assert mock_admin_server.cluster_users[0].org_name is None

    async def test_create_org_user(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_org(name="test")
            await client.create_user(name="test_user", email="email")
            res_user_with_info = await client.create_org_user(
                org_name="test",
                user_name="test_user",
                role=OrgUserRoleType.USER,
                with_user_info=True,
            )
            res_user = await client.get_org_user(org_name="test", user_name="test_user")

        assert res_user.org_name == "test"
        assert res_user.user_name == "test_user"
        assert res_user.role == OrgUserRoleType.USER
        assert res_user_with_info.user_info.email == "email"

        assert mock_admin_server.org_users == [res_user]

    async def test_update_org_user(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_org(name="test")
            await client.create_user(name="test_user", email="email")
            res_user_with_info = await client.create_org_user(
                org_name="test",
                user_name="test_user",
                role=OrgUserRoleType.USER,
                with_user_info=True,
            )
            res_user = await client.get_org_user(org_name="test", user_name="test_user")
            res_user = replace(res_user, role=OrgUserRoleType.ADMIN)
            res_user = await client.update_org_user(res_user)

        assert res_user.org_name == "test"
        assert res_user.user_name == "test_user"
        assert res_user.role == OrgUserRoleType.ADMIN
        assert res_user_with_info.user_info.email == "email"

        assert mock_admin_server.org_users == [res_user]

    async def test_list_orgs_user(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
            User(
                name="test2",
                email="email",
            ),
        ]
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.org_users = [
            OrgUser(
                user_name="test1",
                org_name="org",
                role=OrgUserRoleType.USER,
            ),
            OrgUser(
                user_name="test2",
                org_name="org",
                role=OrgUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            org_users = await client.list_org_users("org")

        assert len(org_users) == 2
        assert set(org_users) == set(mock_admin_server.org_users)

    async def test_get_org_user(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
            User(
                name="test2",
                email="email",
            ),
        ]
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.org_users = [
            OrgUser(
                user_name="test1",
                org_name="org",
                role=OrgUserRoleType.USER,
            ),
            OrgUser(
                user_name="test2",
                org_name="org",
                role=OrgUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            org_user = await client.get_org_user(org_name="org", user_name="test1")
            assert org_user == mock_admin_server.org_users[0]

            org_user = await client.get_org_user(org_name="org", user_name="test2")
            assert org_user == mock_admin_server.org_users[1]

    async def test_delete_org_user(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
            User(
                name="test2",
                email="email",
            ),
        ]
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.org_users = [
            OrgUser(
                user_name="test1",
                org_name="org",
                role=OrgUserRoleType.USER,
            ),
            OrgUser(
                user_name="test2",
                org_name="org",
                role=OrgUserRoleType.ADMIN,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.delete_org_user(org_name="org", user_name="test1")
            assert len(mock_admin_server.org_users) == 1
            assert mock_admin_server.org_users[0].user_name == "test2"

    async def test_create_org_cluster(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name="test")
            await client.create_org(
                name="test_org",
            )
            res_org = await client.create_org_cluster(
                cluster_name="test", org_name="test_org", storage_size_mb=1024
            )

        assert res_org.cluster_name == "test"
        assert res_org.org_name == "test_org"
        assert res_org.storage_size_mb == 1024

        assert mock_admin_server.org_clusters == [res_org]

    async def test_create_org_cluster_with_defaults(
        self, mock_admin_server: AdminServer
    ) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name="test")
            await client.create_org(
                name="test_org",
            )
            res_org = await client.create_org_cluster(
                cluster_name="test",
                org_name="test_org",
                default_credits=Decimal(20),
                default_quota=Quota(total_running_jobs=42),
            )

        assert res_org.cluster_name == "test"
        assert res_org.org_name == "test_org"
        assert res_org.default_credits == Decimal(20)
        assert res_org.default_quota == Quota(total_running_jobs=42)

        assert mock_admin_server.org_clusters == [res_org]

    async def test_update_org_cluster(self, mock_admin_server: AdminServer) -> None:
        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.create_cluster(name="test")
            await client.create_org(
                name="test_org",
            )
            res_org = await client.create_org_cluster(
                cluster_name="test", org_name="test_org"
            )
            new_org_cluster = replace(
                res_org,
                balance=Balance(credits=Decimal(22)),
                default_credits=Decimal(20),
                default_quota=Quota(total_running_jobs=42),
            )
            await client.update_org_cluster(new_org_cluster)

        assert mock_admin_server.org_clusters == [new_org_cluster]

    async def test_list_org_clusters(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.orgs = [
            Org(
                name="test1",
            ),
            Org(
                name="test2",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.org_clusters = [
            OrgCluster(
                cluster_name="cluster",
                org_name="test1",
                balance=Balance(),
                quota=Quota(),
            ),
            OrgCluster(
                cluster_name="cluster",
                org_name="test2",
                balance=Balance(credits=Decimal("20")),
                quota=Quota(total_running_jobs=22),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            org_clusters = await client.list_org_clusters("cluster")

        assert len(org_clusters) == 2
        assert set(org_clusters) == set(mock_admin_server.org_clusters)

    async def test_get_org_cluster(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.orgs = [
            Org(
                name="test1",
            ),
            Org(
                name="test2",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.org_clusters = [
            OrgCluster(
                cluster_name="cluster",
                org_name="test1",
                balance=Balance(),
                quota=Quota(),
            ),
            OrgCluster(
                cluster_name="cluster",
                org_name="test2",
                balance=Balance(credits=Decimal("20")),
                quota=Quota(total_running_jobs=22),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            org_cluster = await client.get_org_cluster(
                cluster_name="cluster", org_name="test1"
            )
            assert org_cluster == mock_admin_server.org_clusters[0]

            org_cluster = await client.get_org_cluster(
                cluster_name="cluster", org_name="test2"
            )
            assert org_cluster == mock_admin_server.org_clusters[1]

    async def test_delete_org_cluster(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.orgs = [
            Org(
                name="test1",
            ),
            Org(
                name="test2",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.org_clusters = [
            OrgCluster(
                cluster_name="cluster",
                org_name="test1",
                balance=Balance(),
                quota=Quota(),
            ),
            OrgCluster(
                cluster_name="cluster",
                org_name="test2",
                balance=Balance(credits=Decimal("20")),
                quota=Quota(total_running_jobs=22),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.delete_org_cluster(cluster_name="cluster", org_name="test1")
            assert len(mock_admin_server.org_clusters) == 1
            assert mock_admin_server.org_clusters[0].org_name == "test2"

    async def test_patch_cluster_user_quota(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(),
                quota=Quota(total_running_jobs=10),
                role=ClusterUserRoleType.USER,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_user = await client.update_cluster_user_quota(
                cluster_name="cluster",
                user_name="test1",
                quota=Quota(total_running_jobs=15),
            )
            assert cluster_user.quota.total_running_jobs == 15

            cluster_user = await client.update_cluster_user_quota_by_delta(
                cluster_name="cluster",
                user_name="test1",
                delta=Quota(total_running_jobs=10),
            )
            assert cluster_user.quota.total_running_jobs == 25

    async def test_patch_cluster_user_balance(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(credits=Decimal(10)),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_user = await client.update_cluster_user_balance(
                cluster_name="cluster", user_name="test1", credits=Decimal(15)
            )
            assert cluster_user.balance.credits == Decimal(15)

            cluster_user = await client.update_cluster_user_balance_by_delta(
                cluster_name="cluster", user_name="test1", delta=Decimal(10)
            )
            assert cluster_user.balance.credits == Decimal(25)

    async def test_cluster_user_add_spending(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name=None,
                balance=Balance(credits=Decimal(10)),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_user = await client.charge_cluster_user(
                cluster_name="cluster", user_name="test1", amount=Decimal(15)
            )
            assert cluster_user.balance.credits == Decimal(-5)
            assert cluster_user.balance.spent_credits == Decimal(15)

    async def test_patch_cluster_user_with_org_quota(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name="org",
                balance=Balance(),
                quota=Quota(total_running_jobs=10),
                role=ClusterUserRoleType.USER,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_user = await client.update_cluster_user_quota(
                cluster_name="cluster",
                user_name="test1",
                org_name="org",
                quota=Quota(total_running_jobs=15),
            )
            assert cluster_user.quota.total_running_jobs == 15

            cluster_user = await client.update_cluster_user_quota_by_delta(
                cluster_name="cluster",
                user_name="test1",
                org_name="org",
                delta=Quota(total_running_jobs=10),
            )
            assert cluster_user.quota.total_running_jobs == 25

    async def test_patch_cluster_user_with_org_balance(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name="org",
                balance=Balance(credits=Decimal(10)),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_user = await client.update_cluster_user_balance(
                cluster_name="cluster",
                user_name="test1",
                org_name="org",
                credits=Decimal(15),
            )
            assert cluster_user.balance.credits == Decimal(15)

            cluster_user = await client.update_cluster_user_balance_by_delta(
                cluster_name="cluster",
                user_name="test1",
                org_name="org",
                delta=Decimal(10),
            )
            assert cluster_user.balance.credits == Decimal(25)

    async def test_cluster_user_with_org_add_spending(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.users = [
            User(
                name="test1",
                email="email",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.cluster_users = [
            ClusterUser(
                user_name="test1",
                cluster_name="cluster",
                org_name="org",
                balance=Balance(credits=Decimal(10)),
                quota=Quota(),
                role=ClusterUserRoleType.USER,
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            cluster_user = await client.charge_cluster_user(
                cluster_name="cluster",
                user_name="test1",
                org_name="org",
                amount=Decimal(15),
            )
            assert cluster_user.balance.credits == Decimal(-5)
            assert cluster_user.balance.spent_credits == Decimal(15)

    async def test_cluster_user_add_debt(self, mock_admin_server: AdminServer) -> None:
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            await client.add_debt(
                cluster_name="cluster",
                username="test1",
                credits=Decimal(15),
                idempotency_key="test",
            )

            assert mock_admin_server.debts[0].cluster_name == "cluster"
            assert mock_admin_server.debts[0].user_name == "test1"
            assert mock_admin_server.debts[0].credits == Decimal(15)

    async def test_patch_org_cluster_quota(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.org_clusters = [
            OrgCluster(
                org_name="org",
                cluster_name="cluster",
                balance=Balance(),
                quota=Quota(total_running_jobs=10),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            org_cluster = await client.update_org_cluster_quota(
                cluster_name="cluster",
                org_name="org",
                quota=Quota(total_running_jobs=15),
            )
            assert org_cluster.quota.total_running_jobs == 15

            org_cluster = await client.update_org_cluster_quota_by_delta(
                cluster_name="cluster",
                org_name="org",
                delta=Quota(total_running_jobs=10),
            )
            assert org_cluster.quota.total_running_jobs == 25

    async def test_patch_org_cluster_balance(
        self, mock_admin_server: AdminServer
    ) -> None:
        mock_admin_server.orgs = [
            Org(
                name="org",
            ),
        ]
        mock_admin_server.clusters = [
            Cluster(
                name="cluster",
                default_credits=None,
                default_quota=Quota(),
            ),
        ]
        mock_admin_server.org_clusters = [
            OrgCluster(
                org_name="org",
                cluster_name="cluster",
                balance=Balance(credits=Decimal(10)),
                quota=Quota(),
            ),
        ]

        async with AdminClient(base_url=mock_admin_server.url) as client:
            org_cluster = await client.update_org_cluster_balance(
                cluster_name="cluster", org_name="org", credits=Decimal(15)
            )
            assert org_cluster.balance.credits == Decimal(15)

            org_cluster = await client.update_org_cluster_balance_by_delta(
                cluster_name="cluster", org_name="org", delta=Decimal(10)
            )
            assert org_cluster.balance.credits == Decimal(25)
