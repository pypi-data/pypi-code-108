import datetime
import enum
import os
import subprocess
import typing
from threading import Lock

import fastapi
from dapr.clients import DaprClient
from fastapi import FastAPI
from pydantic import BaseModel
from wisdoms_dapr import consts, deps, schemas
from wisdoms_dapr.consts import ENV_NAME_SERVICE_RUN_MODE
from wisdoms_dapr.exceptions import ServiceErrorException


class RouteType(str, enum.Enum):
    """路由类型"""

    normal = 'normal'
    crontab = 'crontab'


class ServiceRouteInfo(BaseModel):
    """服务路由信息"""

    id: typing.Optional[str]
    path: str
    verb: str
    desc: typing.Optional[str]
    type: RouteType = RouteType.normal  # 路由类型


class ServiceObjectInfo(BaseModel):
    """服务对象信息"""

    name: str
    desc: typing.Optional[str]


class ServiceLogicInfo(BaseModel):
    """服务逻辑信息"""

    name: str
    desc: typing.Optional[str]


class ServiceRegisterInfo(BaseModel):
    """服务注册信息"""

    app_id: str
    version: str
    mode: schemas.ServiceRunMode = schemas.ServiceRunMode.dev
    server: typing.Literal['FastAPI', 'Django', 'Flask'] = 'FastAPI'
    desc: typing.Optional[str]
    timestamp: int
    routes: list[ServiceRouteInfo]
    objects: list[ServiceObjectInfo]
    logics: list[ServiceLogicInfo]


def extract_fastapi_route_info(
    app: fastapi.FastAPI,
    exclude_verbs: typing.Optional[set[str]] = None,
) -> list[ServiceRouteInfo]:
    """提取FastAPI路由信息"""

    result: list[ServiceRouteInfo] = []
    if not exclude_verbs:
        exclude_verbs = set()

    for r in app.router.routes:
        allow_verbs = r.methods - exclude_verbs
        for v in allow_verbs:
            result.append(
                ServiceRouteInfo(
                    id=getattr(r, 'unique_id', None),
                    path=r.path,
                    verb=v,
                    desc=getattr(r, 'description', None),
                    type=RouteType.crontab
                    if deps.ScheduleTaskRegister.find_route_schedule_dependency(r)
                    else RouteType.normal,
                )
            )

    return result


def extract_service_version_info() -> str:
    """提取服务版本信息"""

    try:
        r = subprocess.run(['git', 'rev-parse', 'HEAD'], shell=False, capture_output=True, text=True)
        return r.stdout.strip()
    except Exception:
        return 'v0.0.1'


def get_app_id() -> str:
    """获取服务ID"""

    return os.environ.get(consts.ENV_NAME_DAPR_APP_ID, '')


