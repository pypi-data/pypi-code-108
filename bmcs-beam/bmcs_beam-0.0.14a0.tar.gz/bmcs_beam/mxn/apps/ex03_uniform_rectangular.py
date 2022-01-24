'''
Created on 2. 2. 2014

@author: Vancikv

Example of cross section assembly - Rectangular concrete
 cross section with uniformly distributed textile layers
'''

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from bmcs_beam.mxn.reinf_layout import \
    RLCTexUniform

from matplotlib.figure import \
    Figure

from matplotlib.backends.backend_agg import \
    FigureCanvasAgg

from bmcs_beam.mxn.utils import \
    get_outfile

uni_layers = RLCTexUniform(n_layers=10,
                           material='default_fabric',
                           material_law='fbm')
'''Uniformly distributed textile layers
'''

ge = MCSGeoRect(height=0.4, width=0.3)
'''Cross section geometry
'''

mcs = MatrixCrossSection(geo=ge,
                         n_cj=20,
                         material='default_mixture',
                         material_law='constant')
'''Matrix cross section
'''

cs = CrossSection(reinf=[uni_layers],
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
                                file_name='ex03.png'))
