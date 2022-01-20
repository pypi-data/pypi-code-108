from typing import Any
from typing import List
from typing import Optional

from pydantic import BaseModel


class Plot2D(BaseModel):
    data: List[List[Any]]
    xlabel: str
    ylabel: str


class SimpleTable(BaseModel):
    rows: List[List[Any]]
    header_row: Optional[bool] = True
    header_column: Optional[bool] = False


class ReportMetric(BaseModel):
    """
    A Quality Report is made up of a list of metrics with the schema defined by this class.
      Additionally this class can produce a Flowable or List of Flowables to be render the metric
      in the PDF Report
    """

    name: str
    description: str
    statement: Optional[str] = None
    plot_data: Optional[Plot2D] = None
    table_data: Optional[SimpleTable] = None
    warnings: Optional[List[str]] = None
