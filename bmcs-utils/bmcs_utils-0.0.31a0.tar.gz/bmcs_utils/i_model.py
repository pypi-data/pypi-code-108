
import traits.api as tr

class IModel(tr.Interface):
    '''Interactive model interface
    '''

    def get_sub_node(self, name):
        '''Return a node with subnodes by scanning the model components'''