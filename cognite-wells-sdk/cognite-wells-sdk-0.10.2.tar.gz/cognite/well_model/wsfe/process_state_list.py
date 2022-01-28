import time
from typing import Any, Dict, List

import pandas as pd

from cognite.well_model.wsfe.log_state_manager import LogStateManager
from cognite.well_model.wsfe.models import ProcessState, ProcessStatus


class ProcessStateList:
    _RESOURCE = None
    STATUS_COMPLETE = [ProcessStatus.ready, ProcessStatus.processing]

    def __init__(self, client, resources: List[ProcessState]):
        self._client = client
        self.data = resources

    def dump(self, camel_case: bool = False) -> List[Dict[str, Any]]:
        """Dump the instance into a json serializable Python data type.

        Args:
            camel_case (bool): Use camelCase for attribute names. Defaults to False.

        Returns:
            List[Dict[str, Any]]: A list of dicts representing the instance.
        """
        return [resource.dump(camel_case=camel_case) for resource in self.data]

    def to_pandas(self, camel_case=True) -> pd.DataFrame:
        """Generate a Pandas Dataframe

        Args:
            camel_case (bool, optional): snake_case if false and camelCase if
                true. Defaults to True.

        Returns:
            DataFrame:
        """
        return pd.DataFrame(self.dump(camel_case=camel_case))

    def wait(self):
        """Wait until the all jobs have completed.

        While waiting, it will poll the service and print updates.
        """
        log_state = LogStateManager()
        while True:
            time.sleep(2)
            self.refresh_status()
            log_state.add_log(self.data)
            if log_state.is_complete():
                log_state.print_summary(self.data)
                return

    def refresh_status(self):
        """Refresh the statuses."""
        self.data = self._client.status([x.process_id for x in self.data]).data

    def _repr_html_(self):
        return self.to_pandas(camel_case=True)._repr_html_()

    def __getitem__(self, item):
        return self.data[item]

    def __iter__(self):
        return self.data.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self.data]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.data.__len__()
