import sys
import time
import logging
from hein_utilities.runnable import Runnable
from ftdi_serial import Serial
from datetime import datetime, timedelta


import vapourtec
from vapourtec.sf10 import SF10
from gui.sf10 import design
from PyQt5 import QtWidgets, QtCore
from vapourtec.errors import VapourtecError
from PyQt5.QtWidgets import QApplication, QTextEdit


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


"""
stylesheet examples - https://doc.qt.io/qt-5/stylesheet-examples.html

create a .py from the gui design.ui file
venv\Scripts\pyuic5.exe gui/sf10/design.ui -o gui/sf10/design.py

create installable - windows version
venv\Scripts\pyinstaller --onefile --windowed --specpath gui/sf10/built_gui --workpath gui/sf10/built_gui/build --distpath gui/sf10/built_gui/dist gui/sf10/main.py
"""


class SF10GUI(QtWidgets.QMainWindow,
              design.Ui_MainWindow,
              Runnable):
    def __init__(self, parent=None):
        Runnable.__init__(self, logger)
        super().__init__(parent)
        self.setupUi(self)

        self.sf10: SF10 = None

        self.action_1 = None
        self.action_2 = None

        # set up logging
        self.logging_output_textEdit_handler = QTextEditLoggerHandler(widget=self.logging_output_textEdit)
        self.gui_logger = logger.getChild('SF10GUI')
        self.gui_logger.setLevel(level=logging.INFO)
        self.gui_logger.addHandler(self.logging_output_textEdit_handler)

        self.make_device_port_comboBox_options()
        self.start()

    def setupUi(self, MainWindow):
        super().setupUi(self)
        self.export_log_file_pushButton.clicked.connect(self.export_log_file)
        self.find_devices_pushButton.clicked.connect(self.make_device_port_comboBox_options)

        self.connect_pushButton.clicked.connect(self.connect_to_sf10)
        self.disconnect_pushButton.clicked.connect(self.disconnect_from_sf10)

        self.flow_radioButton.clicked.connect(self.flow_mode_selected)
        self.gas_radioButton.clicked.connect(self.gas_mode_selected)
        self.regulator_radioButton.clicked.connect(self.regulator_mode_selected)
        self.dose_radioButton.clicked.connect(self.dose_mode_selected)
        self.ramp_radioButton.clicked.connect(self.ramp_mode_selected)

        self.start_pump_pushButton.clicked.connect(self.start_sf10)
        self.stop_pump_pushButton.clicked.connect(self.stop_sf10)

        self.action_1_pushButton.clicked.connect(self.action_1_pushButton_action)
        self.action_2_pushButton.clicked.connect(self.action_2_pushButton_action)

        self.actionAbout.triggered.connect(self.about_button_clicked)

    def flow_mode_selected(self):
        self.mode_flow_groupBox.setEnabled(True)
        self.mode_gas_groupBox.setDisabled(True)
        self.mode_regulator_groupBox.setDisabled(True)
        self.mode_dose_groupBox.setDisabled(True)
        self.mode_ramp_groupBox.setDisabled(True)

    def gas_mode_selected(self):
        self.mode_flow_groupBox.setDisabled(True)
        self.mode_gas_groupBox.setEnabled(True)
        self.mode_regulator_groupBox.setDisabled(True)
        self.mode_dose_groupBox.setDisabled(True)
        self.mode_ramp_groupBox.setDisabled(True)

    def regulator_mode_selected(self):
        self.mode_flow_groupBox.setDisabled(True)
        self.mode_gas_groupBox.setDisabled(True)
        self.mode_regulator_groupBox.setEnabled(True)
        self.mode_dose_groupBox.setDisabled(True)
        self.mode_ramp_groupBox.setDisabled(True)

    def dose_mode_selected(self):
        self.mode_flow_groupBox.setDisabled(True)
        self.mode_gas_groupBox.setDisabled(True)
        self.mode_regulator_groupBox.setDisabled(True)
        self.mode_dose_groupBox.setEnabled(True)
        self.mode_ramp_groupBox.setDisabled(True)

    def ramp_mode_selected(self):
        self.mode_flow_groupBox.setDisabled(True)
        self.mode_gas_groupBox.setDisabled(True)
        self.mode_regulator_groupBox.setDisabled(True)
        self.mode_dose_groupBox.setDisabled(True)
        self.mode_ramp_groupBox.setEnabled(True)

    def start_sf10(self):
        if self.sf10 is not None:
            if self.valve_a_radioButton.isChecked():
                self.sf10.set_valve(SF10.VALVE_A)
                self.gui_logger.info(f'Set valve position to {SF10.VALVE_A}')
            elif self.valve_b_radioButton.isChecked():
                self.sf10.set_valve(SF10.VALVE_B)
                self.gui_logger.info(f'Set valve position to {SF10.VALVE_B}')
            else:
                # no valve selected
                self.create_pop_up_message_box('You must select a valve', 'No valve selected')
                return

            if self.flow_radioButton.isChecked():
                self.sf10.set_mode(SF10.MODE_FLOW)
                flow_rate = self.flow_flow_rate_doubleSpinBox.value()
                self.sf10.set_flow_rate(flow_rate)
                self.gui_logger.info(f'Set to flow mode with flow rate at {flow_rate} mL/min')
            elif self.regulator_radioButton.isChecked():
                self.sf10.set_mode(SF10.MODE_REGULATOR)
                regulator_pressure = self.regulator_pressure_doubleSpinBox.value()
                self.gui_logger.info(f'Set to regulator mode with pressure at {regulator_pressure} bar')
                self.sf10.set_regulator_pressure(regulator_pressure)
            elif self.dose_radioButton.isChecked():
                self.sf10.set_mode(SF10.MODE_DOSE)
                dose_volume = self.dose_volume_doubleSpinBox.value()
                dose_flow_rate = self.dose_flow_rate_doubleSpinBox.value()
                self.sf10.set_flow_rate(dose_flow_rate)
                self.sf10.set_dose_volume(dose_volume)
                self.gui_logger.info(f'Set to dose mode with flow rate at {dose_flow_rate} mL/min and '
                                     f'dose volume at {dose_volume} mL')
            elif self.gas_radioButton.isChecked():
                self.sf10.set_mode(SF10.MODE_GAS)
                gas_flow_rate = self.gas_flow_rate_doubleSpinBox.value()
                self.sf10.set_gas_flow_rate(gas_flow_rate)
                self.gui_logger.info(f'Set to gas mode with gas flow rate at {gas_flow_rate} ssc/min')
            elif self.ramp_radioButton.isChecked():
                self.sf10.set_mode(SF10.MODE_RAMP)
                initial = self.ramp_initial_rate_doubleSpinBox.value()
                final = self.ramp_final_rate_doubleSpinBox.value()
                t = self.ramp_time_doubleSpinBox.value()
                self.sf10.set_ramp(initial, final, t)
                self.gui_logger.info(f'Set to ramp mode from {initial} mL/min to {final} mL/ min '
                                     f'over {t} mins')
            else:
                # no mode selected
                self.create_pop_up_message_box('You must select a mode', 'No mode selected')
                return

            self.sf10.start()
            self.gui_logger.info('Start pump')

    def stop_sf10(self):
        if self.sf10 is not None:
            self.sf10.stop()
            self.gui_logger.info('Stop pump')

    def action_1_pushButton_action(self):
        if self.action_1_pushButton.text() == 'Schedule':
            current_time = datetime.now()
            action_time = current_time + timedelta(minutes=self.action_1_minutes_spinBox.value())
            self.action_1 = {'time': action_time,
                             'action': self.action_1_select_action_comboBox.currentText(),
                             }
            self.action_1_pushButton.setText('Cancel')
            self.action_1_minutes_spinBox.setDisabled(True)
            self.action_1_select_action_comboBox.setDisabled(True)
            self.action_1_countdown.setText(f'Trigger at {action_time.strftime("%I:%M %p")}')
        else:
            self.action_1 = None
            self.action_1_pushButton.setText('Schedule')
            self.action_1_minutes_spinBox.setEnabled(True)
            self.action_1_select_action_comboBox.setEnabled(True)
            self.action_1_countdown.setText(f'Not scheduled yet')

    def action_2_pushButton_action(self):
        if self.action_2_pushButton.text() == 'Schedule':
            current_time = datetime.now()
            action_time = current_time + timedelta(minutes=self.action_2_minutes_spinBox.value())
            self.action_2 = {'time': action_time,
                             'action': self.action_2_select_action_comboBox.currentText(),
                             }
            self.action_2_pushButton.setText('Cancel')
            self.action_2_minutes_spinBox.setDisabled(True)
            self.action_2_select_action_comboBox.setDisabled(True)
            self.action_2_countdown.setText(f'Trigger at {action_time.strftime("%I:%M %p")}')
        else:
            self.action_2 = None
            self.action_2_pushButton.setText('Schedule')
            self.action_2_minutes_spinBox.setEnabled(True)
            self.action_2_select_action_comboBox.setEnabled(True)
            self.action_2_countdown.setText(f'Not scheduled yet')

    def connect_to_sf10(self):
        port = str(self.device_port_comboBox.currentText())
        try:
            self.sf10 = SF10(device_port=port, safe_connect=False)
            self.on_sf10_connect()
            self.gui_logger.info(f'Connect to pump at port {port}')
        except VapourtecError as e:
            self.create_pop_up_message_box(message=str(e),
                                           window_title='Connection error')

    def disconnect_from_sf10(self):
        if self.sf10 is not None:
            self.sf10.disconnect()
            self.sf10 = None
            self.on_sf10_disconnect()
            self.gui_logger.info('Disconnect from pump')

    def run(self):
        """keep the gui up to date while the pump is connected, mainly to keep track of when basic automation should
        be triggered"""
        while self.running:
            self.update_state()

    def update_state(self):
        if self.sf10 is not None:
            current_time = datetime.now()
            if self.action_1 is not None:
                action_time = self.action_1['time']
                if current_time >= action_time:
                    action = self.action_1['action']
                    self.action_1_pushButton_action()
                    self.trigger_scheduled_action(action)
                    time.sleep(1)
            if self.action_2 is not None:
                action_time = self.action_2['time']
                if current_time >= action_time:
                    action = self.action_2['action']
                    self.action_2_pushButton_action()
                    self.trigger_scheduled_action(action)
                    time.sleep(1)

    def trigger_scheduled_action(self, action):
        if action == 'start pump':
            self.start_sf10()
        elif action == 'stop pump':
            self.stop_sf10()

    def reset_actions(self):
        self.action_1 = None
        self.action_2 = None

    def closeEvent(self, *args, **kwargs):
        self.stop()
        self.disconnect_from_sf10()
        super().closeEvent(*args, **kwargs)

    def on_sf10_disconnect(self):
        self.disconnect_pushButton.setDisabled(True)
        self.start_pump_pushButton.setDisabled(True)
        self.stop_pump_pushButton.setDisabled(True)
        self.action_1_pushButton.setDisabled(True)
        self.action_2_pushButton.setDisabled(True)

        self.connect_pushButton.setEnabled(True)

        self.reset_actions()

    def on_sf10_connect(self):
        self.disconnect_pushButton.setEnabled(True)
        self.start_pump_pushButton.setEnabled(True)
        self.stop_pump_pushButton.setEnabled(True)
        self.action_1_pushButton.setEnabled(True)
        self.action_2_pushButton.setEnabled(True)

        self.connect_pushButton.setDisabled(True)

        self.reset_actions()

    def export_log_file(self):
        try:
            file_path = str(QtWidgets.QFileDialog.getSaveFileName(self,
                                                                  "Select log file location",
                                                                  filter="CSV (*.csv)")[0],
                            )
            if file_path != '':
                file = open(file_path, 'w')
                log_output = self.logging_output_textEdit.toPlainText()
                file.write(log_output)
                file.close()

                window_title = 'Log file exported'
                message = f'Exported log file to: {file_path}'
                self.create_pop_up_message_box(window_title=window_title,
                                               message=message,
                                               )
            else:
                pass
        except:
            pass

    def make_device_port_comboBox_options(self):
        list_of_all_connected_ports = Serial.list_device_ports()
        _translate = QtCore.QCoreApplication.translate
        self.device_port_comboBox.clear()

        for index, port_id in enumerate(list_of_all_connected_ports):
            self.device_port_comboBox.addItem(f"{port_id}")
            self.device_port_comboBox.setItemText(index, _translate("MainWindow", port_id))

    def about_button_clicked(self):
        message = f"""Build version: {vapourtec.__version__}<br /><br />
                    For more information, check: <a href="https://gitlab.com/heingroup/vapourtec_private">https://gitlab.com/heingroup/vapourtec_private</a>"""
        self.create_pop_up_message_box(message=message,
                                       window_title='About')

    def create_pop_up_message_box(self,
                                  message: str,
                                  window_title: str):
        '''convenience method for creating a pop up message box, with a message and a window title'''
        message_box = QtWidgets.QMessageBox()
        message_box.setIcon(QtWidgets.QMessageBox.Information)
        message_box.setText(f"{message}")
        message_box.setWindowTitle(f"{window_title}")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        message_box.exec()


class QTextEditLoggerHandler(logging.Handler):
    def __init__(self,
                 widget: QTextEdit,
                 formatter: logging.Formatter = logging.Formatter(fmt='%(asctime)s, %(message)s',
                                                                  datefmt='%Y/%m/%d, %H:%M:%S'),
                 ):
        """
        A logging handler to output logging to a PyQt QTextEdit widget

        :param QTextEdit, widget: widget to log to
        :param logging.Formatter, formatter: formatter for the handler
        """
        super().__init__()
        self.widget = widget
        self.setFormatter(formatter)

    def emit(self, record):
        """
        Emit a logging record - append a formatted logging output to the widget

        :param record:
        :return:
        """
        msg = self.format(record)
        self.widget.append(msg)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    form = SF10GUI()

    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
