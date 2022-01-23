from schemdraw import Drawing
from schemdraw import elements as elm

from .input import Input


def draw_void():
    drawing = Drawing()

    transistor = drawing.add(elm.transistors.BjtNpn().right())

    drawing.push()
    drawing += elm.Line().up()
    drawing += elm.Line().left().length(drawing.unit/2)

    drawing.push()
    drawing += elm.Dot()
    drawing += elm.SourceV().up().reverse().label('Vcc')
    drawing += elm.Ground().left()

    drawing.pop()
    drawing += elm.Line().left().length(drawing.unit/2)
    drawing += elm.Resistor().down().label('R1')
    drawing += elm.Line().down().length(0.24*drawing.unit)
    drawing += elm.Dot()

    drawing.push()
    drawing += elm.Line().to(transistor.base)

    drawing.pop()
    drawing.push()
    drawing += elm.Line().left().length(drawing.unit/4)
    drawing += elm.Capacitor().left().reverse().label('C1')
    drawing += elm.Line().left().length(drawing.unit/4)
    drawing += elm.Dot().label('Vi')

    drawing.pop()
    drawing += elm.Resistor().label('R2')
    drawing += elm.Ground()

    drawing += elm.Resistor().label('Re').down().at(transistor.emitter).length(0.78*drawing.unit)
    drawing += elm.Ground()

    drawing += elm.Dot().at(transistor.emitter)
    drawing += elm.Capacitor().right().label('C2')
    drawing += elm.Dot().label('Vo')

    return drawing


def draw(amplifier_input: Input):
    R2 = str(round(amplifier_input.R2, 2))
    R1 = str(round(amplifier_input.R1, 2))
    Re = str(round(amplifier_input.Re, 2))
    Vcc = str(round(amplifier_input.Vcc, 2))

    drawing = Drawing()

    transistor = drawing.add(elm.transistors.BjtNpn().right())

    drawing.push()
    drawing += elm.Line().up()
    drawing += elm.Line().left().length(drawing.unit/2)

    drawing.push()
    drawing += elm.Dot()
    drawing += elm.SourceV().up().reverse().label(Vcc)
    drawing += elm.Ground().left()

    drawing.pop()
    drawing += elm.Line().left().length(drawing.unit/2)
    drawing += elm.Resistor().down().label(R1)
    drawing += elm.Line().down().length(0.24*drawing.unit)
    drawing += elm.Dot()

    drawing.push()
    drawing += elm.Line().to(transistor.base)

    drawing.pop()
    drawing.push()
    drawing += elm.Line().left().length(drawing.unit/4)
    drawing += elm.Capacitor().left().reverse().label('C1')
    drawing += elm.Line().left().length(drawing.unit/4)
    drawing += elm.Dot().label('Vi')

    drawing.pop()
    drawing += elm.Resistor().label(R2)
    drawing += elm.Ground()

    drawing += elm.Resistor().label(Re).down().at(transistor.emitter).length(0.78*drawing.unit)
    drawing += elm.Ground()

    drawing += elm.Dot().at(transistor.emitter)
    drawing += elm.Capacitor().right().label('C2')
    drawing += elm.Dot().label('Vo')

    return drawing
