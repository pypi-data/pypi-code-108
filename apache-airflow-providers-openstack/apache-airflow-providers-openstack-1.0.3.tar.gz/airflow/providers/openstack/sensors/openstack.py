
from ..hooks.openstack import OpenstackHook
from airflow.sensors.base import BaseSensorOperator


class OpenstackSensor(BaseSensorOperator):
    def __init__(self, *, test_type: str, os_conn_id: str, **kwargs):
        super().__init__(**kwargs)
        self.test_type = test_type
        self.os_conn_id = os_conn_id

    def _create_hook(self) -> OpenstackHook:
        return OpenstackHook(os_conn_id=self.os_conn_id)

    def poke(self, context: dict) -> bool:
        obj_id = context['ti'].xcom_pull(key='return_value')
        if obj_id is None:
            return False
        with self._create_hook() as hook:
            if self.test_type == "snap":
                snap = hook.get_snapshot_by_id(obj_id)
                return snap.status == "available"
            elif self.test_type == "volume":
                volume = hook.get_volume_by_id(obj_id)
                return volume.status == "available"
            elif self.test_type == "image":
                image = hook.get_image_by_id(obj_id)
                return image.status == "active"
            return False


