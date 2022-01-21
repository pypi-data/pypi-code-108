from replifactory.device import BaseDevice


class MorbidostatDevice(BaseDevice):
    """
    Device with tubing connected from pumps into cultures.
       ┌────«───╦────«───╦────«───╦────«───╦────«───╦────«───╦─────«─── PUMP1 (MEDIUM)
       │┌───«────╦───«────╦───«────╦───«────╦───«────╦───«────╦────«─── PUMP2 (DRUG 1)
       ││┌──«─────╦──«─────╦──«─────╦──«─────╦──«─────╦──«─────╦───«─── PUMP3 (DRUG 2)
       │││┌───»────╦───»────╦───»────╦───»────╦───»────╦───»────╦────»─ PUMP4 (VACUUM)
       ││││     ││││     ││││     ││││     ││││     ││││     ││││
       ││││     ││││     ││││     ││││     ││││     ││││     ││││
      »││││«   »││││«   »││││«   »││││«   »││││«   »││││«   »││││«     << Pinch Valves
       ││││     ││││     ││││     ││││     ││││     ││││     ││││
       ││││     ││││     ││││     ││││     ││││     ││││     ││││
     ▓▓││││▓▓ ▓▓││││▓▓ ▓▓││││▓▓ ▓▓││││▓▓ ▓▓││││▓▓ ▓▓││││▓▓ ▓▓││││▓▓    << Vial Cap
     ▓│   ││▓ ▓│   ││▓ ▓│   ││▓ ▓│   ││▓ ▓│   ││▓ ▓│   ││▓ ▓│   ││▓
      │   ││   │   ││   │   ││   │   ││   │   ││   │   ││   │   ││
      │   ││   │   ││   │   ││   │   ││   │   ││   │   ││   │   ││     << Vacuum needle
      │~~~~│   │~~~~│   │~~~~│   │~~~~│   │~~~~│   │~~~~│   │~~~~│     << Liquid level
      │    │   │    │   │    │   │    │   │    │   │    │   │    │
      └────┘   └────┘   └────┘   └────┘   └────┘   └────┘   └────┘
      Vial 1   Vial 2   Vial 3   Vial 4   Vial 5   Vial 6   Vial 7

    Can be used to run CHEMOSTAT, TURBIDOSTAT and MORBIDOSTAT experiments.
    Pumps 1,2,3 transfer medium from stock bottles into the cultures
    Pump 4 transfers medium from the cultures into the waste bottle

    Not to be confused with Lagoon device, which has a different tubing arrangement.
    """

    def __init__(self, ftdi_address='ftdi://ftdi:2232h', connect=False):
        super().__init__(ftdi_address=ftdi_address, connect=connect)
