"""
Main interface for amplify service.

Usage::

    ```python
    import boto3
    from mypy_boto3_amplify import (
        AmplifyClient,
        Client,
        ListAppsPaginator,
        ListBranchesPaginator,
        ListDomainAssociationsPaginator,
        ListJobsPaginator,
    )

    session = boto3.Session()

    client: AmplifyClient = boto3.client("amplify")
    session_client: AmplifyClient = session.client("amplify")

    list_apps_paginator: ListAppsPaginator = client.get_paginator("list_apps")
    list_branches_paginator: ListBranchesPaginator = client.get_paginator("list_branches")
    list_domain_associations_paginator: ListDomainAssociationsPaginator = client.get_paginator("list_domain_associations")
    list_jobs_paginator: ListJobsPaginator = client.get_paginator("list_jobs")
    ```
"""
from .client import AmplifyClient
from .paginator import (
    ListAppsPaginator,
    ListBranchesPaginator,
    ListDomainAssociationsPaginator,
    ListJobsPaginator,
)

Client = AmplifyClient


__all__ = (
    "AmplifyClient",
    "Client",
    "ListAppsPaginator",
    "ListBranchesPaginator",
    "ListDomainAssociationsPaginator",
    "ListJobsPaginator",
)
