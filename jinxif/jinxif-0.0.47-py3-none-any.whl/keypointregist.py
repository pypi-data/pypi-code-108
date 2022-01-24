#####
# code adapted from chandler gatenbee and brian white
# https://github.com/IAWG-CSBC-PSON/registration-challenge
#
# for future development, guillaume mentioned this library listing here: http://pyimreg.github.io
#
# special thanks to: chandler gatenbee, brian white, guillaume thibault, jenny eng.
# input from all was needed that I totally got it running! bue
#####

# library
import copy
import cv2
from matplotlib import pyplot as plt
import numpy as np
import os
from skimage import exposure, transform, util

# development
#import importlib
#importlib.reload()


# function
def _keypoint_distance(target_pts, moving_pts, img_h, img_w):
    '''
    :calculate mean moving to target keypoint distance.
    :return:
    '''
    dst = np.sqrt(np.sum((moving_pts - target_pts)**2, axis=1)) / np.sqrt(img_h**2 + img_w**2)
    return(np.mean(dst))


def _match_keypoints(ai_img_target, ai_img_moving, feature_detector):
    '''
    :param ai_img_target: image to which the moving image will be aligned
    :param ai_img_moving: image that is to be warped to align with target image
    :param feature_detector: a feature detector from opencv
    :return:
    '''

    # get keypoints and descriptors
    kp1, desc1 = feature_detector.detectAndCompute(image=ai_img_moving, mask=None) # cv2
    kp2, desc2 = feature_detector.detectAndCompute(image=ai_img_target, mask=None) # cv2

    # get matches
    matcher = cv2.BFMatcher(normType=cv2.NORM_L2, crossCheck=True)  # cv2
    matches = matcher.match(queryDescriptors=desc1, trainDescriptors=desc2)  # cv2
    # list of integer indexes
    src_match_idx = [m.queryIdx for m in matches]
    dst_match_idx = [m.trainIdx for m in matches]
    # np array of float32
    src_points = np.float32([kp1[i].pt for i in src_match_idx])
    dst_points = np.float32([kp2[i].pt for i in dst_match_idx])

    # find perspective transformation between two planes
    H, mask = cv2.findHomography(srcPoints=src_points, dstPoints=dst_points, method=cv2.RANSAC, ransacReprojThreshold=10)

    # filter for ok matches
    good = [matches[i] for i in range(len(mask)) if mask[i] == [1]]
    # list of integer indexes
    filtered_src_match_idx = [m.queryIdx for m in good]
    filtered_dst_match_idx = [m.trainIdx for m in good]
    # np array of float32
    filtered_src_points = np.float32([kp1[i].pt for i in filtered_src_match_idx])
    filtered_dst_points = np.float32([kp2[i].pt for i in filtered_dst_match_idx])

    # output
    return(filtered_src_points, filtered_dst_points)


def apply_transform(ai_img_target, ai_img_moving, target_pts, moving_pts, transformer, output_shape_rc=None):
    '''
    :param transformer: transformer object from skimage. See https://scikit-image.org/docs/dev/api/skimage.transform.html for different transformations
    :param output_shape_rc: shape of warped image (row, col). If None, uses shape of target image
    :return:
    '''
    # get shape for one channel image
    if output_shape_rc is None:
        output_shape_rc = ai_img_target.shape[:2]

    # case of transformer
    transformer = copy.deepcopy(transformer)
    if str(transformer.__class__) == "<class 'skimage.transform._geometric.SimilarityTransform'>":
        b_ok = transformer.estimate(moving_pts, target_pts)
        print(f'transformation success: {b_ok}')
        ai_img_warped = transform.warp(ai_img_moving, inverse_map=transformer, output_shape=output_shape_rc, preserve_range=False)  # or transformer.inverse
        warped_pts = transformer(moving_pts)

    elif str(transformer.__class__) == "<class 'skimage.transform._geometric.PolynomialTransform'>":
        b_ok = transformer.estimate(target_pts, moving_pts)
        print(f'transformation success: {b_ok}')
        ai_img_warped = transform.warp(ai_img_moving, transformer, output_shape=output_shape_rc, preserve_range=False)
        # re-stimate to warp points
        transformer.estimate(moving_pts, target_pts)
        warped_pts = transformer(moving_pts)

    else:
        sys.exit('Error @ keypointregist.apply_transform : handling for this transformer type is not yet implemented {transformer.__class__}.\nso far, the implementation handles skimage transformer SimilarityTransform and PolynomialTransform.')

    # dtype warped float64 image
    if not (ai_img_warped.dtype.type is np.float64):
        sys.exit('Error @ keypointregist.apply_transform : ai_img_warped dtype is not np.float64 {ai_img_warped.dtype.type}.\nthis should not happen. fix source code!')
    if (ai_img_target.dtype.type is np.uint8):
        ai_img_warped = util.img_as_ubyte(ai_img_warped)
    else:
        ai_img_warped = util.img_as_uint(ai_img_warped)

    # output
    return(ai_img_warped, warped_pts, transformer)


