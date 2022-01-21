import os
from .experiment_messages import *
from cellworld import *
from tcp_messages import MessageServer, Message
from cellworld_tracking import TrackingClient
from datetime import datetime, timedelta


class ExperimentService(MessageServer):
    def __init__(self, tracker_ip: str = "127.0.0.1"):
        MessageServer.__init__(self)
        self.tracking_service = None
        self.router.add_route("set_tracking_service_ip", self.set_tracking_service_ip, str)
        self.router.add_route("start_experiment", self.start_experiment, StartExperimentRequest)
        self.router.add_route("start_episode", self.start_episode, StartEpisodeRequest)
        self.router.add_route("finish_episode", self.finish_episode)
        self.router.add_route("finish_experiment", self.finish_experiment, FinishExperimentRequest)
        self.router.add_route("get_experiment", self.get_experiment, GetExperimentRequest)
        self.allow_subscription = True
        self.active_experiment = None
        self.active_episode = None
        self.episode_in_progress = False
        self.tracking_client = None
        self.tracking_service_ip = None
        self.on_step = self.__process_step__
        self.on_experiment_started = None
        self.on_episode_started = None
        self.on_episode_finished = None
        self.on_experiment_finished = None

    @staticmethod
    def get_experiment_file(experiment_name: str):
        return "logs/" + experiment_name + ".json"

    def start(self):
        return MessageServer.start(self, ExperimentService.port())

    def __process_step__(self, step):
        if self.active_experiment:
            self.active_episode.trajectories.append(step)

    def start_experiment(self, parameters: StartExperimentRequest) -> StartExperimentResponse:
        new_experiment = Experiment(world_configuration_name=parameters.world.world_configuration,
                                    world_implementation_name=parameters.world.world_implementation,
                                    occlusions=parameters.world.occlusions,
                                    duration=parameters.duration,
                                    subject_name=parameters.subject_name,
                                    start_time=datetime.now())
        new_experiment.set_name(parameters.prefix, parameters.suffix)
        new_experiment.save(ExperimentService.get_experiment_file(new_experiment.name))

        response = StartExperimentResponse()
        response.experiment_name = new_experiment.name
        response.start_date = new_experiment.start_time
        response.world = parameters.world
        response.subject_name = parameters.subject_name
        response.duration = parameters.duration
        self.broadcast_subscribed(Message("experiment_started", response))

        if self.on_experiment_started:
            self.on_experiment_started(response)

        return response

    def start_episode(self, parameters: StartEpisodeRequest) -> bool:
        if self.episode_in_progress:
            return False
        experiment = Experiment.load_from_file(ExperimentService.get_experiment_file(parameters.experiment_name))
        if experiment:
            self.active_experiment = experiment.name
            self.active_episode = Episode()
            self.episode_in_progress = True
            if self.tracking_service_ip:
                self.tracking_client = TrackingClient();
                self.tracking_client.connect(self.tracking_service_ip)
                self.tracking_client.register_consumer(self.__process_step__)
            self.broadcast_subscribed(Message("episode_started", self.active_experiment))
            if self.on_episode_started:
                self.on_episode_started(self.active_experiment)
            return True
        return False

    def finish_episode(self, m) -> bool:
        if not self.episode_in_progress:
            return False

        experiment = Experiment.load_from_file(ExperimentService.get_experiment_file(self.active_experiment))
        if experiment:
            self.active_episode.end_time = datetime.now()
            experiment.episodes.append(self.active_episode)
            experiment.save(ExperimentService.get_experiment_file(self.active_experiment))
            self.episode_in_progress = False
            if self.tracking_client:
                self.tracking_client.unregister_consumer()
                self.tracking_client.disconnect()
                self.tracking_client = None
            self.broadcast_subscribed(Message("episode_finished", self.active_experiment))
            if self.on_episode_finished:
                self.on_episode_finished(self.active_experiment)
            return True
        return False

    def finish_experiment(self, parameters: FinishExperimentRequest) -> bool:
        self.broadcast_subscribed(Message("experiment_finished", parameters))
        if self.on_experiment_finished:
            self.on_experiment_finished(parameters)
        return True

    @staticmethod
    def get_experiment(parameters: GetExperimentRequest) -> GetExperimentResponse:
        response = GetExperimentResponse()
        experiment = Experiment.load_from_file(ExperimentService.get_experiment_file(parameters.experiment_name))
        if experiment:
            end_time = experiment.start_time + timedelta(seconds=experiment.duration)
            if end_time < datetime.now():
                remaining = 0
            else:
                remaining = (end_time - datetime.now()).seconds
            print("remaining time", remaining)
            response.experiment_name = experiment.name
            response.start_date = experiment.start_time
            response.duration = experiment.duration
            response.remaining_time = remaining
        return response

    def set_tracking_service_ip(self, ip: str):
        self.tracking_service_ip = ip
        return True

    @staticmethod
    def port() -> int:
        default_port = 4540
        if os.environ.get("CELLWORLD_EXPERIMENT_SERVICE_PORT"):
            try:
                return int(os.environ.get("CELLWORLD_EXPERIMENT_SERVICE_PORT"))
            finally:
                pass
        return default_port
