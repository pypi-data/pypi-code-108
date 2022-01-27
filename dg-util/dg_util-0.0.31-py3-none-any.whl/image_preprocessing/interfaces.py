from .basic_crop import FaceCropper


file_id='1h7xPSL8zkcCIi1ewp59PjKq8Mvtx8VQR'
# download to dg_util/.cache/image_preprocessing/shape_predictor_68_face_landmarks.dat
landmarks_save_path='.cache/shape_predictor_68_face_landmarks.dat'

def download_file_from_google_drive(id, destination):
    import requests
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def download_landmarks(landmark_predictor_path):
    try: 
        download_file_from_google_drive(file_id, landmark_predictor_path)
        print('Landmark downloaded')
    except Exception as e:
        print('[Cannot download landmark data]',e)

def prepare_landmarks(landmark_predictor_path):
    import os
    from pathlib import Path 
    if not os.path.exists(landmark_predictor_path):
        p=Path(landmark_predictor_path)
        if not os.path.exists(p.parent):
            os.makedirs(p.parent)
        download_landmarks(landmark_predictor_path)
    else:
        return False   

def crop_image(img, resolution, if_mirror_padding=False, check_resolution=False, upper_limit_of_black_region_ratio=1.):
    # img is pil or path
    prepare_landmarks(landmarks_save_path)
    face_cropper = FaceCropper(landmarks_save_path, resolution, if_mirror_padding, check_resolution, upper_limit_of_black_region_ratio)
    cropped_img = face_cropper.crop_face_from_image(img)
    return cropped_img

def crop_image_from_path(img_path, resolution, if_mirror_padding=False, check_resolution=False, upper_limit_of_black_region_ratio=1.):
    prepare_landmarks(landmarks_save_path)
    face_cropper = FaceCropper(landmarks_save_path, resolution, if_mirror_padding, check_resolution, upper_limit_of_black_region_ratio)
    cropped_img = face_cropper.crop_face_from_path(img_path)
    return cropped_img