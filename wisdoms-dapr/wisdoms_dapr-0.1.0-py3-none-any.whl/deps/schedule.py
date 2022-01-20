import json
import logging
import typing
from threading import Lock

from dapr.clients import DaprClient
from fastapi.applications import FastAPI
from pydantic import BaseModel, root_validator
from starlette.routing import Route
from wisdoms_dapr import consts
from wisdoms_dapr.schemas import DaprSubscribeInfoItem

# Schedule Type Names
CRONTAB_SCHEDULE_TYPE_NAME = 'crontab'
TIMEDELTA_SCHEDULE_TYPE_NAME = 'timedelta'
SOLAR_SCHEDULE_TYPE_NAME = 'solar'

ALL_SCHEDULE_TYPE_NAMES = [CRONTAB_SCHEDULE_TYPE_NAME, TIMEDELTA_SCHEDULE_TYPE_NAME, SOLAR_SCHEDULE_TYPE_NAME]

INVOKE_CALL_MODE_NAME = 'invoke'
PUBLISH_CALL_MODE_NAME = 'publish'
ALL_CALL_MODE_NAMES = [INVOKE_CALL_MODE_NAME, PUBLISH_CALL_MODE_NAME]
CallModeNameType = typing.Literal['invoke', 'publish']

ALL_SOLAR_EVENTS = {
    'dawn_astronomical',
    'dawn_nautical',
    'dawn_civil',
    'sunrise',
    'solar_noon',
    'sunset',
    'dusk_civil',
    'dusk_nautical',
    'dusk_astronomical',
}


class DaprInvokeServiceSchema(BaseModel):
    """Dapr 调用服务"""

    # app_id: typing.Optional[str]
    # method: typing.Optional[str]
    # verb: typing.Optional[str]
    content_type: typing.Optional[str]
    query: typing.Optional[dict[str, str]]
    data: typing.Any


class DaprPublishEventSchema(BaseModel):
    """Dapr 发布事件"""

    pubsub_name: typing.Optional[str]
    topic_name: typing.Optional[str]
    data: typing.Any
    metadata: typing.Optional[dict[str, str]]
    data_content_type: typing.Optional[str]


class CrontabScheduleRuleSchema(BaseModel):
    """
    Crontab Schedule Rule

    Doc: https://docs.celeryproject.org/en/stable/reference/celery.schedules.html#celery.schedules.crontab
    """

    minute: str = "*"
    hour: str = "*"
    day_of_week: str = "*"
    day_of_month: str = "*"
    month_of_year: str = "*"

    @root_validator
    def load_data(cls, data: dict[str, str]) -> dict[str, str]:
        """验证crontab规则"""

        return data


class TimedeltaScheduleRuleSchema(BaseModel):
    """
    Timedelta Schedule Rule

    Doc: https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#available-fields
    Datetime timedelta: https://docs.python.org/zh-cn/3/library/datetime.html#timedelta-objects
    """

    microseconds: int = 0
    milliseconds: int = 0
    seconds: int = 0
    minutes: int = 0
    hours: int = 0
    days: int = 0
    weeks: int = 0

    @root_validator
    def load_data(cls, data: dict[str, int]) -> dict[str, int]:
        """验证数据"""

        if not any(data.values()):
            raise ValueError(f"timedelta rule value must not all be 0")

        return data


class SolarScheduleRuleSchema(BaseModel):
    """
    Solar Schedule Rule

    Doc: https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#solar-schedules
    """

    event: str
    lat: float
    lon: float

    @root_validator
    def load_data(cls, data: dict[str, typing.Union[str, int]]) -> dict[str, typing.Union[str, int]]:

        if data.get('event') not in ALL_SOLAR_EVENTS:
            raise ValueError(f"invalid event name, event must in {','.join(ALL_SOLAR_EVENTS)}")

        return data


