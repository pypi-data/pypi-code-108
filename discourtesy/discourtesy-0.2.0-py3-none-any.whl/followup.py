from loguru import logger

from discourtesy.utils import simple_message


class FollowupTask:
    def __init__(self, coroutine, application, interaction):
        self.coroutine = coroutine

        self.application = application
        self.interaction = interaction

    async def __call__(self):
        response = await self.coroutine(self.application, self.interaction)

        if not response:
            response = "This command is currently not available."

        if isinstance(response, str):
            response = simple_message(response)

        logger.info(f"{self.coroutine.__name__} followup executed.")

        await self.application.http.create_followup_message(
            self.interaction["token"], response
        )
