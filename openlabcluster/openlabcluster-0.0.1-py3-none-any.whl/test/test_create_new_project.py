from openlabcluster import create_new_project
import os
import shutil
import glob

def test_create_project():

    project_name = 'test'
    working_dir = '/Users/Moishe/projects/uw-lab/IC_GUI/projects'

    project_path = os.path.join(working_dir, project_name)
    for path in glob.glob(project_path + '*'):
        print(path)
        shutil.rmtree(path)

    data_files = [
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-h5/m1s1DLC_resnet_50_openfieldAug20shuffle1_15.h5',
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-h5/m1s2DLC_resnet_50_openfieldAug20shuffle1_15.h5',
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-h5/m2s1DLC_resnet_50_openfieldAug20shuffle1_15.h5',
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-h5/m3s1DLC_resnet_50_openfieldAug20shuffle1_15.h5',
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-h5/m3s2DLC_resnet_50_openfieldAug20shuffle1_15.h5',
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-h5/m4s1DLC_resnet_50_openfieldAug20shuffle1_15.h5',
    ]

    video_files = [
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-mp4/m1s1.mp4',
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-mp4/m1s2.mp4', 
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-mp4/m2s1.mp4',
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-mp4/m3s1.mp4', 
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-mp4/m3s2.mp4',
        '/Users/Moishe/Downloads/openfield-Pranav-2018-08-20/videos-mp4/m4s1.mp4',
    ]

    create_new_project(
        project_name,
        data_name=data_files,
        training_video_list=video_files,
        test_videodir=working_dir,
        working_directory=working_dir,
        copy_videos=True,
        use_gpu=False,
        feature_length=8
    )
    