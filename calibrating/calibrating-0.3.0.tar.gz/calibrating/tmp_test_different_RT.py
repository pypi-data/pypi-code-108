#!/usr/bin/env python3

import boxx
from calibrating import *
from calibrating.stereo import Stereo

if __name__ == "__main__":
    from boxx import *

    checkboard = 0
    checkboard = 1
    if checkboard:
        caml, camr, camd = Cam.get_test_cams()
    else:
        root = "/home/dl/ai_asrs/big_file_for_ai_asrs/jinyu/2108.aruco标定2/5scan"
        feature_lib = ArucoFeatureLib()
        caml = Cam(
            glob(os.path.join(root, "*", "0_color.jpg")),
            feature_lib,
            name="caml",
            enable_cache=True,
        )
        camr = Cam(
            glob(os.path.join(root, "*", "0_stereo.jpg")),
            feature_lib,
            name="camr",
            enable_cache=True,
        )
        camd = Cam(
            glob(os.path.join(root, "*", "mk_color.png")),
            feature_lib,
            name="camd",
            enable_cache=True,
        )

    print(Cam.load(camd.dump()))

    stereo = Stereo(caml, camr)

    T_camd_in_caml = caml.get_T_cam2_in_self(camd)

    stereo2 = Stereo()
    T = caml.get_T_cam2_in_self(camr)
    T = camr.get_T_cam2_in_self(caml)
    stereo2.init_by_K_Rt(caml.K, caml.D, caml.K, caml.D, caml.xy, T[:3, :3], T[:3, 3])
    # init_by_K_Rt(self, K1, D1, K2, D2, xy, R, T):
    Cam.vis_stereo(caml, camr, stereo2)
    # Cam.vis_stereo(caml, camr, stereo)

if 0:
    key = caml.valid_keys_intersection(camd)[0]
    imgl = imread(caml[key]["path"])
    color_path_d = camd[key]["path"]
    depthd = imread(color_path_d.replace("color.jpg", "depth.png"))
    depthd = np.float32(depthd / 1000)

    depthl = caml.project_cam2_depth(camd, depthd, T_camd_in_caml)

    caml.vis_project_align(imgl, depthl, undistort=False)
