'''
Created on 1. 2. 2014

@author: Vancikv

Example of cross section assembly - Rectangular concrete
cross section with textile reinforcement input as
single layers. xxx
'''

from bmcs_beam.mxn import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCTexLayer

from matplotlib.figure import \
    Figure

from matplotlib.backends.backend_agg import \
    FigureCanvasAgg

from bmcs_beam.mxn.utils import \
    get_outfile

tl1 = RLCTexLayer(z_coord=0.1, material='default_fabric', material_law='fbm')
tl2 = RLCTexLayer(z_coord=0.05, material='default_fabric', material_law='fbm')
'''Two layers of textile reinforcement
'''

ge = MCSGeoRect(height=0.5, width=0.3)
'''Cross section geometry
'''

mcs = MatrixCrossSection(geo=ge,
                         n_cj=20,
                         material='default_mixture',
                         material_law='constant')
'''Matrix cross section
'''

cs = CrossSection(reinf=[tl1, tl2],
                  matrix_cs=mcs,
                  eps_lo=0.008,
                  eps_up=-0.0033,
                  )

print('normal force', cs.N)
print('moment', cs.M)

fig = Figure(figsize=(10, 7), dpi=80, facecolor='white')
canvas = FigureCanvasAgg(fig)
ax = fig.add_subplot(1, 1, 1)
cs.plot_geometry(ax)

canvas.print_figure(get_outfile(folder_name='.mxn',
                                file_name='ex02.png'))
