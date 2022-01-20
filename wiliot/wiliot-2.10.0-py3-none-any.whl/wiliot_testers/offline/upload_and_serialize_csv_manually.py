import os
from glob import glob
import PySimpleGUI as sg
import pandas as pd
from wiliot.wiliot_testers.tester_utils import *


def get_files_path():
    """
    opens GUI for selecting a file and returns it
    """
    # Define the window's contents
    layout = [[sg.Text('choose run_data file that you want to upload:'), sg.Input(),
               sg.FileBrowse(key="run_data_file")],
              [sg.Text('choose tags_data file that you want to upload:'), sg.Input(),
               sg.FileBrowse(key="tags_data_file")],
              [sg.Text('would you like to serialize those tags?'),
               sg.InputCombo(('Yes', 'No'), default_value="Yes", key='serialize')],
              [sg.Text('would you like to upload those files?'),
               sg.InputCombo(('Yes', 'No'), default_value="Yes", key='upload')],
              [sg.Button('Select')]]

    # Create the window
    window = sg.Window('upload and serialize', layout)

    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == 'Select' and (values['run_data_file'] != '' or values['tags_data_file'] != ''):
        window.close()
        return values
    else:
        window.close()
        return None


def serialize_data_from_file():
    values = get_files_path()
    if values is None:
        print('user exited the program')
        return False
    tags_df = {}
    if values['run_data_file'] != '' and not values['run_data_file'].endswith('.csv'):
        print('run_data file format is not csv, please insert a csv file')
        return False
    if values['tags_data_file'] != '' and not values['tags_data_file'].endswith('.csv'):
        print('tags_data file format is not csv, please insert a csv file')
        return False

    batch_name, run_data_csv_name, tags_data_csv_name = None, None, None

    if values['run_data_file'] != '':
        batch_name = values['run_data_file'][:(len(values['run_data_file']) -
                                               len(values['run_data_file'].split("/")[-1]))]
        run_data_csv_name = values['run_data_file'].split('/')[-1]
    if values['tags_data_file'] != '':
        batch_name = values['tags_data_file'][:(len(values['tags_data_file']) -
                                                len(values['tags_data_file'].split("/")[-1]))]
        tags_data_csv_name = values['tags_data_file'].split('/')[-1]
    if batch_name is None:
        print('no files were selected, will exit the program')
        return False
    if values['upload'] == 'Yes':
        upload_to_cloud_api(batch_name=batch_name, tester_type='offline', run_data_csv_name=run_data_csv_name,
                            tags_data_csv_name=tags_data_csv_name, to_logging=False, env='prod',
                            is_batch_name_inside_logs_folder=False)

    try:
        tags_df = pd.read_csv(values['tags_data_file'])

    except Exception:
        print('unable to get data from csv')
        return False

    # serialization part
    if values['serialize'] == 'Yes':
        # make it to list
        adv_address = []
        packet = []
        serialization_threads_working = []
        next_batch_to_serialization = {'response': '', 'upload_data': []}
        get_new_token = True
        try_serialize_again = threading.Event()

        for tag in range(len(tags_df['advAddress'])):
            if tags_df['status'][tag] == 'Failed':
                continue
            external_id_tmp = tags_df['externalId'][tag]
            packet_tmp = tags_df['rawData'][tag].split('"')[5]
            adv_address.append(external_id_tmp)
            packet.append(packet_tmp)

            if len(next_batch_to_serialization['upload_data']) == 0:
                next_batch_to_serialization = {'response': '',
                                               'upload_data': [{"payload": packet_tmp,
                                                                "tagId": external_id_tmp}],
                                               'writing_lock': threading.Lock()}
            else:
                next_batch_to_serialization['upload_data'].append({"payload": packet_tmp,
                                                                   "tagId": external_id_tmp})
            # upload after 10 tags
            if tag % 10 == 0:
                serialization_threads_working.append(
                    SerializationAPI(batch_dictionary=next_batch_to_serialization, to_logging=True,
                                     get_new_token=get_new_token, try_serialize_again=try_serialize_again))
                serialization_threads_working[-1].start()

                next_batch_to_serialization = {'response': '', 'upload_data': []}
                get_new_token = False  # will only need new token for the first

            # print('advAddress = ' + str(adv_address))
            # print('packet = ' + str(packet))
        # serialize the reminder

        if not len(next_batch_to_serialization['upload_data']) == 0:
            serialization_threads_working.append(
                SerializationAPI(batch_dictionary=next_batch_to_serialization, to_logging=True,
                                 get_new_token=get_new_token, try_serialize_again=try_serialize_again))
            serialization_threads_working[-1].start()

        check_serialization_response(serialization_threads_working)

        # check_serialization_exception_queues(serialization_threads_working)
        close_all_serialization_processes_when_they_done(serialization_threads_working,
                                                         try_serialize_again=try_serialize_again)
        print("\n\nupload_and_serialize_csv_manually is done\n")


if __name__ == '__main__':
    serialize_data_from_file()
