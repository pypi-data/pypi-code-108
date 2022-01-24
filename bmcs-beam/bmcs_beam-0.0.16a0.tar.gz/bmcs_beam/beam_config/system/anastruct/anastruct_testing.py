from anastruct import SystemElements
import numpy as np
L = 1000
F = -2000

struct = SystemElements()
# struct.plotter = CustomPlotter(struct, mesh=50)

struct.add_multiple_elements([[0, 0], [L, 0]], 2)

struct.add_support_hinged(1)
struct.add_support_roll(3)

struct.point_load(2, Fy=F)

struct.solve()

struct.show_structure()
# struct.show_displacement()
# axes = struct.plotter.plot_structure(figsize=(12, 8),
#         verbosity=0, show=False).get_axes()
# struct.show_shear_force()
struct.show_bending_moment()
# struct.show_reaction_force()


# shear_xy = struct.show_shear_force(values_only=True, factor=1)
#
# # Getting real internal forces values for 1 element
# normal_force = struct.get_element_results(element_id=1, verbose=True)['N']
# shear = struct.get_element_results(element_id=1, verbose=True)['Q']
moment = struct.get_element_results(element_id=1, verbose=True)['M']

moment = struct.get_element_result_range(unit = "moment")
# print(moment)

print(np.array([dict['M'] for dict in struct.get_element_results(verbose=True)]).flatten())