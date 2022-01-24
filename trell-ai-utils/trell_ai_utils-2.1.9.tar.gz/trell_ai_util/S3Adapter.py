import os
import boto3
import pickle
import subprocess
from io import BytesIO

def read_from_s3_bucket(bucket='data-science-datas', sub_bucket='tests/', file_name='test.pkl'):
    key = sub_bucket + file_name

    try:
        s3 = boto3.resource('s3', aws_access_key_id=os.environ['ACCESS_KEY'],
                                      aws_secret_access_key=os.environ['SECRET_KEY'])   
    except:
        s3 = boto3.resource('s3')

    print("Reading data from : " + bucket + "/" + key)
    with BytesIO() as data:
        s3.Bucket(bucket).download_fileobj(key, data)
        data.seek(0)
        old_data = pickle.load(data)
    return old_data


def write_to_s3_bucket(python_data_object=None, bucket='data-science-datas', sub_bucket='tests/', file_name='test.pkl'):
    key = sub_bucket + file_name
    pickle_byte_obj = pickle.dumps(python_data_object)
    print("Writing data to : " + bucket + "/" + key)
    try:
        s3 = boto3.resource('s3', aws_access_key_id=os.environ['ACCESS_KEY'],
                                      aws_secret_access_key=os.environ['SECRET_KEY'])   
    except:
        s3 = boto3.resource('s3')
    
    s3.Object(bucket, key).put(Body=pickle_byte_obj)


def upload_data_from_local_to_s3(model_file_name, bucket='', sub_bucket=''):
    try:
        final_bucket_folder_path =  "s3://"+bucket+"/"+sub_bucket
        final_bucket_folder_path = "s3://data-science-datas/models/"
        print(final_bucket_folder_path)
        upload_command = "aws s3 cp  " + model_file_name+" "+ final_bucket_folder_path
        print(upload_command)
        upload_command_array = upload_command.split()
        p = subprocess.Popen(upload_command_array, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            retcode = p.poll()
            line = p.stdout.readline()
            print(line)
            print(retcode)
            if retcode is not None:
                import os
                os.remove(model_file_name)
                print("Removing file name: ", model_file_name)
                break
    except Exception as e:
        print(e)
