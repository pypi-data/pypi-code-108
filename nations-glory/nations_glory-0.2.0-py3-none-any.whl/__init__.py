from enum import Enum
class Servers(Enum):
    BLUE = 'blue'
    ORANGE = 'orange'
    YELLOW = 'yellow'
    WHITE = 'white'
    BLACK = 'black'
    CYAN = 'cyan'
    LIME = 'lime'
    CORAL = 'coral'
    PINK = 'pink'
    ALPHA = 'alpha'
    SIGMA = 'sigma'
    GAMMA = 'gamma'
    OMEGA = 'omega'
    PURPLE = 'purple'

    def get_map_url(self):
        return "https://%s.nationsglory.fr" % self.value