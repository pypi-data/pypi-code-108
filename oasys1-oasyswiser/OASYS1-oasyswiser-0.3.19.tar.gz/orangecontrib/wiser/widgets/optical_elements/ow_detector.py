import sys, numpy

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QSlider
from PyQt5.QtCore import QRect, Qt

from orangewidget import gui
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.util.oasys_util import EmittingStream
from orangewidget.settings import Setting

from syned.widget.widget_decorator import WidgetDecorator

from LibWiser import Foundation, Optics
from LibWiser import Units as Units

from wofrywiser.beamline.beamline_elements import WiserOpticalElement

from orangecontrib.wiser.widgets.gui.ow_optical_element import OWOpticalElement
from orangecontrib.wiser.widgets.gui.ow_wise_widget import PositioningDirectivesPhrases

WiseDetector = WiserOpticalElement()

class OWDetector(OWOpticalElement, WidgetDecorator):
    name = "Detector"
    id = "Detector"
    description = "Detector"
    icon = "icons/screen.png"
    priority = 10

    oe_name = Setting("Detector")
    OWOpticalElement.WhatWhereReferTo = Setting(PositioningDirectivesPhrases.Type.DistanceFromSource)

    has_figure_error_box = False
    is_full_propagator = True
    run_calculation = False

    alpha = Setting(90.0)
    length = Setting(0.0001)

    defocus_sweep = Setting(0.0)
    defocus_start = Setting(-1.0)
    defocus_stop = Setting(1.0)
    defocus_step = Setting(0.1)
    defocus_Nsteps = Setting(10)
    max_iter = Setting(50)
    show_animation = Setting(0)

    output_data_best_focus = None

    _defocus_sign = 1
    BestDefocus = Setting(0)
    BestHew = Setting(0)
    ActualBestDefocus = Setting(0)
    ActualBestHew = Setting(0)

    def after_change_workspace_units(self):
        super(OWDetector, self).after_change_workspace_units()

        # label = self.le_defocus_start.parent().layout().itemAt(0).widget()
        # label.setText(label.text() + " [" + self.workspace_units_label + "]")
        # label = self.le_defocus_stop.parent().layout().itemAt(0).widget()
        # label.setText(label.text() + " [" + self.workspace_units_label + "]")
        # label = self.le_defocus_step.parent().layout().itemAt(0).widget()
        # label.setText(label.text() + " [" + self.workspace_units_label + "]")


    def check_fields(self):
        super(OWDetector, self).check_fields()

    def build_mirror_specific_gui(self, container_box):

        self.tab_best = oasysgui.createTabPage(self.tabs_setting, "Find Best Focus")

        best_focus_box = oasysgui.widgetBox(self.tab_best, "", orientation="vertical",
                                            width=self.CONTROL_AREA_WIDTH - 20)

        bestFocusLabel = "Use for: \n* best focus metrics (HEW, position)\n* intensity profile at best focus position\n* high computational speed\n"

        gui.label(best_focus_box, self, bestFocusLabel, labelWidth=None, box=None, orientation=2)

        self.le_defocus_start = oasysgui.lineEdit(best_focus_box, self, "defocus_start", "Start [mm]", labelWidth=240, valueType=float, orientation="horizontal")
        self.le_defocus_stop = oasysgui.lineEdit(best_focus_box, self, "defocus_stop", "Stop [mm]", labelWidth=240, valueType=float, orientation="horizontal")
        # self.le_defocus_step = oasysgui.lineEdit(best_focus_box, self, "defocus_step", "Step [mm]", labelWidth=240, valueType=float, orientation="horizontal")
        self.le_max_iter = oasysgui.lineEdit(best_focus_box, self, "max_iter", "Max. iterations", labelWidth=240, valueType=int, orientation="horizontal")

        # gui.separator(best_focus_box, height=5)

        # gui.checkBox(best_focus_box, self, "show_animation", "Show animation during calculation")

        gui.separator(best_focus_box, height=5)

        button_box = oasysgui.widgetBox(best_focus_box, "", orientation="horizontal",
                                        width=self.CONTROL_AREA_WIDTH - 20)

        gui.button(button_box, self, "Scan Start", callback=self.do_find_focus_calculation, height=35)
        stop_button = gui.button(button_box, self, "Interrupt", callback=self.stop_best_focus_calculation, height=35)
        font = QFont(stop_button.font())
        font.setBold(True)
        stop_button.setFont(font)
        palette = QPalette(stop_button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('red'))
        stop_button.setPalette(palette)  # assign new palette

        self.save_button = gui.button(best_focus_box, self, "Save Complete Calculation Results",
                                      callback=self.save_best_focus_results, height=35)
        self.save_button.setEnabled(False)

        # PROBLEM HERE! STR AND FLOAT!

        le_BD = oasysgui.lineEdit(best_focus_box, self, "ActualBestDefocus", "Best focus at [m]", labelWidth=220,
                               valueType=float, orientation="horizontal")
        le_BD.setReadOnly(True)
        font = QFont(le_BD.font())
        # font.setBold(True)
        le_BD.setFont(font)
        palette = QPalette(le_BD.palette())
        palette.setColor(QPalette.Text, QColor('grey'))
        palette.setColor(QPalette.Base, QColor(243, 240, 140))
        le_BD.setPalette(palette)

        le_HEW = oasysgui.lineEdit(best_focus_box, self, "ActualBestHew", "HEW at best focus [" + u"\u03BC" + "m]", labelWidth=220,
                               valueType=float, orientation="horizontal")
        le_HEW.setReadOnly(True)
        font = QFont(le_HEW.font())
        # font.setBold(True)
        le_HEW.setFont(font)
        palette = QPalette(le_HEW.palette())
        palette.setColor(QPalette.Text, QColor('grey'))
        palette.setColor(QPalette.Base, QColor(243, 240, 140))
        le_HEW.setPalette(palette)

        self.best_focus_slider = None

        self.tab_sweep = oasysgui.createTabPage(self.tabs_setting, "Focal Scan")

        focus_sweep_box = oasysgui.widgetBox(self.tab_sweep, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH-20)

        focusSweepLabel = "Use for: \n* a complete plot of the spot size through the focal plane\n* a collection of the intensity profiles\n* below-average computational performance\n"

        gui.label(focus_sweep_box, self, focusSweepLabel, labelWidth=None, box=None, orientation=2)

        self.le_defocus_start = oasysgui.lineEdit(focus_sweep_box, self, "defocus_start", "Lower limit [mm]", labelWidth=240, valueType=float, orientation="horizontal", callbackOnType=True, callback=self.get_StepSize)
        self.le_defocus_stop  = oasysgui.lineEdit(focus_sweep_box, self, "defocus_stop",  "Upper limit [mm]", labelWidth=240, valueType=float, orientation="horizontal", callbackOnType=True, callback=self.get_StepSize)
        self.le_defocus_Nsteps  = oasysgui.lineEdit(focus_sweep_box, self, "defocus_Nsteps",  "No. of steps", labelWidth=240, valueType=int, orientation="horizontal", callbackOnType=True, callback=self.get_StepSize)
        le_defocus_step = oasysgui.lineEdit(focus_sweep_box, self, "defocus_step",  "Step [mm]", labelWidth=240, valueType=float, orientation="horizontal")

        le_defocus_step.setReadOnly(True)
        font = QFont(le_defocus_step.font())
        le_defocus_step.setFont(font)
        palette = QPalette(le_defocus_step.palette())
        palette.setColor(QPalette.Text, QColor('grey'))
        palette.setColor(QPalette.Base, QColor(243, 240, 140))
        le_defocus_step.setPalette(palette)

        gui.separator(focus_sweep_box, height=5)

        gui.checkBox(focus_sweep_box, self, "show_animation", "Show animation during calculation")

        gui.separator(focus_sweep_box, height=5)

        button_box = oasysgui.widgetBox(focus_sweep_box, "", orientation="horizontal", width=self.CONTROL_AREA_WIDTH-20)

        gui.button(button_box, self, "Scan Start", callback=self.do_focus_sweep_calculation, height=35)
        stop_button = gui.button(button_box, self, "Interrupt", callback=self.stop_best_focus_calculation, height=35)
        font = QFont(stop_button.font())
        font.setBold(True)
        stop_button.setFont(font)
        palette = QPalette(stop_button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('red'))
        stop_button.setPalette(palette) # assign new palette

        self.save_button = gui.button(focus_sweep_box, self, "Save Complete Calculation Results", callback=self.save_best_focus_results, height=35)
        self.save_button.setEnabled(False)

        self.best_focus_slider = None

    def get_StepSize(self):
        try:
            self.defocus_step = (self.defocus_stop - self.defocus_start) / self.defocus_Nsteps
        except:
            pass

    def get_ActualBestDefocus(self):
        return round(self.oe_f2 + self.BestDefocus, 4)

    def get_ActualBestHew(self):
        return round(self.BestHew * 1e6, 4)

    def initializeTabs(self):
        super(OWDetector, self).initializeTabs()

        self.tab.append(gui.createTabPage(self.tabs, "Intensity (Best Focus)"))
        self.tab.append(gui.createTabPage(self.tabs, "HEW and SIGMA"))
        self.plot_canvas.append(None)
        self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

    def get_native_optical_element(self):
        return Optics.Detector(L=self.length,
                               AngleGrazing=numpy.deg2rad(self.alpha))

    def get_optical_element(self, native_optical_element):
         return WiserOpticalElement(name=self.oe_name,
                                    boundary_shape=None,
                                    native_CoreOptics=native_optical_element,
                                    native_PositioningDirectives=self.get_PositionDirectives())


    def receive_specific_syned_data(self, optical_element):
        pass

    def check_syned_shape(self, optical_element):
        pass

    def getTabTitles(self):
        return ["Intensity (O.E. Focus)", "Phase (O.E. Focus)"]

    def getTitles(self):
        return ["Intensity (O.E. Focus)", "Phase (O.E. Focus)"]

    def getXTitles(self):
        return ["S", "S"]

    def getXUnits(self):
        return ["m", "m"]

    def getYTitles(self):
        return ["|E0|**2", "Phase"]

    def getVariablesToPlot(self):
        return [(0, 1), (0, 2)]

    def getLogPlot(self):
        return [(False, False), (False, False)]

    def stop_best_focus_calculation(self):
        self.run_calculation = False

    def do_wise_calculation(self):
        self.output_data_best_focus = super(OWDetector, self).do_wise_calculation()

        return self.output_data_best_focus

    def do_focus_sweep_calculation(self):
        # Equivalent to Focal scan in the GUI
        try:
            if self.input_data is None:
                raise Exception("No Input Data!")

            if not self.output_data_best_focus:
                raise Exception("Run computation first!")

            sys.stdout = EmittingStream(textWritten=self.writeStdOut)

            # TODO: TO BE CHECKED THE EQUiVALENT OF THE OLD QUANTITY!!!!
            self.oe_f2 = self.output_data_best_focus.wise_beamline.get_wise_propagation_element(
                -1).PositioningDirectives.Distance

            self.check_fields()
            if self.defocus_start >= self.defocus_stop: raise Exception(
                "Defocus sweep start must be < Defocus sweep stop")
            self.defocus_step = congruence.checkStrictlyPositiveNumber(self.defocus_step, "Defocus sweep step")
            if self.defocus_step >= self.defocus_stop - self.defocus_start: raise Exception("Defocus step is too big")

            if self.best_focus_slider is None:
                self.best_focus_slider = QSlider(self.tab[1])
                self.best_focus_slider.setGeometry(QRect(0, 0, 320, 50))
                self.best_focus_slider.setMinimumHeight(30)
                self.best_focus_slider.setOrientation(Qt.Horizontal)
                self.best_focus_slider.setInvertedAppearance(False)
                self.best_focus_slider.setInvertedControls(False)

                self.tab[2].layout().addWidget(self.best_focus_slider)
            else:
                self.best_focus_slider.valueChanged.disconnect()

            self.setStatusMessage("")
            self.progressBarInit()

            self.defocus_list = numpy.arange(self.defocus_start * 1e-3,
                                             self.defocus_stop * 1e-3,
                                             self.defocus_step * 1e-3)

            n_defocus = len(self.defocus_list)

            if self.defocus_list[-1] != self.defocus_stop * 1e-3:
                n_defocus += 1
                self.defocus_list.resize(n_defocus)
                self.defocus_list[-1] = self.defocus_stop * 1e-3

            self.best_focus_slider.setTickInterval(1)
            self.best_focus_slider.setSingleStep(1)
            self.best_focus_slider.setMinimum(0)
            self.best_focus_slider.setMaximum(n_defocus - 1)
            self.best_focus_slider.setValue(0)

            progress_bar_increment = 100 / n_defocus

            n_pools = self.n_pools if self.use_multipool == 1 else 1

            hew_min = numpy.inf
            index_min_list = []

            self.best_focus_index = -1
            self.electric_fields_list = []
            self.positions_list = []
            self.hews_list = []
            self.sigmas_list = []

            import copy
            last_element = self.get_last_element()
            last_element = copy.deepcopy(last_element)

            self.setStatusMessage("Executing Foundation.FocusSweep()")

            self.run_calculation = True

            self.defocus_list[numpy.where(numpy.abs(self.defocus_list) < 1e-15)] = 0.0

            if self.show_animation == 1:
                for i, defocus in enumerate(self.defocus_list):
                    self.progressBarSet(int((i+1) * 1/len(self.defocus_list)* 100))
                    if not self.run_calculation:
                        if not self.best_focus_slider is None: self.best_focus_slider.valueChanged.connect(
                            self.plot_detail)
                        return

                    ResultList, HewList, SigmaList, More = Foundation.FocusSweep(last_element, [self.defocus_list[i]],
                                                                                 DetectorSize=self.length)

                    S = ResultList[0].S
                    E = ResultList[0].Field
                    I = abs(E) ** 2
                    norm = max(I)
                    norm = 1.0 if norm == 0.0 else norm
                    I = I / norm
                    HEW = HewList[0]
                    sigma0 = SigmaList[0]

                    # E1
                    self.electric_fields_list.append(E)
                    self.positions_list.append(S)
                    self.hews_list.append(HEW)
                    self.sigmas_list.append(sigma0)

                    self.best_focus_slider.setValue(i)

                    self.plot_histo(S * 1e6,
                                    I,
                                    i * progress_bar_increment,
                                    tabs_canvas_index=2,
                                    plot_canvas_index=2,
                                    title="Defocus Sweep: " + Units.SmartFormatter(self._defocus_sign * defocus, {'unit': 'm'}) + " (" + str(
                                        i + 1) + "/" + str(n_defocus) +
                                          "), HEW: " + Units.SmartFormatter(HEW, {'unit': 'm'}),
                                    xtitle="Y [" + u"\u03BC" + "m]",
                                    ytitle="Intensity",
                                    log_x=False,
                                    log_y=False)

                    self.tabs.setCurrentIndex(2)

                    hew = round(HEW * 1e6, 11)  # problems with double precision numbers: inconsistent comparisons

                    if hew < hew_min:
                        hew_min = hew
                        index_min_list = [i]
                    elif hew == hew_min:
                        index_min_list.append(i)
            else:  # NOT INTERACTIVE
                ResultList, HewList, SigmaList, More = Foundation.FocusSweep(last_element,
                                                                             self.defocus_list,
                                                                             DetectorSize=self.length)

                i = 0
                for Result, HEW, sigma0 in zip(ResultList, HewList, SigmaList):

                    self.electric_fields_list.append(Result.Field)
                    self.positions_list.append(Result.S)
                    self.hews_list.append(HEW)
                    self.sigmas_list.append(sigma0)

                    hew = round(HEW * 1e6, 11)  # problems with double precision numbers: inconsistent comparisons

                    if hew < hew_min:
                        hew_min = hew
                        index_min_list = [i]
                    elif hew == hew_min:
                        index_min_list.append(i)

                    i += 1

            index_min = index_min_list[
                int(len(index_min_list) / 2)]  # choosing the central value, when hew reach a pletau

            self.best_focus_index = index_min
            best_focus_electric_fields = self.electric_fields_list[index_min]
            best_focus_I = abs(best_focus_electric_fields) ** 2
            norm = max(best_focus_I)
            norm = 1.0 if norm == 0.0 else norm
            best_focus_I = best_focus_I / norm

            best_focus_positions = self.positions_list[index_min]
            self.ActualBestDefocus = self.get_ActualBestDefocus()
            self.ActualBestHew = self.get_ActualBestHew()

            QMessageBox.information(self,
                                    "Focal Scan calculation",
                                    "Best Focus Found!\n\nPosition: " + Units.SmartFormatter(self.oe_f2 + (
                                            self._defocus_sign *
                                            self.defocus_list[index_min]), {'unit': 'm'}) +
                                    "\nHEW: " + Units.SmartFormatter(self.hews_list[index_min], {'unit': 'm'}),
                                    QMessageBox.Ok)

            self.plot_histo(best_focus_positions * 1e6,
                            best_focus_I,
                            100,
                            tabs_canvas_index=2,
                            plot_canvas_index=2,
                            title="(BEST FOCUS) Defocus Sweep: " + Units.SmartFormatter(self._defocus_sign * self.defocus_list[index_min], {'unit': 'm'}) +
                                  " (" + str(index_min + 1) + "/" + str(n_defocus) + "), Position: " +
                                  Units.SmartFormatter(self.oe_f2 +
                                                       (self._defocus_sign * self.defocus_list[index_min]),
                                                       {'unit': 'm'}) + ", HEW: " +
                                  Units.SmartFormatter(self.ActualBestHew * 1e-6, {'unit': 'm'}),
                            xtitle="Y [" + u"\u03BC" + "m]",
                            ytitle="Intensity",
                            log_x=False,
                            log_y=False)

            self.plot_histo(self._defocus_sign * self.defocus_list * 1e3,
                            numpy.multiply(self.hews_list, 1e6),
                            100,
                            tabs_canvas_index=3,
                            plot_canvas_index=3,
                            title="HEW (blue) and SIGMA (red)",
                            xtitle="",
                            ytitle="",
                            log_x=False,
                            log_y=False)

            self.plot_canvas[3].addCurve(self._defocus_sign * self.defocus_list * 1e3,
                                         numpy.multiply(self.sigmas_list, 1e6),
                                         legend="HEW (blue) and SIGMA (red)",
                                         color='red',
                                         replace=False)

            self.plot_canvas[3].addCurve(self._defocus_sign * self.defocus_list * 1e3,
                                         numpy.multiply(self.hews_list, 1e6),
                                         color='blue',
                                         replace=False)

            # self.plot_histo(self._defocus_sign * self.defocus_list,
            #                 numpy.multiply(self.sigmas_list, 1e6),
            #                 100,
            #                 tabs_canvas_index=3,
            #                 plot_canvas_index=3,
            #                 title="SIGMA",
            #                 xtitle="",
            #                 ytitle="",
            #                 log_x=False,
            #                 log_y=False)

            self.plot_canvas[3].setDefaultPlotLines(True)
            self.plot_canvas[3].setDefaultPlotPoints(True)
            self.plot_canvas[3].setGraphXLabel("Defocus [mm]")
            self.plot_canvas[3].setGraphYLabel("Size [" + u"\u03BC" + "m]")

            self.best_focus_slider.setValue(index_min)

            self.tabs.setCurrentIndex(3 if self.show_animation == 1 else 2)
            self.setStatusMessage("")

            self.save_button.setEnabled(True)

        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            self.setStatusMessage("Error!")

            # raise exception

        if not self.best_focus_slider is None: self.best_focus_slider.valueChanged.connect(self.plot_detail)
        self.progressBarFinished()

    # Function below MUST be completed to account for all the particularities of FocusFind compared to FocusSweep
    def do_find_focus_calculation(self):
        try:
            if self.input_data is None:
                raise Exception("No Input Data!")

            if not self.output_data_best_focus:
                raise Exception("Run computation first!")

            sys.stdout = EmittingStream(textWritten=self.writeStdOut)

            self.oe_f2 = self.output_data_best_focus.wise_beamline.get_wise_propagation_element(-1).PositioningDirectives.Distance

            self.check_fields()
            if self.defocus_start >= self.defocus_stop: raise Exception("Defocus sweep start must be < Defocus sweep stop")
            self.defocus_step = congruence.checkStrictlyPositiveNumber(self. defocus_step, "Defocus sweep step")
            if self.defocus_step >= self.defocus_stop - self.defocus_start: raise Exception("Defocus step is too big")

            if self.best_focus_slider is None:
                self.best_focus_slider = QSlider(self.tab[1])
                self.best_focus_slider.setGeometry(QRect(0, 0, 320, 50))
                self.best_focus_slider.setMinimumHeight(30)
                self.best_focus_slider.setOrientation(Qt.Horizontal)
                self.best_focus_slider.setInvertedAppearance(False)
                self.best_focus_slider.setInvertedControls(False)

                self.tab[2].layout().addWidget(self.best_focus_slider)
            else:
                self.best_focus_slider.valueChanged.disconnect()

            self.setStatusMessage("")
            self.progressBarInit()

            progress_bar_increment = 100. / self.max_iter

            hew_min = numpy.inf
            index_min_list = []

            self.best_focus_index = -1
            self.electric_fields_list = []
            self.positions_list = []
            self.hews_list = []

            import copy
            last_element = self.get_last_element()
            last_element = copy.deepcopy(last_element)

            self.setStatusMessage("Executing Foundation.FocusFind()")

            self.run_calculation = True

            #   Results : struct-like class with the following attributes
            #   	- BestField : 1d-array (complex)
            #   				    Field at the best focus
            #       - BestDefocus : scalar (real)
            #                       Defocus of the best spot
	        #       - BestHew : scalar (real)
            #				        Half energy width of the best spot
            #       - OptResult : OptimizationResult object
            #                       Contains the results of the optimization

            Results = Foundation.FocusFind(last_element,
                                           DefocusRange=(self.defocus_start*1e-3, self.defocus_stop*1e-3),
                                           DetectorSize = self.length)

            self.progressBarSet(50)

            BestField = Results.BestField
            self.BestDefocus = Results.BestDefocus
            self.BestHew = Results.BestHew
            OptResult = Results.OptResult
            S = Results.S

            best_focus_I = numpy.abs(BestField)**2
            norm = max(best_focus_I)
            norm = 1.0 if norm == 0.0 else norm
            best_focus_I = best_focus_I/norm

            self.ActualBestHew = self.get_ActualBestHew()
            self.ActualBestDefocus = self.get_ActualBestDefocus()

            QMessageBox.information(self,
                                    "Best focus calculation",
                                    "Best Focus Found!\n\nPosition: " + Units.SmartFormatter(self.ActualBestDefocus, {'unit': 'm'}) +
                                    "\nHEW: " + Units.SmartFormatter(self.ActualBestHew * 1e-6, {'unit': 'm'}),
                                    QMessageBox.Ok
                                    )

            self.plot_histo(S * 1e6,
                            best_focus_I,
                            100,
                            tabs_canvas_index=2,
                            plot_canvas_index=2,
                            title="(BEST FOCUS) Position: " + Units.SmartFormatter(self.ActualBestDefocus, {'unit': 'm'}) +
                            ", HEW: " + Units.SmartFormatter(self.ActualBestHew * 1e-6, {'unit': 'm'}),
                            xtitle="Y [" + u"\u03BC" + "m]",
                            ytitle="Intensity",
                            log_x=False,
                            log_y=False)
            #
            # self.plot_histo(self._defocus_sign * self.defocus_list,
            #                 numpy.multiply(self.hews_list, 1e6),
            #                 100,
            #                 tabs_canvas_index=3,
            #                 plot_canvas_index=3,
            #                 title="HEW vs Defocus Sweep",
            #                 xtitle="",
            #                 ytitle="",
            #                 log_x=False,
            #                 log_y=False)
            #
            # self.plot_canvas[3].setDefaultPlotLines(True)
            # self.plot_canvas[3].setDefaultPlotPoints(True)
            # self.plot_canvas[3].setGraphXLabel("Defocus [mm]")
            # self.plot_canvas[3].setGraphYLabel("HEW [$\mu$m]")
            #
            # self.best_focus_slider.setValue(index_min)
            #
            self.tabs.setCurrentIndex(2)
            self.setStatusMessage("")

            self.save_button.setEnabled(True)

        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            self.setStatusMessage("Error!")

            #raise exception

        if not self.best_focus_slider is None: self.best_focus_slider.valueChanged.connect(self.plot_detail)
        self.progressBarFinished()

    def get_last_element(self):
        last_element = self.output_data_best_focus.wise_beamline.get_wise_propagation_element(-1)

        if isinstance(last_element.CoreOptics, Optics.Detector):
            return last_element.Parent
        else:
            return last_element

    def plot_detail(self, value):
        try:
            index = value
            n_defocus = len(self.positions_list)

            electric_fields = self.electric_fields_list[index]
            I = abs(electric_fields)**2
            norm = max(I)
            norm = 1.0 if norm == 0.0 else norm
            I = I/norm
            positions       = self.positions_list[index]

            if index == self.best_focus_index:
                title = "(BEST FOCUS) Defocus Sweep: " +\
                        Units.SmartFormatter(self._defocus_sign * self.defocus_list[index], {'unit': 'm'}) +\
                        " ("+ str(index+1) + "/" + str(n_defocus) + "), Position: " +\
                        Units.SmartFormatter(self.oe_f2 + self.defocus_list[index], {'unit': 'm'}) +\
                        ", HEW: " + Units.SmartFormatter(self.hews_list[index], {'unit': 'm'})
            else:
                title = "Defocus Sweep: " + Units.SmartFormatter(self._defocus_sign * self.defocus_list[index], {'unit': 'm'}) +\
                        " (" + str(index+1) + "/" + str(n_defocus) + "), HEW: " + Units.SmartFormatter(self.hews_list[index], {'unit': 'm'})


            self.plot_histo(positions * 1e6,
                            I,
                            100,
                            tabs_canvas_index=2,
                            plot_canvas_index=2,
                            title=title,
                            xtitle="Y [" + u"\u03BC" + "m]",
                            ytitle="Intensity",
                            log_x=False,
                            log_y=False)

            self.tabs.setCurrentIndex(2)
        except:
            pass

    def save_best_focus_results(self):
        try:
            path_dir = QFileDialog.getExistingDirectory(self, "Select destination directory", ".", QFileDialog.ShowDirsOnly)

            if not path_dir is None:
                if not path_dir.strip() == "":
                    if QMessageBox.question(self,
                                            "Save Data",
                                            "Data will be saved in :\n\n" + path_dir + "\n\nConfirm?",
                                            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                        for index in range(0, len(self.electric_fields_list)):
                            file_name = "best_focus_partial_result_" + str(index) + ".dat"

                            file = open(path_dir + "/" + file_name, "w")

                            intensities = abs(self.electric_fields_list[index])**2
                            norm = max(intensities)
                            norm = 1.0 if norm == 0.0 else norm
                            intensities = intensities/norm

                            file.write("# Defocus Sweep: " + str(self.defocus_list[index]) + " [m]\n")
                            file.write("# HEW          : " + str(self.hews_list[index]) + " [m]\n")
                            file.write("# Position [m]  Intensity\n")

                            for i in range (0, len(self.positions_list[index])):
                                file.write(str(self.positions_list[index][i]) + " " + str(intensities[i]) + "\n")


                            file.close()

                        QMessageBox.information(self,
                                                "Best Focus Calculation",
                                                "Best Focus Calculation complete results saved on directory:\n\n" + path_dir,
                                                QMessageBox.Ok
                                                )

        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            self.setStatusMessage("Error!")

from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWDetector()
    ow.show()
    a.exec_()
    ow.saveSettings()