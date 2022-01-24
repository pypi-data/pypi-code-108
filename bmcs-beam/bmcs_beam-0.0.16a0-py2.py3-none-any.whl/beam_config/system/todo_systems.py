# elif config == BoundaryConfig.THREE_SPAN_DIST_LOAD:
#     # 3 span distributed load example
#     beam.apply_load(R1, 0, -1)
#     beam.apply_load(R2, L / 3, -1)
#     beam.apply_load(R3, 2 * L / 3, -1)
#     beam.apply_load(R4, L, -1)
#     beam.apply_load(F, 0, 0)
#     beam.bc_deflection = [(0, 0), (L / 3, 0), (2 * L / 3, 0), (L, 0)]
#
# elif config == BoundaryConfig.THREE_PB_FIXED_SUPPORT:
#     # fixed support example
#     beam.apply_load(R1, 0, -1)
#     beam.apply_load(M1, 0, -2)
#     beam.apply_load(R2, L, -1)
#     beam.apply_load(M2, L, -2)
#     beam.apply_load(F, L / 2, -1)
#     beam.bc_deflection = [(0, 0), (L, 0)]
#     beam.bc_slope = [(0, 0), (L, 0)]
#
# elif config == BoundaryConfig.SINGLE_MOMENT:
#     # single moment example
#     beam.apply_load(R1, 0, -1)
#     beam.apply_load(R2, L, -1)
#     beam.apply_load(-F, L / 2, -2)
#     beam.bc_deflection = [(0, 0), (L, 0)]
#
# elif config == BoundaryConfig.FIXED_SUPPORT_DIST_LOAD:
#     beam.apply_load(R1, 0, -1)
#     beam.apply_load(M1, 0, -2)
#     beam.apply_load(R2, L, -1)
#     beam.apply_load(M2, L, -2)
#     beam.apply_load(F, 0, 0)
#     beam.bc_deflection = [(0, 0), (L, 0)]
#     beam.bc_slope = [(0, 0), (L, 0)]
#
# elif config == BoundaryConfig.FIXED_AND_ROLLER_SUPPORT_DIST_LOAD:
#     beam.apply_load(R1, 0, -1)
#     beam.apply_load(R2, L, -1)
#     beam.apply_load(M2, L, -2)
#     beam.apply_load(F, 0, 0)
#     beam.bc_deflection = [(0, 0), (L, 0)]
#     beam.bc_slope = [(L, 0)]