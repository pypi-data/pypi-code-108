from .experiment_messages import *
from tcp_messages import MessageClient, Message
from .experiment_service import ExperimentService
from cellworld import World_info


class ExperimentClient(MessageClient):
    def __init__(self):
        MessageClient.__init__(self)
        self.router.add_route("experiment_started", self.__process_experiment_started__, StartExperimentResponse)
        self.router.add_route("episode_started", self.__process_episode_started__, str)
        self.router.add_route("episode_finished", self.__process_episode_finished__, str)
        self.router.add_route("experiment_finished", self.__process_experiment_finished__, str)
        self.on_experiment_started = None
        self.on_experiment_finished = None
        self.on_episode_started = None
        self.on_episode_finished = None

    def subscribe(self):
        return self.send_request(Message("!subscribe"), 0).body == "success"

    def __process_experiment_started__(self, parameters: StartExperimentResponse):
        if self.on_experiment_started:
            self.on_experiment_started(parameters)

    def __process_episode_started__(self, experiment_name: str):
        if self.on_episode_started:
            self.on_episode_started(experiment_name)

    def __process_episode_finished__(self, experiment_name: str):
        if self.on_episode_finished:
            self.on_episode_finished(experiment_name)

    def __process_experiment_finished__(self, experiment_name: str):
        if self.on_experiment_finished:
            self.on_experiment_finished(experiment_name)


    def connect(self, ip: str = "127.0.0.1"):
        MessageClient.connect(self, ip, ExperimentService.port())

    def start_experiment(self, prefix: str, suffix: str, world_configuration: str, world_implementation: str, occlusions: str, subject_name: str, duration: int) -> StartExperimentResponse:
        parameters = StartExperimentRequest(prefix=prefix, suffix=suffix, world=World_info(world_configuration, world_implementation, occlusions), subject_name=subject_name, duration=duration)
        return self.send_request(Message("start_experiment", parameters), 5000).get_body(StartExperimentResponse)

    def start_episode(self, experiment_name: str) -> str:
        return self.send_request(Message("start_episode", StartEpisodeRequest(experiment_name=experiment_name)), 5000).get_body(bool)

    def finish_episode(self) -> str:
        return self.send_request(Message("finish_episode"), 5000).get_body(bool)

    def finish_experiment(self, experiment_name: str):
        return self.send_request(Message("finish_experiment", FinishExperimentRequest(experiment_name=experiment_name)), 5000).get_body(bool)

    def get_experiment(self, experiment_name: str) -> GetExperimentResponse:
        return self.send_request(Message("get_experiment", GetExperimentRequest(experiment_name=experiment_name)), 5000).get_body(GetExperimentResponse)

    def is_active(self, experiment_name: str) -> bool:
        return self.get_experiment(experiment_name).remaining_time > 0

