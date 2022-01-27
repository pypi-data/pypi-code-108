#!/usr/bin/env python3

from dlpoly import DLPoly
from ase.build import bulk
from ase.io import write
from dlpoly.field import Field
from dlpoly.new_control import NewControl as Control

a = bulk('Ar', 'fcc', a=4.0)
write("Ar-fcc.config",a*(8,8,8),format='dlp4')

ctl = Control()
ctl['title'] = 'Ar'
ctl['temperature'] = (300, 'K')
ctl['timestep'] = ( 0.001, 'ps')
ctl['ensemble'] = 'nve'
ctl['padding'] = (0.5, 'Ang')
ctl['vdw_method'] = 'direct'
ctl['cutoff'] = (7.0,'Ang')
ctl['stats_frequency'] = (100,'steps')
ctl['print_frequency'] = (100,'steps')
ctl['stack_size'] = (10,'steps')
ctl['time_run'] = (10000,'steps')
ctl['time_equilibration'] = (10000,'steps')
ctl['time_job'] = (10000,'s')
ctl['time_close'] = (10,'s')
ctl['data_dump_frequency'] = (5000,'steps')
ctl['io_file_config'] = 'Ar-fcc.config'

ctl.write("new.control")

dlp='/home/drFaustroll/lavello/build-dlpoly-alin/bin/DLPOLY.Z'
dlpoly = DLPoly()
dlpoly.control = ctl
dlpoly.load_config("Ar-fcc.config")
dlpoly.load_field("Ar.field")
dlpoly.workdir = "argon"

dlpoly.run(executable=dlp,numProcs = 2)


