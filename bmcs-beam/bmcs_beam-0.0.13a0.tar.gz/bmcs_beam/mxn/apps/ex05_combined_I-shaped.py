'''
Created on 6. 2. 2014

@author: Vancikv

Example of cross section assembly - I-shaped concrete
cross section with combined reinforcement of textile
layers and steel bars
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoI

from bmcs_beam.mxn.reinf_layout import \
    RLCTexLayer, RLCBar

from matplotlib.figure import \
    Figure

from matplotlib.backends.backend_agg import \
    FigureCanvasAgg

from bmcs_beam.mxn.utils import \
    get_outfile

import numpy as np

ge = MCSGeoI(height=0.4, height_up=0.05, width_up=0.25,
             height_lo=0.05, width_lo=0.35, width_st=0.05)
mcs = MatrixCrossSection(geo=ge,
                         n_cj=20,
                         material='default_mixture',
                         material_law='constant')
'''Cross section geometry + matrix
'''

bar1 = RLCBar(x=0.025, z=0.025, material='bar_d10',
              material_law='steel')
bar2 = RLCBar(x=0.125, z=0.025, material='bar_d10',
              material_law='steel')
bar3 = RLCBar(x=0.225, z=0.025, material='bar_d10',
              material_law='steel')
bar4 = RLCBar(x=0.325, z=0.025, material='bar_d10',
              material_law='steel')
'''Four steel reinforcement bars in lower flange
'''

tl1 = RLCTexLayer(z_coord=0.39, material='default_fabric',
                  material_law='fbm')
tl2 = RLCTexLayer(z_coord=0.01, material='default_fabric',
                  material_law='fbm')
'''Two layers of textile reinforcement
'''

cs = CrossSection(reinf=[tl1, tl2, bar1, bar2, bar3, bar4],
                         matrix_cs=mcs,
                         eps_lo=0.002,
                         eps_up=-0.0033,
                         )

print('normal force', cs.N)
print('moment', cs.M)

fig = Figure(figsize=(10, 7), dpi=80, facecolor='white')
canvas = FigureCanvasAgg(fig)
ax = fig.add_subplot(1, 1, 1)
cs.plot_geometry(ax)

canvas.print_figure(get_outfile(folder_name='.mxn',
                                file_name='ex05.png'))
