"""
Test minimal dependency dag export (used for scheduler deployments)
"""


def test_workflow_export(workflow_tasks, workflow, export_path):
    """
    Given: A workflow instance with tasks in the
      structure of A >> [B, C] >> D
    When: Exporting the dag
    Then: The exported dag compiles
    """
    workflow_instance, category, name, version = workflow
    TaskA, TaskB, TaskC, TaskD = workflow_tasks
    task_definitions = {
        TaskA: None,  # none
        TaskB: TaskA,  # single
        TaskC: TaskA,  # single
        TaskD: [TaskB, TaskC],  # list
    }
    for task, upstream in task_definitions.items():
        workflow_instance.add_node(task, upstreams=upstream)

    # When
    dag_file = workflow_instance.export(export_path)
    # Then
    with dag_file.open(mode="r") as f:
        compile(f.read(), filename=f"{category}_{name}_{version}.pyc", mode="exec")
    assert True  # exception not raised from compile
