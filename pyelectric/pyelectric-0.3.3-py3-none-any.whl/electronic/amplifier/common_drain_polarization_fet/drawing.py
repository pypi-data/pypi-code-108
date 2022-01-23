from schemdraw import Drawing
from schemdraw import elements as elm

from .input import Input


def draw_void():
    drawing = Drawing()

    transistor = drawing.add(elm.transistors.JFetP().right().reverse())

    drawing += elm.SourceV().at(transistor.drain).up().label('Vdd').reverse()
    drawing += elm.Ground().left()

    drawing += elm.Line().left().at(transistor.gate).length(drawing.unit/4)

    drawing.push()
    drawing += elm.Dot()
    drawing += elm.Resistor().down().label('Rg')
    drawing += elm.Ground()

    drawing.pop()
    drawing += elm.Capacitor().left()
    drawing += elm.Dot().label('Vi')

    drawing += elm.Dot().at(transistor.source).down()

    drawing.push()
    drawing += elm.Resistor().down().label('Rs').length(drawing.unit*0.857)
    drawing += elm.Ground()

    drawing.pop()
    drawing += elm.Capacitor().right().label('C2')
    drawing += elm.Dot().label('Vo')

    return drawing


def draw(amplifier_input: Input):
    Vdd = str(amplifier_input.Vdd)
    Rg = str(amplifier_input.Rg)
    Rs = str(amplifier_input.Rs)

    drawing = Drawing()

    transistor = drawing.add(elm.transistors.JFetP().right().reverse())

    drawing += elm.SourceV().at(transistor.drain).up().label(Vdd).reverse()
    drawing += elm.Ground().left()

    drawing += elm.Line().left().at(transistor.gate).length(drawing.unit/4)

    drawing.push()
    drawing += elm.Dot()
    drawing += elm.Resistor().down().label(Rg)
    drawing += elm.Ground()

    drawing.pop()
    drawing += elm.Capacitor().left()
    drawing += elm.Dot().label('Vi')

    drawing += elm.Dot().at(transistor.source).down()

    drawing.push()
    drawing += elm.Resistor().down().label(Rs).length(drawing.unit*0.857)
    drawing += elm.Ground()

    drawing.pop()
    drawing += elm.Capacitor().right().label('C2')
    drawing += elm.Dot().label('Vo')

    return drawing
