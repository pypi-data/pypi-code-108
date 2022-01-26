from meili_sdk.models.task import Task
from meili_sdk.resources.base import BaseResource


class TaskResource(BaseResource):
    def get_tasks(self, page=None, **filters):
        return self.get("sdk/tasks/", expected_class=Task, filters=filters, page=page)

    def create_task(self, task):
        return self.post("sdk/tasks/", expected_class=Task, data=task)

    def confirm_task(self, task):
        return self.post(f"sdk/tasks/{task.uuid}/", expected_class=Task, data=None)

    def fail_task(self, task):
        return self.delete(f"sdk/tasks/{task.uuid}/", expected_class=Task)

    def get_vehicle_task(self, vehicle):
        return self.get(
            f"sdk/vehicles/{vehicle.uuid}/current-task/", expected_class=Task
        )

    def update_vehicle_task(self, vehicle, goal_status, goal_id):
        return self.patch(
            f"sdk/vehicles/{vehicle.uuid}/current-task/",
            data={
                "goal_status": goal_status,
                "goal_id": goal_id,
            },
            expected_class=Task,
        )
