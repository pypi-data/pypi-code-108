import logging
import sys
import os

import hipecta
import h5py
import tables
import numpy as np
from ctapipe.instrument import CameraGeometry
from ctapipe.utils.linalg import rotation_matrix_2d
from ctapipe.visualization import CameraDisplay
from astropy import units as u
import matplotlib.pyplot as plt

import gammalearn.utils as utils


if __name__ == '__main__':

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    lapp_file = '/home/mikael/projets_CTA/Prod3b/diffuse/LaPalma_gamma_diffuse_20deg_0deg_prod3b_training_0021.hdf5'
    ucm_file = '/home/mikael/projets_CTA/CMU/diffuse/gamma_20deg_180deg_srun1-19496___cta-prod3_desert-2150m-Paranal-HB9_cone10.h5'

    with h5py.File('camera_parameters.h5', 'w') as camera_parameters:
        with h5py.File(lapp_file, 'r') as lapp:
            for cam in lapp['Cameras']:
                camera_parameters.create_group(cam)
                camera_parameters[cam].create_dataset('pixelsPosition', data=lapp['Cameras'][cam]['pixelsPosition'])
                camera_parameters[cam].create_dataset('injTable', data=lapp['Cameras'][cam]['injTable'])
                camera_parameters[cam].attrs['nbCol'] = lapp['Cameras'][cam].attrs['nbCol']
                camera_parameters[cam].attrs['nbRow'] = lapp['Cameras'][cam].attrs['nbRow']

        with tables.File(ucm_file, 'r') as ucm:
            num_pixels = ucm.root['Telescope_Info'][:]['num_pixels']
            tel_type = ucm.root['Telescope_Info'][:]['tel_type']
            pixel_pos = ucm.root['Telescope_Info'][:]['pixel_pos']
            for i, tel in enumerate(tel_type):
                tel = tel.decode('ascii')
                if tel == 'LST':
                    rot_angle = CameraGeometry.from_name('LSTCam').pix_rotation
                elif tel == 'MSTN':
                    rot_angle = CameraGeometry.from_name('NectarCam').pix_rotation
                elif tel == 'MSTF':
                    rot_angle = CameraGeometry.from_name('FlashCam').pix_rotation
                elif tel == 'MSTS':
                    rot_angle = CameraGeometry.from_name('SCTCam').pix_rotation
                elif tel == 'SST1':
                    rot_angle = CameraGeometry.from_name('DigiCam').pix_rotation
                elif tel == 'SSTA':
                    rot_angle = CameraGeometry.from_name('ASTRICam').pix_rotation
                elif tel == 'SSTC':
                    rot_angle = CameraGeometry.from_name('CHEC').pix_rotation
                else:
                    logger.error('Unknown camera type')
                    exit(1)
                pix_pos = pixel_pos[i, :, 0:num_pixels[i]].transpose()
                pix_pos = (pix_pos @ rotation_matrix_2d(rot_angle)).astype(np.float32)
                injTable, nbRow, nbCol = hipecta.camera.getAutoInjunctionTable(pix_pos)

                camera_parameters.create_group(tel)
                camera_parameters[tel].create_dataset('pixelsPosition', data=pix_pos)
                camera_parameters[tel].create_dataset('injTable', data=injTable.astype(np.float32))
                camera_parameters[tel].attrs['nbCol'] = nbCol
                camera_parameters[tel].attrs['nbRow'] = nbRow

    with h5py.File('camera_parameters.h5', 'r') as camera_parameters:
        lst_inj = camera_parameters['LST/injTable'][()]
        lst_pixpos = camera_parameters['LST/pixelsPosition'][()]
        lst_row = camera_parameters['LST'].attrs['nbRow']
        lst_col = camera_parameters['LST'].attrs['nbCol']
    with tables.File(ucm_file, 'r') as ucm:
        img_vec = ucm.root['LST'][1]['image_charge']
        ucm_pix_pos = ucm.root['Telescope_Info'][ucm.root['Telescope_Info'][:]['tel_type'] == 'LST']['pixel_pos']
        ucm_pix_pos = ucm_pix_pos.T[0:1855]

    fid, ((ax1), (ax2), (ax3), (ax4)) = plt.subplots(1, 4)
    # Plot original hexagonal image from pixel pos
    geom = CameraGeometry.from_name('LSTCam')
    disp = CameraDisplay(geom, ax=ax1, title='Original geom from name')
    disp.image = img_vec

    # Plot original hexagonal image from pixel pos
    geom = CameraGeometry.guess(list(map(lambda x: x[0], ucm_pix_pos)) * u.m,
                                list(map(lambda x: x[1], ucm_pix_pos)) * u.m,
                                28 * u.m,
                                apply_derotation=False)
    disp2 = CameraDisplay(geom, ax=ax2, title='Original pixel pos')
    disp2.image = img_vec

    # Plot derotated hexagonal image
    geom = CameraGeometry.guess(list(map(lambda x: x[0], lst_pixpos)) * u.m,
                                list(map(lambda x: x[1], lst_pixpos)) * u.m,
                                28 * u.m,
                                apply_derotation=False)
    disp3 = CameraDisplay(geom, ax=ax3, title='Derotated')
    disp3.image = img_vec

    # Plot squared image
    index_matrix = utils.create_index_matrix(lst_row, lst_col, lst_inj).numpy().squeeze().squeeze()
    print(index_matrix.shape)
    hex_mat = np.zeros(index_matrix.shape)
    for i in range(index_matrix.shape[0]):
        for j in range(index_matrix.shape[1]):
            if not int(index_matrix[i, j]) == -1:
                hex_mat[i, j] = img_vec[int(index_matrix[i, j])]
    ax4.imshow(hex_mat)

    plt.show()
