import replifactory




#%%
# dev = replifactory.BaseDevice(None, directory="NewExperiment")
# dev.calibrate()
dev = replifactory.BaseDevice(directory="NewExperiment3/")
dev.connect()
dev.valves.open(1)
dev.valves.close(1)
#%%
c = replifactory.MorbidostatCulture("NewExperiment3/", 1)
c.connect_device(dev)
c.dead_volume = 15
c.default_dilution_volume = 10
# dev.od_sensors[1].measure_od()
# dev.queue_od(2)
dev.valves.open(1)
dev.valves.close(1)
#%%
c.make_morbidostat_dilution()
#%%
# dev.od_sensors[2].calibration_curve_plot()
#
# #%%
# dev.od_sensors[2].add_calibration_point(mv=22, od=0.5)

#%% RUN EXPERIMENT

# exp = replifactory.Experiment("NewExperiment/")
# exp.device.valves.open_all()
# c = exp.cultures[3]
#
# c.measure_od  ()
#
# c.dilute(1)
# print(5)