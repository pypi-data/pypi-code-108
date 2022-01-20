from pangeamt_tea.project.workflow.stage.base_stage import BaseStage


class PublishStage(BaseStage):
    NAME = 'publish'

    def __init__(self, workflow):
        super().__init__(workflow, self.NAME)

    async def run(self):
        return {

        }