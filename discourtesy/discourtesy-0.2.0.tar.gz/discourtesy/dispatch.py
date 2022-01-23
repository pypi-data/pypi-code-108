import datetime

from loguru import logger

from discourtesy.utils import simple_message


class Dispatch:
    def __init__(self):
        self.slash_command_callbacks = dict()
        self.slash_command_followup_callbacks = dict()

        self.user_command_callbacks = dict()
        self.message_command_callbacks = dict()

        self.component_callbacks = dict()
        self.component_timeouts = dict()

    def add_command(self, command):
        if command.input_type == 1:
            if command.followup:
                self.slash_command_followup_callbacks[
                    command.name
                ] = command.coroutine
            else:
                self.slash_command_callbacks[command.name] = command.coroutine
        elif command.input_type == 2:
            self.user_command_callbacks[command.name] = command.coroutine
        elif command.input_type == 3:
            self.message_command_callbacks[command.name] = command.coroutine

    def add_component(self, component):
        try:
            self.component_callbacks[component.name].append(
                component.coroutine
            )
        except KeyError:
            self.component_callbacks[component.name] = [component.coroutine]

        if component.timeout != 0:
            self.component_timeouts[component.name] = component.timeout

    async def execute_command(self, application, interaction):
        command_name = interaction["data"]["name"]

        coroutine = None

        if interaction["data"].get("type") == 1:
            coroutine = self.slash_command_callbacks.get(command_name)

            if not coroutine:
                task = self.slash_command_followup_callbacks.get(command_name)

                if task:
                    return str(), task

        elif interaction["data"].get("type") == 2:
            coroutine = self.user_command_callbacks.get(command_name)
        elif interaction["data"].get("type") == 3:
            coroutine = self.message_command_callbacks.get(command_name)

        if coroutine is None:
            logger.warning(f"Command {command_name} could not be found.")

            return simple_message("This command is currently not available.")

        response = await coroutine(application, interaction)

        if isinstance(response, str):
            response = simple_message(response)

        logger.info(f"Command {command_name} executed.")

        return response, None

    async def execute_component(self, client, interaction):
        component_name = interaction["data"]["custom_id"]

        coroutines = self.component_callbacks.get(component_name)

        if not coroutines:
            logger.warning(f"Component {component_name} could not be found.")

            return

        timeout = self.component_timeouts.get(component_name)

        if timeout is not None:
            start = datetime.datetime.fromisoformat(
                interaction["message"]["timestamp"]
            )
            now = datetime.datetime.now(datetime.timezone.utc)

            if int((now - start).total_seconds()) > timeout:
                logger.info(f"Component {component_name} failed, timed out.")

                return

        response = None

        for coroutine in coroutines:
            maybe_response = await coroutine(client, interaction)

            if maybe_response is not None:
                response = maybe_response

        if isinstance(response, str):
            response = simple_message(response)

        logger.info(f"Component {component_name} executed.")

        return response
