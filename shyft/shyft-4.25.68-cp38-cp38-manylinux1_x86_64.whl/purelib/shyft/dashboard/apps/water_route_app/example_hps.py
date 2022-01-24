from shyft.energy_market import stm

from shyft.energy_market.core import ConnectionRole


def get_example_hps() -> stm.HydroPowerSystem:
    hps = stm.HydroPowerSystem(uid=0, name="Example HPS")
    rsv0 = hps.create_reservoir(uid=0, name="R0")

    tunnel0a = hps.create_waterway(uid=0, name="Tunnel 0A - R0 to power plant 0").input_from(rsv0)
    main_gate0a = tunnel0a.add_gate(uid=0, name="Main gate 0a")
    penstock0a = hps.create_waterway(uid=1, name="Turbine penstock 0a").input_from(tunnel0a)
    unit0a = hps.create_unit(uid=0, name='Unit 0A').input_from(penstock0a)

    tunnel0b = hps.create_waterway(uid=2, name="Tunnel 0B - R0 to power plant 0").input_from(rsv0)
    main_gate0b = tunnel0b.add_gate(uid=1, name="Main gate 0b")
    penstock0b = hps.create_waterway(uid=3, name="Turbine penstock 0b").input_from(tunnel0b)
    unit0b = hps.create_unit(uid=1, name='Unit 0B').input_from(penstock0b)

    plant0 = hps.create_power_plant(0, 'Power plant 0')
    plant0.add_unit(unit0a)
    plant0.add_unit(unit0b)
    draft_tube0a = hps.create_waterway(uid=4, name="Draft tube 0A").input_from(unit0a)
    draft_tube0b = hps.create_waterway(uid=5, name="Draft tube 0B").input_from(unit0b)

    rsv1 = hps.create_reservoir(uid=1, name="R1")

    tunnel1a = hps.create_waterway(uid=6, name="Tunnel 1A - R1 to power plant 1").input_from(rsv1)
    main_gate1a = tunnel1a.add_gate(uid=2, name="Main gate 1a")
    penstock1a = hps.create_waterway(uid=7, name="Turbine penstock 1a").input_from(tunnel1a)
    unit1a = hps.create_unit(uid=2, name='Unit 1A').input_from(penstock1a)

    plant1 = hps.create_power_plant(1, 'Power plant 1')
    plant1.add_unit(unit1a)
    draft_tube1a = hps.create_waterway(uid=8, name="Draft tube 1A").input_from(unit1a)

    rsv2 = hps.create_reservoir(uid=2, name="R2").input_from(draft_tube0a).input_from(draft_tube0b).input_from(draft_tube1a)

    tunnel2a = hps.create_waterway(uid=9, name="Tunnel 2A - R2 to power plant 2").input_from(rsv2)
    main_gate2a = tunnel2a.add_gate(uid=3, name="Main gate 2a")
    penstock2a = hps.create_waterway(uid=10, name="Turbine penstock 2a").input_from(tunnel2a)
    unit2a = hps.create_unit(uid=3, name='Unit 2A').input_from(penstock2a)

    plant2 = hps.create_power_plant(2, 'Power plant 2')
    plant2.add_unit(unit2a)
    draft_tube2a = hps.create_waterway(uid=11, name="Draft tube 2A").input_from(unit2a)

    river_to_ocean = hps.create_waterway(uid=12, name="River to ocean").input_from(draft_tube2a)

    flood_river0 = hps.create_waterway(13, "Flood river 0")
    flood_river0.input_from(rsv0, ConnectionRole.flood).output_to(rsv2)
    flood_gate0 = flood_river0.add_gate(4, "Flood gate 0")

    bypass_river0 = hps.create_waterway(14, "Bypass river 0")
    bypass_river0.input_from(rsv0, ConnectionRole.bypass).output_to(rsv2)
    bypass_gate0 = bypass_river0.add_gate(5, "Bypass gate 0")

    flood_river1 = hps.create_waterway(15, "Flood river 1")
    flood_river1.input_from(rsv1, ConnectionRole.flood).output_to(river_to_ocean)
    flood_gate1 = flood_river1.add_gate(6, "Flood gate 1")

    bypass_river1 = hps.create_waterway(16, "Bypass river 1")
    bypass_river1.input_from(rsv1, ConnectionRole.bypass).output_to(river_to_ocean)
    bypass_gate1 = bypass_river1.add_gate(7, "Bypass gate 1")

    flood_river2 = hps.create_waterway(17, "Flood river 2")
    flood_river2.input_from(rsv2, ConnectionRole.flood).output_to(river_to_ocean)
    flood_gate2 = flood_river2.add_gate(8, "Flood gate 2")

    bypass_river2 = hps.create_waterway(18, "Bypass river 2")
    bypass_river2.input_from(rsv2, ConnectionRole.bypass).output_to(river_to_ocean)
    bypass_gate2 = bypass_river2.add_gate(9, "Bypass gate 2")

    return hps
