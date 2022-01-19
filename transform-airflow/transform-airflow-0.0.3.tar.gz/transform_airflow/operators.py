import logging

from typing import Optional, Any
from airflow.exceptions import AirflowException  # type: ignore
from airflow.models.baseoperator import BaseOperator  # type: ignore

from .utils import initialize_mql_client

logger = logging.getLogger()


class MaterializeOperator(BaseOperator):
    """Airflow operator for materializing with MQL."""

    def __init__(  # type: ignore[misc] # noqa: D
        self,
        materialization_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        model_key_id: Optional[int] = None,
        output_table: Optional[str] = None,
        force: bool = False,
        **kwargs: Any,
    ) -> None:
        self.materialization_name = materialization_name
        self.start_time = start_time
        self.end_time = end_time
        self.model_key_id = model_key_id
        self.output_table = output_table
        self.force = force
        self.mql = initialize_mql_client()
        super().__init__(**kwargs)

    def execute(self, context: Any) -> None:  # type: ignore[misc] # noqa: D
        logger.info("starting materialization")
        try:
            resp = self.mql.materialize(
                self.materialization_name,
                self.start_time,
                self.end_time,
                model_key_id=self.model_key_id,
                output_table=self.output_table,
                force=self.force,
                timeout=0,
            )
            logger.info(f"got table-{resp.table}, schema-{resp.schema}")
        except Exception as e:
            raise AirflowException(str(e))