def register(ai_img_target, ai_img_moving, s_pathfile_qcplot='QC/RegistrationPlots/qc_registration_rigid_align.png'):
    '''
    version: 2021-12-00

    input:
        ai_img_target: as numpy array loaded 16[bit] or 8[bit] image.
            to ensure the image`s dtype load like this:
            util.img_as_uint(util.img_as_float(io.imread(s_target_file)))  # 16[bit]
            util.img_as_ubyte(util.img_as_float(io.imread(s_target_file)))  # 8[bit]

        ai_img_moving: as numpy array loaded 16[bit] or 8[bit] image.
            to ensure the image`s dtype load like this:
            util.img_as_uint(util.img_as_float(io.imread(s_moving_file)))  # 16[bit]
            util.img_as_ubyte(util.img_as_float(io.imread(s_moving_file)))  # 8[bit]

        s_pathfile_qcplot: path and filename for registration qc plot. can be None.
            if None no qc plot will be generated.

    output:
        moving_pts: moving points object
        target_pts: target points object
        warped_pts: warped points object
        transformer: transformer object
        registration qc plot, if s_path_qcplot not is None.

    description:
        main function to do keypoint registration.
    '''
    # normalize images: clip by two sigma and scale over the whole uint range.
    i_min_clip = int(np.percentile(ai_img_target, 2.5))
    i_max_clip = int(np.percentile(ai_img_target, 97.5))
    ai_img_target = np.clip(ai_img_target, a_min=i_min_clip, a_max=i_max_clip)
    ai_img_target = exposure.rescale_intensity(ai_img_target, in_range='image') # 16 or 8[bit] normalized

    i_min_clip = int(np.percentile(ai_img_moving, 2.5))
    i_max_clip = int(np.percentile(ai_img_moving, 97.5))
    ai_img_moving = np.clip(ai_img_moving, a_min=i_min_clip, a_max=i_max_clip)
    ai_img_moving = exposure.rescale_intensity(ai_img_moving, in_range='image') # 16 or 8[bit] normalized

    # registration
    # bue 20201112 jenny said, alternatively kaze can be used, though akaze is a superior feature detection algorithm.
    #fd = cv2.KAZE_create(extended=True)
    fd = cv2.AKAZE_create()
    moving_pts, target_pts = _match_keypoints(
        ai_img_target=ai_img_target,
        ai_img_moving=ai_img_moving,
        feature_detector=fd
    )

    # generate transformer
    transformer = transform.SimilarityTransform()

    # apply transformtion
    ai_img_warped, warped_pts, transformer = apply_transform(
        ai_img_target=ai_img_target,
        ai_img_moving=ai_img_moving,
        target_pts=moving_pts,
        moving_pts=moving_pts,
        transformer=transformer
    )

    # qc plot
    if not (s_pathfile_qcplot is None):
        # get offset
        r_unaligned_offset = _keypoint_distance(target_pts=target_pts, moving_pts=moving_pts, img_h=ai_img_moving.shape[0], img_w=ai_img_moving.shape[1])
        r_aligned_offset = _keypoint_distance(target_pts=target_pts, moving_pts=warped_pts, img_h=ai_img_warped.shape[0], img_w=ai_img_warped.shape[1])

        # generate qc plot
        fig, ax = plt.subplots(2,2, figsize=(10,10))
        ax[0][0].imshow(ai_img_target)
        ax[0][0].imshow(ai_img_moving, alpha=0.5)
        ax[1][0].scatter(target_pts[:,0], -target_pts[:,1], s=1)
        ax[1][0].scatter(moving_pts[:,0], -moving_pts[:,1], s=1)
        ax[1][0].set_aspect('equal')
        ax[0][0].set_title(f"Target Moving\nunaligned offset: {r_unaligned_offset}")

        ax[0][1].imshow(ai_img_target)
        ax[0][1].imshow(ai_img_warped, alpha=0.5)
        ax[1][1].scatter(target_pts[:,0], -target_pts[:,1], s=1)
        ax[1][1].scatter(warped_pts[:,0], -warped_pts[:,1], s=1)
        ax[1][1].set_aspect('equal')
        ax[0][1].set_title(f"Target Warped\naligned offset: {r_aligned_offset}")

        # save qc plot
        s_erase = s_pathfile_qcplot.split('/')[-1]
        s_path_qcplot = s_pathfile_qcplot.replace(s_erase,'')
        os.makedirs(s_path_qcplot, exist_ok=True)
        plt.savefig(s_pathfile_qcplot, format="png", facecolor='white')

    # output results
    return(target_pts, moving_pts, warped_pts, transformer)
