import typing as T

from dbt.contracts.results import NodeResult
from dbt.contracts.graph.parsed import (
    ParsedNode,
    ParsedSourceDefinition,
    SeedConfig,
    TestConfig,
    NodeConfig,
    SnapshotConfig,
)
from dbt.contracts.graph.compiled import (
    CompiledGenericTestNode,
    CompiledSeedNode,
    CompiledSnapshotNode,
)

from ..logger import GLOBAL_LOGGER as log


def _parse_node(node: ParsedNode) -> T.Dict:
    parsed = dict(
        database=node.database.lower(),
        schema=node.schema.lower(),
        path=node.path.lower(),
        name=node.name.lower(),
        resource_type=node.resource_type.lower(),
        package_name=node.package_name.lower(),
    )

    # only add tags when they exist
    if node.tags:
        parsed["tags"] = ", ".join(node.tags).lower()

    return parsed


def _parse_parsed_node(node: ParsedNode) -> T.Dict:
    parsed = _parse_node(node)
    parsed["filename"] = node.root_path
    parsed["abs_path"] = f"{node.root_path}/{node.build_path}"
    return parsed


def _parse_parsed_source_node(node: ParsedSourceDefinition) -> T.Dict:
    parsed = _parse_node(node)
    parsed["filename"] = node.original_file_path
    parsed["abs_path"] = f"{node.root_path}/{node.original_file_path}"
    return parsed


# TO DO, not important
def _parse_seed_node_config(config: SeedConfig) -> T.Dict:
    return {}


def _parse_test_node_config(config: TestConfig) -> T.Dict:
    return dict(
        materialized=config.materialized.lower(),
    )


def _parse_snapshot_node_config(
    config: SnapshotConfig,
) -> T.Dict:
    node_config = _parse_node_config(config)
    snapshot_config = dict(
        strategy=config.get("stategy", "").lower(),
        unique_key=config.get("unique_key", "").lower(),
        updated_at=config.get('updated_at'),
    )

    return {**node_config, **snapshot_config}


def _parse_node_config(config: NodeConfig) -> T.Dict:
    return dict(
        materialized=config.materialized.lower(),
    )


def parse_node(result: NodeResult) -> T.Dict:
    node = result.node
    config = {}

    log.info(type(node))
    # currently each config function returns the entire config
    # as dict, they are seperated out so we can omit unnecessary
    # values in the future
    if isinstance(node, ParsedSourceDefinition):
        log.info("parsing source definition node")
        parsed_node = _parse_parsed_source_node(node)
        return parsed_node

    parsed_node = _parse_parsed_node(node)
    if isinstance(node, CompiledSeedNode):
        log.debug("parsing seed node config")
        config = _parse_seed_node_config(node.config)
    elif isinstance(node, CompiledGenericTestNode):
        log.debug("parsing test node config")
        config = _parse_test_node_config(node.config)
    elif isinstance(node, CompiledSnapshotNode):
        log.debug("parsing snapshot node config")
        config = _parse_snapshot_node_config(node.config)
    else:
        log.debug("parsing default node config")
        config = _parse_node_config(node.config)

    return {**parsed_node, **config}
