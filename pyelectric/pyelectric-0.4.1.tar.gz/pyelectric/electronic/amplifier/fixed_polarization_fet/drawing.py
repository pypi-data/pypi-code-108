from schemdraw import Drawing
from schemdraw import elements as elm

from .input import Input


def draw_void():
    drawing = Drawing()

    transistor = drawing.add(elm.transistors.JFetP().reverse().right())
    drawing += elm.Line().left()

    drawing.push()
    drawing += elm.Dot()
    drawing += elm.Line().up().length(drawing.unit*0.3)
    drawing += elm.Resistor().up().label('Rg')
    drawing += elm.SourceV().up().label('Vgg').length(drawing.unit/2)
    drawing += elm.Ground().left()

    drawing.pop()
    drawing += elm.Capacitor().left()
    drawing += elm.Dot().label('Vi')

    drawing += elm.Resistor().up().at(transistor.drain).label('Rd')
    drawing += elm.SourceV().label('Vdd').reverse().length(drawing.unit/2)
    drawing += elm.Ground().left()

    drawing += elm.Line().at(transistor.source).down().length(drawing.unit/8)
    drawing += elm.Ground()

    drawing += elm.Dot().at(transistor.drain)
    drawing += elm.Capacitor().right().label('C2')
    drawing += elm.Dot().label('Vo')

    return drawing


def draw(amplifier_input: Input):
    Vdd = amplifier_input.Vdd
    Vgg = amplifier_input.Vgg
    Rd = amplifier_input.Rd
    Rg = amplifier_input.Rg

    drawing = Drawing()

    transistor = drawing.add(elm.transistors.JFetP().reverse().right())
    drawing += elm.Line().left()

    drawing.push()
    drawing += elm.Dot()
    drawing += elm.Line().up().length(drawing.unit*0.3)
    drawing += elm.Resistor().up().label(str(Rg))
    drawing += elm.SourceV().up().label(str(Vgg)).length(drawing.unit/2)
    drawing += elm.Ground().left()

    drawing.pop()
    drawing += elm.Capacitor().left()
    drawing += elm.Dot().label('Vi')

    drawing += elm.Resistor().up().at(transistor.drain).label(str(Rd))
    drawing += elm.SourceV().label(str(Vdd)).reverse().length(drawing.unit/2)
    drawing += elm.Ground().left()

    drawing += elm.Line().at(transistor.source).down().length(drawing.unit/8)
    drawing += elm.Ground()

    drawing += elm.Dot().at(transistor.drain)
    drawing += elm.Capacitor().right().label('C2')
    drawing += elm.Dot().label('Vo')

    return drawing