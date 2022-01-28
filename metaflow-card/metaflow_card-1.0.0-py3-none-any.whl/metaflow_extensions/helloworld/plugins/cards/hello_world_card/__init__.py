from metaflow.cards import MetaflowCard

class HelloWorldCard(MetaflowCard):

    type = 'helloworld'
    
    def __init__(self, options={"attribute":"html"}, components=[], graph=None):
        self._attribute = "html"
        if options and "attribute" in options:
            self._attribute = options["attribute"]
    
    def render(self, task):
        if self._attribute in task:
            tsk_data = task[self._attribute].data
        return str(tsk_data)

CARDS = [HelloWorldCard]