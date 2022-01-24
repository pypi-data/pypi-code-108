from typing import Any, List, Optional, Dict, Union, Iterable

from adagio.instances import TaskContext, WorkflowContext
from adagio.specs import InputSpec, OutputSpec, TaskSpec, WorkflowSpec
from triad.utils.assertion import assert_or_throw
from triad.utils.hash import to_uuid
from triad.collections import ParamDict
from qpd.qpd_engine import QPDEngine
from qpd.dataframe import Column, DataFrame, DataFrames


class QPDWorkflowContext(WorkflowContext):
    def __init__(self, qpd_engine: QPDEngine, dfs: Dict[str, Any]):
        self._qpd_engine = qpd_engine
        self._dfs = DataFrames({k: qpd_engine.to_df(v) for k, v in dfs.items()})
        self._result: Any = None
        super().__init__()

    @property
    def qpd_engine(self) -> QPDEngine:
        return self._qpd_engine

    @property
    def dfs(self) -> DataFrames:
        return self._dfs

    def set_result(self, obj: Any) -> None:
        self._result = obj

    @property
    def result(self) -> Any:
        return self._result


class QPDTask(TaskSpec):
    def __init__(
        self,
        op_name: str,
        input_n: int = 0,
        output_n: int = 1,
        *args: Any,
        **kwargs: Any,
    ):
        self._op_name = op_name
        self._args = args
        self._kwargs = kwargs
        assert_or_throw(
            output_n <= 1,
            NotImplementedError("multiple output tasks"),
        )
        inputs = [
            InputSpec("_" + str(i), object, nullable=False) for i in range(input_n)
        ]
        outputs = [
            OutputSpec("_" + str(i), object, nullable=False) for i in range(output_n)
        ]
        super().__init__(
            configs=None,
            inputs=inputs,
            outputs=outputs,
            func=self.execute,
            deterministic=True,
            lazy=False,
        )

    def pre_add_uuid(self, *args: Any, **kwargs) -> str:
        return to_uuid(
            self.configs,
            self.inputs,
            self.outputs,
            self._op_name,
            self._args,
            self._kwargs,
            args,
            kwargs,
        )

    def __uuid__(self) -> str:
        return to_uuid(
            self.configs,
            self.inputs,
            self.outputs,
            self.node_spec,
            self._op_name,
            self._args,
            self._kwargs,
        )

    def execute(self, ctx: TaskContext) -> None:
        ctx.ensure_all_ready()
        op = ctx.workflow_context.qpd_engine
        res = op(self._op_name, *list(ctx.inputs.values()), *self._args, **self._kwargs)
        ctx.outputs["_0"] = res


class Create(QPDTask):
    def __init__(self, op_name: str, *args: Any, **kwargs: Any):
        super().__init__(op_name, 0, 1, *args, **kwargs)

    def create(self, op: QPDEngine, ctx: TaskContext) -> Any:  # pragma: no cover
        raise NotImplementedError

    def execute(self, ctx: TaskContext) -> None:
        op = ctx.workflow_context.qpd_engine
        res = self.create(op, ctx)
        ctx.outputs["_0"] = res


class CreateColumn(Create):
    def __init__(self, df_name: str, col_name: str):
        super().__init__("to_col", df_name, col_name)
        self._df_name = df_name
        self._col_name = col_name

    def create(self, op: QPDEngine, ctx: TaskContext) -> Any:
        return ctx.workflow_context.dfs[self._df_name][self._col_name]
        # return op(self._op_name, self._value, self._name)


class ExtractColumn(QPDTask):
    def __init__(self, name: str):
        super().__init__("extract_col", 1, 1, name)
        self._name = name

    def execute(self, ctx: TaskContext) -> None:
        op = ctx.workflow_context.qpd_engine
        res = op(self._op_name, ctx.inputs["_0"], self._name)
        ctx.outputs["_0"] = res


class CreateConstColumn(Create):
    def __init__(self, value: Any, name: str = ""):
        super().__init__("to_col", value, name)
        self._value = value
        self._name = name

    def create(self, op: QPDEngine, ctx: TaskContext) -> Any:
        return op(self._op_name, self._value, self._name)


class Output(QPDTask):
    def __init__(self):
        super().__init__("to_native", 1, 1)

    def execute(self, ctx: TaskContext) -> None:
        op = ctx.workflow_context.qpd_engine
        res = op(self._op_name, ctx.inputs["_0"])
        ctx.workflow_context.set_result(res)
        ctx.outputs["_0"] = res


class QPDTaskWrapper(object):
    def __init__(self, workflow: "QPDWorkflow", task: QPDTask):
        self._workflow = workflow
        self._task = task

    @property
    def workflow(self) -> "QPDWorkflow":
        return self._workflow

    @property
    def task(self) -> QPDTask:
        return self._task

    # def __uuid__(self) -> str:
    #     return self.task.__uuid__()


