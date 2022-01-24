'''
Created on 19. 3. 2014

@author: Vancikv

An example of a parameter study script - an alternative
to the tree view interface in creating a pstudy.
'''

from bmcs_beam.mxn import \
    CrossSection, MxNDiagram

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

ge = MCSGeoRect(height=0.06, width=0.14)
mcs = MatrixCrossSection(geo=ge, n_cj=20,
                         material='default_mixture',
                         material_law='constant')
uni_layers = RLCTexUniform(n_layers=12,
                           material='default_fabric',
                           material_law='fbm')
'''Geometry, matrix and reinforcement
'''

uni_layers.material_law_.sig_tex_u = 1200.13
'''
N = 103 kN
sig_tex_u = N / A_tex_tot = 103000 / (12 * 16 * 0.447) = 1200.13 N/mm2
'''

cs = CrossSection(matrix_cs=mcs, reinf=[uni_layers])
'''Cross section object
'''

mxn = MxNDiagram(cs=cs, n_eps=20)
'''MxN diagram object
'''

fig = Figure(figsize=(10, 7), dpi=80, facecolor='white')
canvas = FigureCanvasAgg(fig)
ax = fig.add_subplot(1, 1, 1)
'''Create something to plot into
'''

mxn.plot_custom(ax, color='black', linestyle='-',
                linewidth=2.0, label='fbm')

uni_layers.material_law = 'bilinear'
mxn.plot_custom(ax, color='black', linestyle='--',
                linewidth=2.0, label='bilinear')

uni_layers.material_law = 'linear'
mxn.plot_custom(ax, color='black', linestyle='-.',
                linewidth=2.0, label='linear')

uni_layers.material_law = 'cubic'
mxn.plot_custom(ax, color='black', linestyle=':',
                linewidth=2.0, label='cubic')
'''Parameter study - Plot the mxn diagram for different
reinforcement laws. Equivalently when using the tree view,
the plot_custom function is used by the PStudyElement
object which contains the plotting specs for its MxNDiagram.
'''

ax.legend()
ax.set_xlabel('M[kNm]')
ax.set_ylabel('N[kN]')

canvas.print_figure(get_outfile(folder_name='.mxn',
                                file_name='ex11.png'))
