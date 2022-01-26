from schemdraw import Drawing
from schemdraw import elements as elm

from .output import Output


def draw_equivalent_model_void():
    drawing = Drawing()
    drawing += elm.Dot().label('Vi')
    drawing += elm.Resistor().right().label('Zi')
    drawing += elm.Ground()
    drawing += elm.Dot()
    drawing += elm.SourceControlledI().right()
    drawing += elm.Resistor().right().label('Zo')
    drawing += elm.Dot().label('Vo')

    return drawing


def draw_equivalent_model(output: Output):
    Zi = str(round(output.Zi, 2))
    Zo = str(round(output.Zo, 2))
    drawing = Drawing()
    drawing += elm.Dot().label('Vi')
    drawing += elm.Resistor().right().label(Zi)
    drawing += elm.Ground()
    drawing += elm.Dot()
    drawing += elm.SourceControlledI().right()
    drawing += elm.Resistor().right().label(Zo)
    drawing += elm.Dot().label('Vo')

    return drawing