class ScheduleTaskSchema(BaseModel):

    name: typing.Optional[str]  # 任务名称
    call_mode: str = INVOKE_CALL_MODE_NAME  # 调用方式
    call_info: typing.Optional[dict[str, typing.Any]]  # 调用信息
    schedule_type: str = CRONTAB_SCHEDULE_TYPE_NAME  # 调度信息
    schedule_rule: dict[str, typing.Any]  # 调度规则
    # Task Options: https://docs.celeryproject.org/en/stable/userguide/tasks.html#general
    task_options: typing.Optional[dict[str, typing.Any]] = None  # 任务调用选项
    is_cover: bool = True  # 是否覆盖同名任务
    relative: bool = False  # 是否相对于celery启动时间进行计时

    @root_validator(pre=True)
    def before_load_data(cls, data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """加载数据前验证数据"""

        # 调用方式判断
        call_mode = data.get('call_mode')
        if not call_mode or call_mode not in ALL_CALL_MODE_NAMES:
            raise ValueError(f"call mode must be in {ALL_CALL_MODE_NAMES}")

        # 根据调用方式验证调用信息
        call_info = data.get('call_info', {})
        if call_info:
            if call_mode == INVOKE_CALL_MODE_NAME:
                data['call_info'] = DaprInvokeServiceSchema(**call_info)
            elif call_mode == PUBLISH_CALL_MODE_NAME:
                data['call_info'] = DaprPublishEventSchema(**call_info)
            else:
                raise ValueError(f"invalid call mode: {call_mode}")

        # 调度类型判断
        schedule_type = data.get('schedule_type')
        if not schedule_type or schedule_type not in ALL_SCHEDULE_TYPE_NAMES:
            raise ValueError(f"schedule type must be set in {ALL_SCHEDULE_TYPE_NAMES}")

        # 根据schedule类型进行验证
        if schedule_type == CRONTAB_SCHEDULE_TYPE_NAME:
            data['schedule_rule'] = CrontabScheduleRuleSchema(**data['schedule_rule'])
        elif schedule_type == TIMEDELTA_SCHEDULE_TYPE_NAME:
            data['schedule_rule'] = TimedeltaScheduleRuleSchema(**data['schedule_rule'])
        elif schedule_type == SOLAR_SCHEDULE_TYPE_NAME:
            data['schedule_rule'] = SolarScheduleRuleSchema(**data['schedule_rule'])
        else:
            raise ValueError(f"invalid scheduler type: {schedule_type}")

        return data


class ScheduleDependency(object):
    def __init__(
        self,
        call_mode: typing.Literal['invoke', 'publish'],
        schedule_type: typing.Literal['crontab', 'solar', 'timedelta'],
        schedule_rule: dict[str, typing.Any],
        name: typing.Optional[str] = None,
        call_info: typing.Optional[dict[str, typing.Any]] = None,
        task_options: typing.Optional[dict[str, typing.Any]] = None,
        relative: bool = False,
    ) -> None:

        self.schedule_info = ScheduleTaskSchema(
            **{
                'name': name,
                'call_mode': call_mode,
                'call_info': call_info,
                'schedule_type': schedule_type,
                'schedule_rule': schedule_rule,
                'task_options': task_options,
                'relative': relative,
            }
        )

    def __call__(self):
        pass


class ScheduleTaskRegister(object):
    """调度任务注册器"""

    schedule_task_register_topic_name = consts.EVENT_TOPIC_NAME_SCHEDULE_TASK_REGISTER
    schedule_task_register_route = consts.EVENT_SUBSCRIBE_ROUTE_SCHEDULE_TASK_REGISTER

    def __init__(
        self,
        app_id: str,
        app: FastAPI,
        *,
        schedule_app_id: str = 'crontab_celery',
        schedule_pubsub_name: str = consts.DEFAULT_PUBSUB_NAME,
        schedule_tasks_register_method_name: str = 'v1/schedule/register',
        schedule_tasks_remove_method_name: str = 'v1/schedule/remove',
        remove_schedule_tasks_on_shutdown: bool = True,
    ) -> None:
        """
        :param app_id: 当前微服务id
        :param router: 当前FastAPI微服务的根路由实例
        :param schedule_app_id: 调度微服务id
        :param schedule_pubsub_name: 调度任务默认的pubsub名称
        :param schedule_task_register_topic_name: 调度微服务发布的注册调度任务的事件名称
        :param schedule_tasks_register_method_name: 调度微服务进行服务注册的路由名称
        :param schedule_tasks_remove_method_name: 调度微服务进行任务移除的路由名称
        :param remove_schedule_tasks_on_shutdown: 在FastAPI服务器关闭时是否移除所有调度任务
        """

        # NOTE: 属性声明顺序和代码逻辑相关
        self.app_id = app_id
        self.pubsub_name = schedule_pubsub_name
        self.app = app
        self.schedule_app_id = schedule_app_id
        self.schedule_tasks_register_method_name = schedule_tasks_register_method_name
        self.schedule_tasks_remove_method_name = schedule_tasks_remove_method_name
        self.subscribe_info: list[DaprSubscribeInfoItem] = [
            DaprSubscribeInfoItem(
                pubsubname=schedule_pubsub_name,
                topic=self.schedule_task_register_topic_name,
                route=self.schedule_task_register_route,
            ),
        ]  # 所有的订阅信息

        self.is_registered: bool = False

        self.tasks = self.get_schedule_tasks()
        self.lock = Lock()

        # 注册订阅注册调度任务事件的路由
        self.app.router.post('/' + self.schedule_task_register_route, tags=[consts.ROUTE_TAG_NAME_AUTO_REGISTER])(
            self.register
        )

        # 注册清理事件
        if remove_schedule_tasks_on_shutdown:
            self.app.on_event('shutdown')(self.remove)

    @staticmethod
    def find_route_schedule_dependency(r: Route) -> typing.Optional[ScheduleDependency]:
        """查找调度依赖"""

        if getattr(r, 'dependencies', None):
            for d in r.dependencies:
                if isinstance(d.dependency, ScheduleDependency):
                    return d.dependency

    def get_schedule_tasks(self) -> list[dict[str, typing.Any]]:
        """获取调度任务"""

        result: list[dict[str, typing.Any]] = []
        task_names: list[str] = []
        for r in self.app.router.routes:
            # 判断路由是否为定时路由，仅支持一个定时依赖
            schedule_dep = self.find_route_schedule_dependency(r)
            if not schedule_dep:
                continue

            # 添加调度依赖
            info = schedule_dep.schedule_info.dict()

            info['app_id'] = self.app_id
            if not info.get('name'):
                task_name: str = r.unique_id
                if task_name in task_names:
                    raise NameError(
                        f"task_name {task_name} exists, please specify name or rename the route function name."
                    )
                info['name'] = task_name
                task_names.append(task_name)

            # 生成调用信息
            call_info: dict[str, typing.Any] = {}
            if isinstance(info.get('call_info'), dict):
                call_info = info['call_info']

            if info['call_mode'] == 'invoke':
                call_info['app_id'] = self.app_id
                call_info['method'] = r.path[1:]
                call_info['verb'] = list(r.methods)[0]
            elif info['call_mode'] == 'publish':
                if not call_info.get('pubsub_name'):
                    call_info['pubsub_name'] = self.pubsub_name

                if not call_info.get('topic_name'):
                    call_info['topic_name'] = r.unique_id

                # 添加订阅信息
                self.subscribe_info.append(
                    DaprSubscribeInfoItem(
                        **{
                            'pubsubname': call_info['pubsub_name'],
                            'topic': call_info['topic_name'],
                            'route': r.path[1:],
                        }
                    )
                )
            else:
                logging.warning(f"invalid call mode: {info['call_mode']}")
                continue

            info['call_info'] = call_info
            result.append(info)

        return result

    def register(self) -> typing.Optional[dict[str, typing.Any]]:
        """注册调度任务"""

        with self.lock:
            if not self.is_registered:
                # 移除历史调度任务
                self.remove()

                # 注册当前所有调度任务
                with DaprClient() as c:
                    r = c.invoke_method(
                        app_id=self.schedule_app_id,
                        method_name=self.schedule_tasks_register_method_name,
                        data=json.dumps(self.tasks),
                        http_verb='POST',
                    )
                    self.is_registered = True
                    return json.loads(r.data)

            return None

    def remove(self):
        """移除调度任务"""

        with DaprClient() as c:
            r = c.invoke_method(
                app_id=self.schedule_app_id,
                method_name=self.schedule_tasks_remove_method_name,
                data=json.dumps({'app_id': self.app_id}),
                http_verb='POST',
            )
            print(r.data)

    def get_schedule_subscribe_info(self) -> list[dict[str, str]]:
        """获取调度的订阅信息"""

        return [item.dict() for item in self.subscribe_info]

    def get_schedule_subscribe_schemas(self) -> list[DaprSubscribeInfoItem]:
        """获取调度的订阅schema"""

        return self.subscribe_info