class WorkflowColumn(Column, QPDTaskWrapper):
    def __init__(self, workflow: "QPDWorkflow", task: QPDTask, col: str = ""):
        Column.__init__(self, None, col)
        QPDTaskWrapper.__init__(self, workflow, task)

    @property
    def native(self) -> Any:  # pragma: no cover
        raise NotImplementedError

    def rename(self, name) -> "WorkflowColumn":
        if name == self.name:
            return self
        task = self.workflow.add("rename", self.task, name)
        return WorkflowColumn(self.workflow, task, name)


class WorkflowDataFrame(DataFrame, QPDTaskWrapper):
    def __init__(self, *args: Any):
        assert_or_throw(len(args) > 0, "WorkflowDataFrame can't be empty")
        DataFrame.__init__(self, *args)

        def get_objs(objs) -> Iterable[QPDTaskWrapper]:
            for o in objs:
                if isinstance(o, (WorkflowColumn, WorkflowDataFrame)):
                    yield o
                # elif isinstance(o, List):
                #     for x in get_objs(o):
                #         yield x
                else:
                    raise ValueError(f"{o} is invalid")

        deps = list(get_objs(args))
        workflow = deps[0].workflow
        task = workflow.add("assemble_df", *deps)
        QPDTaskWrapper.__init__(self, workflow, task)

    def __getitem__(
        self, key: Union[str, List[str]]
    ) -> Union[WorkflowColumn, "WorkflowDataFrame"]:
        res = super().__getitem__(key)
        if isinstance(res, (WorkflowColumn, WorkflowDataFrame)):
            return res
        if isinstance(res, DataFrame):
            return WorkflowDataFrame(*list(res.values()))
        raise ValueError(f"{res} is invalid")  # pragma: no cover


class QPDWorkflow(object):
    def __init__(self, ctx: QPDWorkflowContext):
        self._spec = WorkflowSpec()
        self._tasks: Dict[str, QPDTask] = {}
        self._ctx = ctx
        self._dfs = DataFrames({k: self._extract_df(k) for k in ctx.dfs.keys()})

    @property
    def ctx(self) -> QPDWorkflowContext:
        return self._ctx

    @property
    def dfs(self) -> DataFrames:
        return self._dfs

    def run(self) -> Any:
        self.ctx.run(self._spec, {})
        return self.ctx.result

    def const_to_col(self, value: Any, name: str = "") -> WorkflowColumn:
        value = CreateConstColumn(value, name)
        value = self._add_task(value)
        return WorkflowColumn(self, value, name)

    def op_to_col(self, op: str, *args: Any, **kwargs: Any) -> WorkflowColumn:
        task = self.add(op, *args, **kwargs)
        return WorkflowColumn(self, task)

    def op_to_df(
        self, cols: List[str], op: str, *args: Any, **kwargs: Any
    ) -> WorkflowDataFrame:
        task = self.add(op, *args, **kwargs)

        def get_cols():
            deps: Dict[str, str] = {}
            self._add_dep(deps, task)
            for col in cols:
                value = ExtractColumn(col)
                value = self._add_task(value, deps)
                yield WorkflowColumn(self, value, col)

        return WorkflowDataFrame(*list(get_cols()))

    def show(self, df: WorkflowDataFrame) -> None:
        self.add("show", df)

    def show_col(self, col: WorkflowColumn) -> None:
        self.add("show_col", col)

    def assemble_output(self, *args: Any) -> None:
        task = self.add("assemble_df", *args)
        deps: ParamDict = {}
        self._add_dep(deps, task)
        self._add_task(Output(), deps)

    def add(self, op: str, *args: Any, **kwargs: Any) -> QPDTask:
        deps: ParamDict = {}
        for i in range(len(args)):
            if isinstance(args[i], (QPDTask, QPDTaskWrapper)):
                self._add_dep(deps, args[i])
        args = args[len(deps) :]
        task = QPDTask(op, len(deps), 1, *args, **kwargs)
        return self._add_task(task, deps)

    def _extract_df(self, df_name: str) -> WorkflowDataFrame:
        def extract_col(df_name: str, col_name: str) -> WorkflowColumn:
            task = CreateColumn(df_name, col_name)
            task = self._add_task(task)
            return WorkflowColumn(self, task, col_name)

        cols = self.ctx.dfs[df_name].keys()
        return WorkflowDataFrame(*[extract_col(df_name, x) for x in cols])

    def _add_task(self, task, dependencies: Optional[Dict[str, str]] = None) -> QPDTask:
        if dependencies is None:
            pre_add_id = task.pre_add_uuid()
        else:
            pre_add_id = task.pre_add_uuid(dependencies)
        if pre_add_id not in self._tasks:
            name = "_" + str(len(self._spec.tasks))
            task = self._spec.add_task(name, task, dependencies)
            self._tasks[pre_add_id] = task
        return self._tasks[pre_add_id]

    def _add_dep(self, deps: Dict[str, str], obj: Any):
        if isinstance(obj, QPDTask):
            oe = obj.name + "._0"
        elif isinstance(obj, QPDTaskWrapper):
            oe = obj.task.name + "._0"
        else:  # pragma: no cover
            raise ValueError(f"{obj} is invalid")
        deps[f"_{len(deps)}"] = oe