class FastAPIServiceRegister(object):
    """FastAPI Service Register

    设计：
    - 注册服务接口，方便对服务权限的管理
    - 提取服务中存在的定时调度依赖，用于定时任务的注册
    - 初始化服务运行相关环境变量，如：服务端口，dapr相关端口等
    """

    exclude_http_verbs: set[str] = {'OPTION', 'HEAD'}

    service_register_topic_name = consts.EVENT_TOPIC_NAME_SERVICE_REGISTER
    service_register_subscribe_route = consts.EVENT_SUBSCRIBE_ROUTE_SERVICE_REGISTER

    def __init__(
        self,
        app: FastAPI,
        app_id: str = '',
        run_mode: typing.Optional[schemas.ServiceRunMode] = None,
        desc: typing.Optional[str] = '',
        *,
        subscribe_infos: typing.Optional[list[schemas.DaprSubscribeInfoItem]] = None,
        pubsub_name: str = consts.DEFAULT_PUBSUB_NAME,
        schedule_tasks_register_method_name: str = 'v1/schedule/register',
        schedule_tasks_remove_method_name: str = 'v1/schedule/remove',
        remove_schedule_tasks_on_shutdown: bool = False,
    ) -> None:
        """
        初始化服务注册器

        :param app: FastAPI app实例
        :param app_id: 注册的服务名称
        :param run_mode: 运行模式
        :param desc: 服务描述
        :param pubsub_name: pubsub名称
        :param schedule_tasks_register_method_name: 定时任务注册接口名称
        :param schedule_tasks_remove_method_name: 定时任务移除接口名称
        :param remove_schedule_tasks_on_shutdown: 当服务关闭时是否移除定时任务
        """

        self.app = app
        if not app_id:
            app_id = get_app_id()

        if not app_id:
            raise ServiceErrorException(
                f'get dapr `app_id` failed, please set `app_id` in env or set app_id value in {self.__class__.__name__} __init__ function.'
            )

        self.app_id = app_id

        mode = os.getenv(ENV_NAME_SERVICE_RUN_MODE)
        if not mode:
            self.run_mode = schemas.ServiceRunMode.dev
        else:
            self.run_mode = {}

        self.run_mode = run_mode
        self.desc = desc
        self.subscribe_infos = subscribe_infos
        self.pubsub_name = pubsub_name

        self.schedule_tasks_register_method_name = schedule_tasks_register_method_name
        self.schedule_tasks_remove_method_name = schedule_tasks_remove_method_name
        self.remove_schedule_tasks_on_shutdown = remove_schedule_tasks_on_shutdown

        self.lock = Lock()
        self.is_registered: bool = False

    def get_register_service_info_subscribe_info(self) -> schemas.DaprSubscribeInfoItem:
        """注册服务注册订阅路由并返回注册服务信息订阅信息"""

        return schemas.DaprSubscribeInfoItem(
            topic=self.service_register_topic_name,
            pubsubname=self.pubsub_name,
            route=self.service_register_subscribe_route,
        )

    def add_dapr_subscribe_route(self):
        """添加dapr订阅路由"""

        # 获取调度路由订阅信息
        infos = deps.ScheduleTaskRegister(
            self.app_id,
            app=self.app,
            schedule_tasks_register_method_name=self.schedule_tasks_register_method_name,
            schedule_tasks_remove_method_name=self.schedule_tasks_remove_method_name,
            remove_schedule_tasks_on_shutdown=self.remove_schedule_tasks_on_shutdown,
        ).get_schedule_subscribe_schemas()

        # 添加服务注册订阅信息
        infos.append(self.get_register_service_info_subscribe_info())

        # 添加服务自定义订阅路由
        if self.subscribe_infos:
            infos.extend(self.subscribe_infos)

        # 添加dapr订阅注册路由
        if infos:
            self.app.get('/dapr/subscribe', tags=[consts.ROUTE_TAG_NAME_AUTO_REGISTER])(lambda: infos)

    def extract_register_info(self) -> ServiceRegisterInfo:
        """提取服务注册信息"""

        route_infos = extract_fastapi_route_info(app=self.app, exclude_verbs=self.exclude_http_verbs)
        version = extract_service_version_info()
        return ServiceRegisterInfo(
            app_id=self.app_id,
            version=version,
            mode=self.run_mode,
            desc=self.desc,
            timestamp=int(datetime.datetime.now().timestamp()),
            routes=route_infos,
        )

    def register_to_policy_service(self):
        """注册到policy服务"""

        with self.lock:

            if self.is_registered:
                return

            register_info = self.extract_register_info()
            with DaprClient() as client:
                try:
                    client.invoke_method(
                        app_id=consts.SERVICE_NAME_POLICY,
                        method_name=consts.INVOKE_ROUTE_POLICY_SERVICE_SCHEDULE_TASK_REGISTER,
                        data=register_info.json(),
                        content_type=consts.CONTENT_TYPE_JSON,
                        http_verb=consts.HTTP_VERB_POST,
                        metadata=None,
                    )
                    self.is_registered = True
                except Exception as e:
                    print('catch service register exception:', e)

    def register(self):
        """注册服务信息

        提取服务信息，并将其添加到服务的订阅事件中

        不直接注册的原因：dapr依赖服务先启动，而直接注册则要求dapr先启动
        """

        # 添加订阅路由
        self.add_dapr_subscribe_route()

        # 添加服务信息获取订阅路由
        # NOTE: 所有路由注册操作，必须先于注册信息提取
        self.app.post('/' + self.service_register_subscribe_route, tags=[consts.ROUTE_TAG_NAME_AUTO_REGISTER])(
            self.register_to_policy_service
        )

    def __call__(self):
        self.register()
