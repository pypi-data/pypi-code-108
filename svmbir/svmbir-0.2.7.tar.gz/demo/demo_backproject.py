import numpy as np
from demo_utils import plot_image
import svmbir

"""
Backproject demo
"""

verbose_level = 1

# Generate 3D phantom
num_rows = 512
num_cols = 512
num_slices = 4
phantom = np.zeros((num_slices,num_rows,num_cols))
phantom[:,100:180,100:140]=1
phantom[:,180:220,300:350]=1

# Generate the array of view angles
num_channels= 512
num_views = 144
tilt_angle = np.pi/2
angles = np.linspace(-tilt_angle, tilt_angle, num_views, endpoint=False)

# Generate sinogram by projecting phantom
sino = svmbir.project(phantom, angles, num_channels, verbose=verbose_level)

# Compute MBIR reconstruction
recon = svmbir.recon(sino, angles, sharpness=0.0, verbose=verbose_level)

# Compute simple backprojection
recon_adj = svmbir.backproject(sino, angles, num_rows=num_rows, num_cols=num_cols, verbose=verbose_level)
recon_adj2 = svmbir.backproject(sino, angles, num_rows=num_rows, num_cols=num_cols, roi_radius=num_rows, verbose=verbose_level)

slnum=0
plot_image(phantom[slnum], title='Original phantom')
plot_image(sino[:,slnum,:].transpose(), title='Sinogram')
plot_image(recon[slnum], title='MBIR result')
plot_image(recon_adj[slnum], title='Simple backprojection')
plot_image(recon_adj2[slnum], title='Simple backprojection, extended radius')

input("press Enter")

