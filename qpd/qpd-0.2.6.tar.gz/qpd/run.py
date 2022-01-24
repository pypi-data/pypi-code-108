from typing import Any, Dict

from qpd._parser.sql import QPDSql
from qpd._parser.utils import VisitorContext
from qpd._parser.visitors import StatementVisitor
from qpd.qpd_engine import QPDEngine
from qpd.workflow import QPDWorkflow, QPDWorkflowContext


def run_sql(
    engine: QPDEngine, sql: str, dfs: Dict[str, Any], ignore_case: bool = False
) -> Any:
    qsql = QPDSql(sql, "singleStatement", ignore_case=ignore_case)
    ctx = QPDWorkflowContext(engine, dfs)
    wf = QPDWorkflow(ctx)
    v = StatementVisitor(
        VisitorContext(
            sql=qsql,
            workflow=wf,
            dfs=wf.dfs,
        )
    )
    wf.assemble_output(v.visit(qsql.tree))
    wf.run()
    return ctx.result
