"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import http.client
import serial.tools.list_ports
from wiliot.wiliot_testers.tester_utils import *
from wiliot.wiliot_testers.calibration_test.calibration_test import *


class ConfigDefaults(object):
    """
    contains the default values for the configuration json
    """

    def __init__(self):
        self.printer_defaults = {'TCP_IP': '192.168.7.61', 'TCP_PORT': '3003', 'TCP_BUFFER': '128',
                                 'printingFormat': 'SGTIN'}
        self.single_band_gw_defaults = {'energizingPattern': '18', 'timeProfile': '3,7', 'txPower': '3',
                                        'rssiThreshold': '90', 'plDelay': '150'}
        self.dual_band_gw_defaults = {'energizingPattern': '18', 'secondEnergizingPattern': '52', 'timeProfile': '5,10',
                                      'txPower': '3', 'rssiThreshold': '90', 'plDelay': '100'}

    def get_printer_defaults(self):
        return self.printer_defaults

    def get_single_band_gw_defaults(self):
        return self.single_band_gw_defaults

    def get_dual_band_gw_defaults(self):
        return self.dual_band_gw_defaults


class DefaultGUIValues:
    def __init__(self, gui_type):
        if gui_type == 'Main':
            self.default_gui_values = {'missingLabel': 'No',
                                       'maxMissingLabels': '6',
                                       'toPrint': 'No', 'printingFormat': 'SGTIN', 'batchName': 'test_reel',
                                       'tagGen': 'D2',
                                       'inlayType': 'Dual Band', 'inlay': '088', 'testTime': '10', 'maxTtfp': '5',
                                       'packetThreshold': '10',
                                       'desiredTags': '9999999', 'desiredPass': '9999999', 'surface': 'air',
                                       'converted': 'Yes', 'blackListAfter': '2',
                                       'comments': ''}
        elif gui_type == 'Test':
            self.default_gui_values = {'passJobName': 'SGTIN_QR', 'sgtin': 'test_test_test_test_X_',
                                       'stringBeforeCounter': 'test',
                                       'reelNumManually': 'test', 'firstPrintingValue': '0'}
        elif gui_type == 'SGTIN':
            self.default_gui_values = {'passJobName': 'SGTIN_QR', 'sgtin': '(01)00850027865010(21)',
                                       'stringBeforeCounter': '',
                                       'reelNumManually': '', 'firstPrintingValue': '0'}
        else:
            self.default_gui_values = {}


