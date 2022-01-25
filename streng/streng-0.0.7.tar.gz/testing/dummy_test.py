# bld = RCTypology()
# bld.from_old_analyses_name('4_du_59_bare')
#
# print(bld.storeys)
# print(bld.code)
# print(bld.structural_system)
# print(bld.infill_pattern)
#
# print(bld.riskue_name)
#
# bld2 = RCTypology()
# bld2.from_riskue_name('RC4.3MM')
# print(bld2.storeys)
# print(bld2.code_level)
# print(bld2.structural_system)
# print(bld2.infill_pattern)
#
# bld3 = RCTypology()
# print(bld3.storeys)
# print(bld3.code_level)
# print(bld3.structural_system)
# print(bld3.infill_pattern)


from streng.seismic_assessment.fragility import FragilityCurves

fc = FragilityCurves()

fc.means = [0.016, 0.072, 0.223, 0.429, 0.988]
# fc.means = [0.06672286, 0.12565208, 0.23399973, 0.35775175, 0.78358797]
fc.stddevs = [0.738, 0.738, 0.738, 0.738, 0.738]
# fc.stddevs = [0.733, 0.733, 0.733, 0.733, 0.733]
fc.thresholds = [0.001, 0.01, 0.1, 0.3, 0.6]
# fc.centrals = [0.0055, 0.055, 0.2, 0.45, 0.8]

# print(fc.centrals)
# print(fc.P_DSi(0.2))
# print(fc.dP_DSi(0.2))
# print(fc.mdf(0.2))

# fc.calc(0.2)

print(fc.calc(0.2).P_DSi)
print(fc.calc(0.2).deltaP)