def open_session():
    """
    gets the user inputs from first GUI
    :return: dictionary of the values
    """
    # move to r2r : return dict - r2r
    folder_name = 'configs'
    file_name = 'gui_inputs_do_not_delete.json'
    gui_inputs_values = open_json(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                  default_values=DefaultGUIValues(gui_type='Main').default_gui_values)
    for key in DefaultGUIValues(gui_type='Main').default_gui_values.keys():
        if key not in gui_inputs_values.keys():
            gui_inputs_values[key] = DefaultGUIValues(gui_type='Main').default_gui_values[key]
    def_layout = [[SimGUI.Text('Max missing labels in a row:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['maxMissingLabels'], key='maxMissingLabels')],
                  [SimGUI.Text('To print?', size=(40, 1)),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=gui_inputs_values['toPrint'], key='toPrint')],
                  [SimGUI.Text('Reel_name:', size=(40, 1)), SimGUI.InputText(gui_inputs_values['batchName'],
                                                                             key='batchName')],
                  [SimGUI.Text('Tags Generation:', size=(40, 1)),
                   SimGUI.InputCombo(('C0', 'D1', 'D2'), default_value=gui_inputs_values['tagGen'], key='tagGen')],
                  [SimGUI.Text('Inlay type:', size=(40, 1)),
                   SimGUI.InputCombo(('Dual Band', 'Single Band'), default_value=gui_inputs_values['inlayType'],
                                     key='inlayType')],
                  [SimGUI.Text('Inlay serial number (3 digits):', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['inlay'], key='inlay')],
                  [SimGUI.Text('Test Time [sec]\n(reel2reel controller->delay between steps = 999):', size=(40, 2)),
                   SimGUI.InputText(gui_inputs_values['testTime'], key='testTime')],
                  [SimGUI.Text('Fail if no packet received until [sec]:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['maxTtfp'], key='maxTtfp')],
                  [SimGUI.Text('PacketThreshold:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['packetThreshold'], key='packetThreshold')],
                  [SimGUI.Text('Surface:', size=(40, 1)),
                   SimGUI.InputCombo(('air', 'cardboard', 'RPC', 'Er3', 'Er3.5', 'Er5', 'Er7', 'Er12'),
                                     default_value=gui_inputs_values['surface'], key='surface')],
                  [SimGUI.Text('Is converted?', size=(40, 1)),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=gui_inputs_values['converted'], key='converted')],
                  [SimGUI.Text('Comments:', size=(40, 1)), SimGUI.InputText(gui_inputs_values['comments'],
                                                                            key='comments')],
                  [SimGUI.Button('Advance'), SimGUI.Submit(button_color=('white', '#0e6251'))]]

    layout = def_layout
    window = SimGUI.Window('Offline Tester', layout)
    open_advance = False
    while True:
        event, values = window.read()
        if event == 'Submit':
            # make sure user input is legit
            if ' ' in values['batchName'] or '/' in values['batchName'] or '\\' in values['batchName']:
                print("Reel name could not contain spaces, '\\' or '/'\nplease fix it and press Submit")
                continue
            else:
                try:
                    float(values['maxTtfp'])
                    float(values['testTime'])
                except Exception:
                    print("the following values should be numbers (float): maxTtfp, testTime")
                    continue
                try:
                    int(values['maxMissingLabels'])
                    int(values['packetThreshold'])
                except Exception:
                    print("the following values should be numbers (integer): maxMissingLabels, packetThreshold")
                    continue
                yes_no = ['Yes', 'No']
                if values['toPrint'] not in yes_no or values['converted'] not in yes_no:
                    print("the following values should be 'Yes' or 'No': toPrint, converted")
                    continue
                break
        if event == 'Advance':
            open_advance = True
            break
        elif event is None:
            print('User exited the program')
            window.close()
            exit()

    window.close()
    for key in gui_inputs_values.keys():
        if key not in values.keys():
            values[key] = gui_inputs_values[key]
    # to defend against user errors
    values['tagGen'] = values['tagGen'].upper()
    with open(os.path.join(folder_name, file_name), 'w') as f:
        json.dump(values, f)
    if open_advance:
        values = advanced_open_session()
    return values


def advanced_open_session():
    """
    opens advanced (more options to the open_session window
    :return: dictionary of the values
    """
    # move to r2r : return dict - r2r
    folder_name = 'configs'
    file_name = 'gui_inputs_do_not_delete.json'
    gui_inputs_values = open_json(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                  default_values=DefaultGUIValues(gui_type='Main').default_gui_values)
    # add key if it is missing from json
    for key in DefaultGUIValues(gui_type='Main').default_gui_values.keys():
        if key not in gui_inputs_values.keys():
            gui_inputs_values[key] = DefaultGUIValues(gui_type='Main').default_gui_values[key]

    def_layout = [[SimGUI.Text('Max missing labels in a row:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['maxMissingLabels'], key='maxMissingLabels')],
                  [SimGUI.Text('To print?', size=(40, 1)),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=gui_inputs_values['toPrint'], key='toPrint')],
                  [SimGUI.Text('Reel_name:', size=(40, 1)), SimGUI.InputText(gui_inputs_values['batchName'],
                                                                             key='batchName')],
                  [SimGUI.Text('Tags Generation:', size=(40, 1)),
                   SimGUI.InputCombo(('C0', 'D1', 'D2'), default_value=gui_inputs_values['tagGen'], key='tagGen')],
                  [SimGUI.Text('Inlay type:', size=(40, 1)),
                   SimGUI.InputCombo(('Dual Band', 'Single Band'), default_value=gui_inputs_values['inlayType'],
                                     key='inlayType')],
                  [SimGUI.Text('Inlay serial number (3 digits):', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['inlay'], key='inlay')],
                  [SimGUI.Text('Test Time [sec]\n(reel2reel controller->delay between steps = 999):', size=(40, 2)),
                   SimGUI.InputText(gui_inputs_values['testTime'], key='testTime')],
                  [SimGUI.Text('Fail if no packet received until [sec]:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['maxTtfp'], key='maxTtfp')],
                  [SimGUI.Text('PacketThreshold:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['packetThreshold'], key='packetThreshold')],
                  [SimGUI.Text('Surface:', size=(40, 1)),
                   SimGUI.InputCombo(('air', 'cardboard', 'RPC', 'Er3', 'Er3.5', 'Er5', 'Er7', 'Er12'),
                                     default_value=gui_inputs_values['surface'], key='surface')],
                  [SimGUI.Text('Is converted?', size=(40, 1)),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=gui_inputs_values['converted'], key='converted')],
                  [SimGUI.Text('Comments:', size=(40, 1)), SimGUI.InputText(gui_inputs_values['comments'],
                                                                            key='comments')],
                  [SimGUI.Text('Allow multiple missing label in a row?', size=(40, 1)),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=gui_inputs_values['missingLabel'],
                                     key='missingLabel')],
                  [SimGUI.Text('Desired amount of tags\n(will stop the run after this amount of tags):', size=(40, 2)),
                   SimGUI.InputText(gui_inputs_values['desiredTags'], key='desiredTags')],
                  [SimGUI.Text('Desired amount of pass\n(will stop the run after this amount of passes):',
                               size=(40, 2)),
                   SimGUI.InputText(gui_inputs_values['desiredPass'], key='desiredPass')],
                  [SimGUI.Text('What is the printing job format?', size=(40, 1)),
                   SimGUI.InputCombo(('Test', 'SGTIN'), default_value='SGTIN',
                                     key='printingFormat')],
                  [SimGUI.Text('Locations tag appears on before it enters black list (min=2)',
                               size=(40, 2)),
                   SimGUI.InputText(gui_inputs_values['blackListAfter'], key='blackListAfter')],
                  [SimGUI.Button('Simple'), SimGUI.Button('Start calibration'),
                   SimGUI.Submit(button_color=('white', '#0e6251'))]]

    layout = def_layout
    window = SimGUI.Window('Offline Tester', layout)
    open_simple = False
    should_start_calibration = False

    while True:
        event, values = window.read()
        if event == 'Submit':
            # make sure user input is legit
            if ' ' in values['batchName'] or '/' in values['batchName'] or '\\' in values['batchName']:
                print("Reel name could not contain spaces, '\\' or '/'\nplease fix it and press Submit")
                continue
            else:
                try:
                    float(values['maxTtfp'])
                    float(values['testTime'])
                except Exception:
                    print("the following values should be numbers (float): maxTtfp, testTime")
                    continue
                try:
                    int(values['maxMissingLabels'])
                    int(values['packetThreshold'])
                    int(values['desiredTags'])
                    int(values['desiredPass'])
                    if int(values['blackListAfter']) < 2:
                        raise Exception('bad black list value')
                except Exception:
                    print("the following values should be numbers (integer): maxMissingLabels, packetThreshold,"
                          "desiredTags, desiredPass, blackListAfter (and should not be smaller than 2")
                    continue
                yes_no = ['Yes', 'No']
                if values['toPrint'] not in yes_no or values['converted'] not in yes_no:
                    print("the following values should be 'Yes' or 'No': toPrint, converted")
                    continue
                break
        elif event == 'Simple':
            open_simple = True
            break
        elif event == 'Start calibration':
            should_start_calibration = True
            break
        elif event is None:
            print('User exited the program')
            window.close()
            exit()

    window.close()
    # to defend against user errors
    values['tagGen'] = values['tagGen'].upper()
    with open(os.path.join(folder_name, file_name), 'w') as f:
        json.dump(values, f)
    if open_simple:
        values = open_session()
    if should_start_calibration:
        print('Will start calibration, When done program will end')
        print('---------------------------------------------------------------\n'
              'Please make sure the tags on and around the antenna are working\n'
              '---------------------------------------------------------------')
        start_calibration(inlay_type=values['inlayType'])
        exit()  # TODO - remove this line after logging fails due to calibration process fixed
    return values


def get_printed_value(string_before_the_counter: str, digits_in_counter: int, first_counter: str, printing_format: str):
    """
    builds the printed value
    :type string_before_the_counter: string
    :param string_before_the_counter: the sg1 Id of the tested reel
    :type digits_in_counter: int
    :param digits_in_counter: amount of digits in the tag counter field (usually 4)
    :type first_counter: string
    :param first_counter: counter of the run first tag
    :type printing_format: string
    :param printing_format: this run printing format (SGTIN, string)
    """
    first_print = str(string_before_the_counter)
    if 'SGTIN' in printing_format or 'Test' in printing_format:
        first_print += 'T'
    if digits_in_counter < len(first_counter):
        is_ok = False
    else:
        dif_len = (digits_in_counter - len(first_counter))
        for i in range(digits_in_counter):
            # add zeros to where the counter is not needed
            if i < dif_len:
                first_print += '0'
            else:
                # add the first counter number by order to the string
                first_print += str(first_counter)
                break
        is_ok = True
    return first_print, is_ok


def printing_test_window():
    """
    opens the GUI for user input for test print
    :return: dictionary of user inputs
    """
    printing_format = 'Test'
    folder_name = 'configs'
    file_name = 'gui_printer_inputs_4_Test_do_not_delete.json'
    gui_inputs_values = open_json(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                  default_values=DefaultGUIValues(printing_format).default_gui_values)

    # Define the window's contents
    layout = [[SimGUI.Text('Job to print for pass and fail:'),
               SimGUI.InputCombo(('SGTIN_only', 'SGTIN_QR', 'devkit_TEO', 'devkit_TIKI', 'empty'),
                                 default_value="SGTIN_QR", key='passJobName')],
              [SimGUI.Text("What is the first counter number?")],
              [SimGUI.Input(gui_inputs_values['firstPrintingValue'], key='firstPrintingValue')],
              [SimGUI.Checkbox('Insert reel number manually?', default=True, key='isManually')],
              [SimGUI.Text("for manual mode only - what is the sgtin number?", key='sgtinNumManuallyText'),
               SimGUI.Input(gui_inputs_values['sgtin'], key='sgtinNumManually')],
              [SimGUI.Text("for manual mode only - what is the reel number?", key='reelNumManuallyText'),
               SimGUI.Input(gui_inputs_values['reelNumManually'], key='reelNumManually')],
              [SimGUI.Text(size=(60, 3), key='-OUTPUT-')],
              [SimGUI.Text("* tags in this run will not be serialized")],
              [SimGUI.Button('Check first print'), SimGUI.Button('Submit', button_color=('white', '#0e6251'))]]

    # Create the window
    window = SimGUI.Window('Printing Test', layout)

    # Display and interact with the Window using an Event Loop
    tag_digits_num = 4
    pass_job_name = None
    reel_number = ''
    did_withdraw = False
    reel_num = {}
    is_ok = True
    rerun_upload_func = False
    while True:
        event, values = window.read()
        should_submit = True
        # See if user wants to quit or window was closed
        if event == SimGUI.WINDOW_CLOSED or event is None:
            is_ok = False
            break
        if event == 'Submit':
            # check if the first counter number is int
            try:
                # to check if it is int as it should
                tmp = int(values['firstPrintingValue'])
                # the user want to insert one manually
                if not values['isManually']:
                    # there is no reel number already
                    if not did_withdraw:
                        window['-OUTPUT-'].update(
                            'Please wait until reel number will received from cloud\nIt might take few seconds')
                        try:
                            reel_num = get_reel_name_from_cloud_api()
                        except Exception:
                            window['-OUTPUT-'].update(
                                'there was a problem with get_reel_name_from_cloud_api()')
                            rerun_upload_func = True
                        # reelNum = {'data': 'blablabla11111111111111111'}
                        if 'data' in reel_num.keys() and len(reel_num['data']) == 26:
                            did_withdraw = True
                            reel_number = reel_num['data']
                        else:
                            should_submit = False
                            window['-OUTPUT-'].update(
                                'Data withdraw from cloud failed\nPlease try again or contact Wiliot')
                            continue
                    pass_job_name = values['passJobName']
                    first_counter = values['firstPrintingValue']
                    # Output a message to the window
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update(
                            'First counter number is too big for counter digits number!!\n'
                            'Please enter a new first counter number')
                        should_submit = False
                    else:
                        first_print, is_ok = get_printed_value(reel_num['data'], tag_digits_num, first_counter,
                                                               printing_format)
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                        print('The first tag printing value will be: ' + first_print)
                        should_submit = True
                # manual input
                elif values['isManually']:
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update(
                            'First counter number is too big for counter digits number!!\n'
                            'Please enter a new first counter number')
                        should_submit = False
                    else:
                        pass_job_name = values['passJobName']
                        reel_number = values['sgtinNumManually'] + values['reelNumManually']
                        first_counter = values['firstPrintingValue']
                        first_print, is_ok = get_printed_value(reel_number, tag_digits_num,
                                                               first_counter, printing_format)
                        # Output a message to the window
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                        should_submit = True
            except Exception:
                window['-OUTPUT-'].update(
                    'First counter is not a number!!\nPlease enter a new first counter number')
                should_submit = False

            if should_submit:
                break

        if event == 'Check first print':
            # check if the first counter number is int
            try:
                tmp = int(values['firstPrintingValue'])
                # the user want to insert one manually
                if not values['isManually']:
                    # there is no reel number already
                    if not did_withdraw:
                        window['-OUTPUT-'].update(
                            'Please wait until reel number will received from cloud\nIt might take few seconds')
                        try:
                            reel_num = get_reel_name_from_cloud_api()
                        except Exception:
                            window['-OUTPUT-'].update(
                                'there was a problem with get_reel_name_from_cloud_api()')
                            rerun_upload_func = True                        # reelNum = {'data': 'blablabla11111111111111111'}
                        if 'data' in reel_num.keys() and len(reel_num['data']) == 26:
                            did_withdraw = True
                            reel_number = reel_num['data']
                        else:
                            window['-OUTPUT-'].update(
                                'Data withdraw from cloud failed\nPlease try again or contact Wiliot')
                            continue
                    pass_job_name = values['passJobName']
                    first_counter = values['firstPrintingValue']
                    first_print, is_ok = get_printed_value(reel_num['data'], tag_digits_num,
                                                           first_counter, printing_format)
                    # Output a message to the window
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update('First counter number is too big for counter digits number!!\n'
                                                  'Please enter a new first counter number')
                    else:
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                # manual input
                elif values['isManually']:
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update('First counter number is too big for counter digits number!!\n'
                                                  'Please enter a new first counter number')
                    else:
                        pass_job_name = values['passJobName']
                        reel_number = values['sgtinNumManually'] + values['reelNumManually']
                        first_counter = values['firstPrintingValue']
                        first_print, is_ok = get_printed_value(reel_number, tag_digits_num,
                                                               first_counter, printing_format)
                        # Output a message to the window
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
            except Exception:
                window['-OUTPUT-'].update(
                    'First counter is not a number!!\nPlease enter a new first counter number')

    # Finish up by removing from the screen
    window.close()
    v = {'passJobName': pass_job_name, 'stringBeforeCounter': reel_number, 'digitsInCounter': tag_digits_num,
         'firstPrintingValue': values['firstPrintingValue'], 'failJobName': pass_job_name}
    data_to_save = {'passJobName': pass_job_name, 'sgtin': reel_number[:22], 'reelNumManually': reel_number[22:26],
                    'firstPrintingValue': values['firstPrintingValue']}
    f = open(os.path.join(folder_name, file_name), "w")
    json.dump(data_to_save, f)
    f.close()
    if rerun_upload_func:
        get_reel_name_from_cloud_api()
    return v, is_ok


def printing_sgtin_window():
    """
    opens the GUI for user input for SGTIN print
    :return: dictionary of user inputs
    """
    printing_format = 'SGTIN'
    folder_name = 'configs'
    file_name = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'
    gui_inputs_values = open_json(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                  default_values=DefaultGUIValues(printing_format).default_gui_values)

    # Define the window's contents
    layout = [[SimGUI.Text('Job to print for pass:'),
               SimGUI.InputCombo(('SGTIN_only', 'SGTIN_QR', 'devkit_TEO', 'devkit_TIKI', 'empty'),
                                 default_value="SGTIN_QR", key='passJobName')],
              [SimGUI.Text("What is the first counter number?")],
              [SimGUI.Input(gui_inputs_values['firstPrintingValue'], key='firstPrintingValue')],
              [SimGUI.Checkbox('Insert reel number manually?', default=False, key='isManually')],
              [SimGUI.Text("for manual mode only - what is the sgtin number?", key='sgtinNumManuallyText'),
               SimGUI.Input(gui_inputs_values['sgtin'], key='sgtinNumManually')],
              [SimGUI.Text("for manual mode only - what is the reel number?", key='reelNumManuallyText'),
               SimGUI.Input(gui_inputs_values['reelNumManually'], key='reelNumManually')],
              [SimGUI.Text(size=(60, 3), key='-OUTPUT-')],
              [SimGUI.Button('Check first print'), SimGUI.Button('Submit', button_color=('white', '#0e6251'))]]

    # Create the window
    window = SimGUI.Window('Printing SGTIN', layout)

    # Display and interact with the Window using an Event Loop
    tag_digits_num = 4
    pass_job_name = None
    reel_number = ''
    did_withdraw = False
    reel_num = {}
    is_ok = True
    rerun_upload_func = False
    while True:
        event, values = window.read()
        should_submit = True
        # See if user wants to quit or window was closed
        if event == SimGUI.WINDOW_CLOSED or event is None:
            is_ok = False
            break
        if event == 'Submit':
            # check if the first counter number is int
            try:
                # to check if it is int as it should
                tmp = int(values['firstPrintingValue'])
                # the user want to insert one manually
                if not values['isManually']:
                    # there is no reel number already
                    if not did_withdraw:
                        window['-OUTPUT-'].update(
                            'Please wait until reel number will received from cloud\nIt might take few seconds')
                        try:
                            reel_num = get_reel_name_from_cloud_api()
                        except Exception:
                            window['-OUTPUT-'].update(
                                'there was a problem with get_reel_name_from_cloud_api()')
                            rerun_upload_func = True                        # reelNum = {'data': 'blablabla11111111111111111'}
                        if 'data' in reel_num.keys() and len(reel_num['data']) == 26:
                            did_withdraw = True
                            reel_number = reel_num['data']
                        else:
                            should_submit = False
                            window['-OUTPUT-'].update(
                                'Data withdraw from cloud failed\nPlease try again or contact Wiliot')
                            continue
                    pass_job_name = values['passJobName']
                    first_counter = values['firstPrintingValue']
                    # Output a message to the window
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update(
                            'First counter number is too big for counter digits number!!\n'
                            'Please enter a new first counter number')
                        should_submit = False
                    else:
                        first_print, is_ok = get_printed_value(reel_num['data'], tag_digits_num, first_counter,
                                                               printing_format)
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                        print('The first tag printing value will be: ' + first_print)
                        should_submit = True
                # manual input
                elif values['isManually']:
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update(
                            'First counter number is too big for counter digits number!!\n'
                            'Please enter a new first counter number')
                        should_submit = False
                    else:
                        pass_job_name = values['passJobName']
                        reel_number = values['sgtinNumManually'] + values['reelNumManually']
                        first_counter = values['firstPrintingValue']
                        first_print, is_ok = get_printed_value(reel_number, tag_digits_num,
                                                               first_counter, printing_format)
                        # Output a message to the window
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                        should_submit = True
            except Exception:
                window['-OUTPUT-'].update(
                    'First counter is not a number!!\nPlease enter a new first counter number')
                should_submit = False

            if should_submit:
                break

        if event == 'Check first print':
            # check if the first counter number is int
            try:
                tmp = int(values['firstPrintingValue'])
                # the user want to insert one manually
                if not values['isManually']:
                    # there is no reel number already
                    if not did_withdraw:
                        window['-OUTPUT-'].update(
                            'Please wait until reel number will received from cloud\nIt might take few seconds')
                        try:
                            reel_num = get_reel_name_from_cloud_api()
                        except Exception:
                            window['-OUTPUT-'].update(
                                'there was a problem with get_reel_name_from_cloud_api()')
                            rerun_upload_func = True                        # reelNum = {'data': 'blablabla11111111111111111'}
                        if 'data' in reel_num.keys() and len(reel_num['data']) == 26:
                            did_withdraw = True
                            reel_number = reel_num['data']
                        else:
                            window['-OUTPUT-'].update(
                                'Data withdraw from cloud failed\nPlease try again or contact Wiliot')
                            continue
                    pass_job_name = values['passJobName']
                    first_counter = values['firstPrintingValue']
                    first_print, is_ok = get_printed_value(reel_num['data'], tag_digits_num,
                                                           first_counter, printing_format)
                    # Output a message to the window
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update('First counter number is too big for counter digits number!!\n'
                                                  'Please enter a new first counter number')
                    else:
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                # manual input
                elif values['isManually']:
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update('First counter number is too big for counter digits number!!\n'
                                                  'Please enter a new first counter number')
                    else:
                        pass_job_name = values['passJobName']
                        reel_number = values['sgtinNumManually'] + values['reelNumManually']
                        first_counter = values['firstPrintingValue']
                        first_print, is_ok = get_printed_value(reel_number, tag_digits_num,
                                                               first_counter, printing_format)
                        # Output a message to the window
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
            except Exception:
                window['-OUTPUT-'].update(
                    'First counter is not a number!!\nPlease enter a new first counter number')

    # Finish up by removing from the screen
    window.close()
    v = {'passJobName': pass_job_name, 'stringBeforeCounter': reel_number, 'digitsInCounter': tag_digits_num,
         'firstPrintingValue': values['firstPrintingValue'], 'failJobName': 'line_'}
    data_to_save = {'passJobName': pass_job_name, 'sgtin': reel_number[:22], 'reelNumManually': reel_number[22:26],
                    'firstPrintingValue': values['firstPrintingValue']}

    f = open(os.path.join(folder_name, file_name), "w")
    json.dump(data_to_save, f)
    f.close()
    if rerun_upload_func:
        get_reel_name_from_cloud_api()
    return v, is_ok


def save_screen(tested, passed, yield_, missing_labels, problem_in_locations_hist_val, ttfgp_avg,
                default_upload_value=None):
    """
    open last GUI
    :type tested: int
    :param tested: amount of tested tags
    :type passed: int
    :param passed: amount of passed tags
    :type yield_: float
    :param yield_: yield in the run
    :type missing_labels: int
    :param missing_labels: amount of missing_labels tags
    :type problem_in_locations_hist_val: dictionary
    :param problem_in_locations_hist_val: histogram of problem in the run (amount of locations)
    :type ttfgp_avg: float
    :param ttfgp_avg: average of ttfgp (time to first good packet) in this run
    :type default_upload_value: string ('Yes' or 'No')
    :param default_upload_value: default value to use in upload to cloud field
    :return dictionary with the user inputs (should upload, last comments)
    """
    if ttfgp_avg is None or str(ttfgp_avg) == 'nan':
        ttfgp_avg_line = []
    elif ttfgp_avg < 1:
        ttfgp_avg_line = [SimGUI.Text("Average time to first good packet is OK (" + '{0:.4g}'.format(ttfgp_avg) + " secs)",
                                      border_width=10, background_color='green')]
    else:
        ttfgp_avg_line = [SimGUI.Text("Average time to first good packet is too high (" + '{0:.4g}'.format(ttfgp_avg) +
                                      " secs)", border_width=10, background_color='red')]
    if default_upload_value is not None:
        def_upload = default_upload_value
    else:
        def_upload = "Yes"

    layout = [
        [SimGUI.Text('Tags tested = ' + str(tested), size=(21, 1)),
         SimGUI.Text('Tags passed = ' + str(passed), size=(21, 1))],
        [SimGUI.Text('Yield = ' + '{0:.4g}'.format(yield_) + '%', size=(21, 2)),
         SimGUI.Text('Missing labels = ' + str(missing_labels), size=(21, 2))],
        ttfgp_avg_line,
        [SimGUI.Text('Would you like to upload this log to the cloud?'),
         SimGUI.InputCombo(('Yes', 'No'), default_value=def_upload, key='upload')],
        [SimGUI.Text('Post run comments:')],
        [SimGUI.InputText('', key='comments')],
        [SimGUI.Button('Expand'), SimGUI.Submit(button_color=('white', '#0e6251'))]]

    window = SimGUI.Window('Offline Tester - Run highlights (Shrunk)', layout)
    expand = False
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == SimGUI.WINDOW_CLOSED or event is None:
            print("user exited the program, upload did not happen")
            break
        if event == 'Submit':
            break
        if event == 'Expand':
            expand = True
            break
    window.close()
    if expand:
        expand_save_screen(tested, passed, yield_, missing_labels, problem_in_locations_hist_val, ttfgp_avg,
                           default_upload_value=values['upload'])
    return values


def expand_save_screen(tested, passed, yield_, missing_labels, problem_in_locations_hist_val, ttfgp_avg,
                       default_upload_value=None):
    """
    open last GUI (expanded)
    :type tested: int
    :param tested: amount of tested tags
    :type passed: int
    :param passed: amount of passed tags
    :type yield_: float
    :param yield_: yield in the run
    :type missing_labels: int
    :param missing_labels: amount of missing_labels tags
    :type problem_in_locations_hist_val: dictionary
    :param problem_in_locations_hist_val: histogram of problem in the run (amount of locations)
    :type ttfgp_avg: float
    :param ttfgp_avg: average of ttfgp (time to first good packet) in this run
    :type default_upload_value: string ('Yes' or 'No')
    :param default_upload_value: default value to use in upload to cloud field
    :return dictionary with the user inputs (should upload, last comments)
    """
    if ttfgp_avg is None or str(ttfgp_avg) == 'nan':
        ttfgp_avg_line = []
    elif ttfgp_avg < 1:
        ttfgp_avg_line = [SimGUI.Text("Average time to first good packet is OK (" + '{0:.4g}'.format(ttfgp_avg) +
                                      " secs)", border_width=10, background_color='green')]
    else:
        ttfgp_avg_line = [SimGUI.Text("Average time to first good packet is too high (" + '{0:.4g}'.format(ttfgp_avg) +
                                      " secs)", border_width=10, background_color='red')]
    layout = [
        [SimGUI.Text('Tags tested = ' + str(tested), size=(21, 1)),
         SimGUI.Text('Tags passed = ' + str(passed), size=(21, 1))],
        [SimGUI.Text('Yield = ' + '{0:.4g}'.format(yield_) + '%', size=(21, 2)),
         SimGUI.Text('Missing labels = ' + str(missing_labels), size=(21, 2))],
        ttfgp_avg_line,
        [SimGUI.Text('The following events happened in the run [ = amount of locations the event happened in]',
                     size=(63, 2))]]
    counter = 0
    line = []
    for key in problem_in_locations_hist_val.keys():
        counter += 1
        line.append(SimGUI.Text(str(key) + ' = ' + str(problem_in_locations_hist_val[key]), size=(21, 1)))
        if counter % 3 == 0:
            layout.append(line)
            line = []
    if counter % 3 != 0:
        layout.append(line)
    if default_upload_value is not None:
        def_upload = default_upload_value
    else:
        def_upload = "Yes"
    layout.append([SimGUI.Text('Would you like to upload this log to the cloud?'),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=def_upload, key='upload')])
    layout.append([SimGUI.Text('Post run comments:')])
    layout.append([SimGUI.InputText('', key='comments')])
    layout.append([SimGUI.Button('Shrink'), SimGUI.Submit(button_color=('white', '#0e6251'))])

    window = SimGUI.Window('Offline Tester - Run highlights (Expanded)', layout)
    shrink = False
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == SimGUI.WINDOW_CLOSED or event is None:
            print("user exited the program, upload did not happen")
            break
        if event == 'Submit':
            break
        if event == 'Shrink':
            shrink = True
            break
    window.close()
    if shrink:
        save_screen(tested, passed, yield_, missing_labels, problem_in_locations_hist_val, ttfgp_avg,
                    default_upload_value=values['upload'])
    return values


def pop_up_window(message=None):
    """
    open pop up window
    :type message: string
    :param message: message to print on the window
    """
    if message is None:
        return

    layout = [
        [SimGUI.Text(message, background_color='red')],
        [SimGUI.Button('Done')]]

    window = SimGUI.Window('Offline pop-up window', layout, background_color='red', keep_on_top=True,
                           element_padding=((0, 0), (0, 0)), )
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == SimGUI.WINDOW_CLOSED or event == 'Done':
            break

    window.close()
    return


def get_reel_name_from_cloud_api():
    """
    api to receive reel number from cloud (should use it to avoid duplications)
    :return: the reel number (in 0x)
    """
    try:
        # this part is legacy code that can only be removed (and replaced with the part that commented out)
        # when the public API is created (should replace this private API)
        assert ('R2R_station_name' in os.environ), 'R2R_station_name is missing from PC environment variables'
        tester_station_name = os.environ['R2R_station_name']
        user_name = os.environ['FUSION_AUTH_USER']
        print('success in getting the FUSION_AUTH_USER environment variables')
        password = os.environ['FUSION_AUTH_PASSWORD']
        print('success in getting the environment variables')

        # TODO - enable this part and delete previous after replacing the API
        # file_path, user_name, password, owner_id, is_successful = check_user_config_is_ok()
        # if not is_successful:
        #     raise Exception('check_user_config_is_ok() failed')
        # # check if the system variable exist
        # assert ('testerStationName' in os.environ), 'testerStationName is missing from PC environment variables, ' \
        #                                             'please add it in the following convention:' \
        #                                             ' <company name>_<tester number>'
        # tester_station_name = os.environ['testerStationName']
    except Exception:
        raise Exception('system variables are missing from this PC')

    try:
        conn = http.client.HTTPSConnection("api.wiliot.com")
        headers = {'accept': "application/json"}
        conn.request("POST", "/v1/auth/token?password=" + password + "&username=" + user_name, headers=headers)
        res = conn.getresponse()
        data = res.read()
        tokens = json.loads(data.decode("utf-8"))
        token = tokens['access_token']
        headers = {
            'accept': "*/*",
            'authorization': "Bearer " + token + "",
            'content-type': "application/json"
        }
        body = json.dumps({"printerId": tester_station_name})
        payload = body
        conn.request("POST", "/v1/owner/wiliot/tag/roll/print", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print("get_reel_name_from_cloud_API answer is:")
        print(data.decode("utf-8"))
        return ast.literal_eval(data.decode("utf-8"))

    except Exception:
        print("An exception occurred at get_reel_name_from_cloud_API()")


class PrinterNeedsResetException(Exception):
    pass


class R2rGpio(object):
    """
    class to open and use communication to Arduino on R2R machine
    """

    def __init__(self):
        """
        initialize params and port
        """
        self.baud_rate = 1000000
        ports_list = [s.device for s in serial.tools.list_ports.comports()]
        if len(ports_list) == 0:
            ports_list = [s.name for s in serial.tools.list_ports.comports()]
            if len(ports_list) == 0:
                print("no serial ports were found. please check your connections", "init")
                return

        for port in ports_list:
            try:
                self.comport = port
                self.s = serial.Serial(self.comport, self.baud_rate, timeout=0, write_timeout=0)
                response = self.query("*IDN?")
                if ("Williot R2R GPIO" in response):
                    print('Found ' + response + " Serial Number " + self.query("SER?"))
                    self.s.flushInput()
                    break
                else:
                    self.s.close()
            except (OSError, serial.SerialException):
                pass
            except Exception as e:
                print(e)

    def __del__(self):
        if self.s is not None:
            self.s.close()

    def write(self, cmd):
        """
        Send the input cmd string via COM Socket
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()

        try:
            self.s.flushInput()
            self.s.write(str.encode(cmd))
        except Exception:
            pass

    def query(self, cmd):
        """
        Send the input cmd string via COM Socket and return the reply string
        :return: massage from arduino (w/o the '\t\n')
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()
            sleep(1)
        self.s.flushInput()
        sleep(1)
        try:
            self.s.write(str.encode(cmd))
            sleep(2)
            data = self.s.readlines()
            value = data[0].decode("utf-8")
            # Cut the last character as the device returns a null terminated string
            value = value[:-2]
        except Exception:
            value = ''
        return value

    def read(self):
        """
        Send the input cmd string via COM Socket and return the reply string
        :return: massage from arduino (w/o the '\t\n')
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()
        try:
            while self.s.in_waiting == 0:
                pass

            data = self.s.readlines()
            self.s.flushInput()
            value = data[0].decode("utf-8")
            # Cut the last character as the device returns a null terminated string
            value = value[:-2]
        except Exception:
            value = ''
        return value

    def gpio_state(self, gpio, state):
        """
        gets the gpio state:
            my_gpio.gpio_state(3, "ON")
               start"on"/stop"off"
            my_gpio.gpio_state(4, "ON")
               enable missing label
        :param gpio: what gpio to write to
        :param state: to what state to transfer (ON / OFF)
        :return: reply from Arduino
        """
        cmd = 'GPIO' + str(gpio) + "_" + state
        replay = self.query(cmd)
        return replay

    def pulse(self, gpio, time):
        """
        send a pulse to the r2r machine:
            my_gpio.pulse(1, 1000)
               Pass
            my_gpio.pulse(2, 1000)
               fail
        :param gpio: what gpio to write to
        :param time: how long is the pulse
        :return: True if succeeded, False otherwise
        """
        cmd = 'GPIO' + str(gpio) + '_PULSE ' + str(time)
        self.write(cmd)
        sleep(time * 2 / 1000)
        replay = self.read()
        if replay == "Completed Successfully":
            return True
        else:
            return False
