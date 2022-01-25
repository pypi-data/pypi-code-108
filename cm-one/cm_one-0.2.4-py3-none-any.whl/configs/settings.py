from tkinter import *
from glob import glob
import sys, os
from PIL import Image
from PIL import ImageTk


class Settings:
    ''' Модуль для всех настроек терминала '''
    version = '0.2.4'

    def __init__(self, root, dirpath, mirrored=False):
        self.project_name = 'Gravity interface'
        # SCREEN SIZES#
        self.screenwidth = root.winfo_screenwidth()
        w = self.screenwidth
        self.screenheight = root.winfo_screenheight()
        h = self.screenheight
        self.screensize = (self.screenwidth, self.screenheight)
        self.screencenter = (self.screenwidth / 2, self.screenheight / 2)
        self.w = w
        self.h = h
        self.exit_gate = 'exit_gate_arrow'
        self.entry_gate = 'entry_gate_arrow'
        self.orup_enter_comm = 'orup_extended'
        self.orup_exit_comm = 'orup_short'
        self.mirrored = False
        if mirrored:
            self.mirrored = True

        # GATEICONS#
        self.bw = 1320
        self.bh = 653
        self.bwS = 450
        self.bhS = 600
        self.weight_show_posses = (w / 1.92, h / 1.0924608819345663)

        # DIRPATHS#
        self.rootdir = dirpath
        if self.w == 1366:
            self.imgsysdir = os.path.join(dirpath, 'imgs1366') + os.sep
        else:
            self.imgsysdir = os.path.join(dirpath, 'imgs') + os.sep

        self.settingsfile = os.path.join(dirpath, 'settings.py')

        self.slideanimpath = os.path.join(dirpath, 'slideanim')
        self.mainscreenpath = r'%s\imgs\mainscreen.png' % dirpath
        # SCREENS#
        self.shadow = ('shadow.png', w / 2, h / 2,
                       PhotoImage(file=self.imgsysdir + 'shadow.png'))
        self.accessscreen = [('access.png', 1600, 900)]
        self.toolbar = ('toolbar.png', self.w / 19.104895, self.h / 2.0026,
                        PhotoImage(file=self.imgsysdir + 'toolbar.png'))
        self.road = ('road.png', w / 2, h / 1.1327767780760494,
                     PhotoImage(file=self.imgsysdir + 'road.png'))
        self.order = ('order', w / 4.599326, h / 3.09054,
                      PhotoImage(file=self.imgsysdir + 'order.png'))
        self.currentEvents = ('order', w / 1.504405, h / 3.090543,
                              PhotoImage(
                                  file=self.imgsysdir + 'currentEvents.png'))
        # self.auth_logo = ('auth_logo',w/2,h/2,
        #	PhotoImage(file=self.imgsysdir + 'auth_logo.png'))
        self.statisticwin = ('statisticwin', w / 1.9, h / 2,
                             PhotoImage(
                                 file=self.imgsysdir + 'statisticwin.png'))
        self.orupWinUs = ('orupwinus', w / 1.9486447931526392, h / 2,
                          PhotoImage(file=self.imgsysdir + 'orupwinus.png'))
        self.record_change_win = (
        'record_change_win', w / 1.9486447931526392, h / 2,
        PhotoImage(file=self.imgsysdir + 'record_change_win.png'))
        self.orupWinEx = ('orupwinex', w / 2, h / 2,
                          PhotoImage(file=self.imgsysdir + 'orupwinex.png'))
        self.redbg = ('redbg', w / 1.9486447931526392, h / 1.20,
                      PhotoImage(file=self.imgsysdir + 'redbg.png'))
        self.redbgEx = ('redbgEx', w / 2, h / 1.35,
                        PhotoImage(file=self.imgsysdir + 'redbgOrupEx.png'))

        # OTHER OBJECTS#КЧ
        self.car_in_icon = ('car_in', w / 2, h / 2,
                            PhotoImage(file=self.imgsysdir + 'car_in.png'))
        self.car_out_icon = ('car_out', w / 2, h / 2,
                             PhotoImage(file=self.imgsysdir + 'car_out.png'))
        if not self.mirrored:
            self.exit_gate_arrow = (
            'exit_gate_arrow', w / 2.7007163323782233, h / 1.235,
            PhotoImage(file=self.imgsysdir + 'gate_arrow.png'))
            self.entry_gate_arrow = (
            'entry_gate_arrow', w / 1.4737712519319939, h / 1.235,
            PhotoImage(file=self.imgsysdir + 'gate_arrow.png'))
            orupAct = 'self.orupAct(call_method="manual")'
            orupActExit = 'self.orupActExit(call_method="manual")'
        else:
            self.entry_gate_arrow = (
            'exit_gate_arrow', w / 2.7007163323782233, h / 1.235,
            PhotoImage(file=self.imgsysdir + 'gate_arrow.png'))
            self.exit_gate_arrow = (
            'entry_gate_arrow', w / 1.4737712519319939, h / 1.235,
            PhotoImage(file=self.imgsysdir + 'gate_arrow.png'))
            orupActExit = 'self.orupAct(call_method="manual")'
            orupAct = 'self.orupActExit(call_method="manual")'
        self.exitwin = ('chatwin', w / 2, self.h / 2,
                        PhotoImage(file=self.imgsysdir + 'exitwin.png'))
        self.logo = ('logo', w / 2, h / 2.8,
                     PhotoImage(file=self.imgsysdir + 'logo.png'))
        self.sysNot = ('sysNot', w / 1.9, h / 2,
                       PhotoImage(file=self.imgsysdir + 'sysnotwin.png'))
        self.login = ('login', w / 2, h / 2,
                      PhotoImage(file=self.imgsysdir + 'login.png'))
        self.password = ('password', w / 2, h / 1.63,
                         PhotoImage(file=self.imgsysdir + 'pw.png'))
        self.ensureCloseRec = ('ensureCloseRec', w / 2, self.h / 2,
                               PhotoImage(
                                   file=self.imgsysdir + 'ensureCloseRec.png'))
        self.pw = (w / 2, h / 2.8, Entry(root, bd=5, width=20, show="*"))
        self.picker = PhotoImage(file=self.imgsysdir + 'picker.png')
        self.start_background = ('start_background', w / 2, h / 2,
                                 PhotoImage(
                                     file=self.imgsysdir + 'loadingWin.png'))

        self.notifIconAlert = (
        'notifAlert.png', w / 18.871, h / 1.6781, 'operator.sysNot.openWin()',
        PhotoImage(file=self.imgsysdir + 'sysnotAlert.png'), 25, 25,
        'toolbarBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'sysnotAlertZ.png'))

        # BUTTONS#
        self.abort_round =[(
        'abortRound.png', w / 4.6, h / 1.9, 'operator.ar_qdk.abort_round()',
        PhotoImage(file=self.imgsysdir + 'abortRound.png'), 25, 25,
        'toolbarBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'abortRoundZ.png'))]
        self.abort_round_unactive =[(
        'abortRoundUnactive.png', w / 4.6, h / 1.9, ...,
        PhotoImage(file=self.imgsysdir + 'abortRoundUnactive.png'), 25, 25,
        'toolbarBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'abortRoundUnactive.png'))]
        self.mainLogoBtn = (
        'mainL.png', w / 19.0609, h / 2.5282, 'operator.mainPage.openWin()',
        PhotoImage(file=self.imgsysdir + 'mainL.png'), 25, 25,
        'toolbarBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'mainLZ.png'))
        self.exitBtn = (
        'exit.png', w / 1.02429, h / 19.893796, 'self.drawExitWin'
                                                '()',
        PhotoImage(file=self.imgsysdir + 'exit.png'), 25, 25,
        'onGreyBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'exitZ.png'))
        self.exitBtnAuth = (
        'exit.png', w / 1.02429, h / 19.893796, 'self.drawExitWin'
                                                '()',
        PhotoImage(file=self.imgsysdir + 'exit.png'), 25, 25,
        'authWinBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'exitZ.png'))
        self.lockBtn = (
        'lock.png', w / 1.068, h / 19.893796, 'operator.authWin.openWin()',
        PhotoImage(file=self.imgsysdir + 'lock.png'), 25, 25,
        'onGreyBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'lockZ.png'))
        self.minimize_btn = (
        'minimize.png', w / 1.0459778, h / 18.073796, 'self.minimize_window()',
        PhotoImage(file=self.imgsysdir + 'minimize.png'), 25, 25,
        'onGreyBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'minimizeZ.png'))
        self.statisticBtn = ('statistic.png', w / 18.9669, h / 2.01619,
                             'operator.statPage.openWin()',
                             PhotoImage(file=self.imgsysdir + 'statistic.png'),
                             25, 25, 'toolbarBtn.TButton',
                             PhotoImage(
                                 file=self.imgsysdir + 'statisticZ.png'))
        self.notifBtn = (
        'notifUs', w / 18.871, h / 1.6781, 'operator.sysNot.openWin()',
        PhotoImage(file=self.imgsysdir + 'sysnot.png'), 25, 25,
        'toolbarBtn.TButton',
        PhotoImage(file=self.imgsysdir + 'sysnotZ.png'))

        self.toolBarBtns = [
            self.mainLogoBtn,
            self.statisticBtn,
            self.notifBtn,
        ]
        self.statBtns = [
            ('Ок', w / 1.12, h / 4.91, 'operator.statPage.get_history()',
             PhotoImage(file=self.imgsysdir + 'ok.png'), 25, 25,
             "toolbarBtn.TButton",
             PhotoImage(file=self.imgsysdir + 'okZ.png')),
            (
            'Сбросить', w / 1.12, h / 3.78, 'operator.statPage.abortFiltres()',
            PhotoImage(file=self.imgsysdir + 'abortFiltres.png'), 25, 25,
            "toolbarBtn.TButton",
            PhotoImage(file=self.imgsysdir + 'abortFiltresZ.png'))]
        # ('Выбрать',w/3.7,h/3.5,'operator.mailroom.upLowNow()',
        # hotoImage(file=self.imgsysdir + 'choose.png'),25,25),]

        self.orupEnterBtns = [
            ('accept.png', w / 1.6032, h / 1.35,
             'self.initOrupAct()',
             PhotoImage(file=self.imgsysdir + 'accept.png'), 100, 25,
             "onORUPbtn.TButton",
             PhotoImage(file= self.imgsysdir + 'acceptZ.png')),
            ('abort.png', w / 2.4927, h / 1.35,
             'self.destroyORUP(mode="decline")',
             PhotoImage(file=self.imgsysdir + 'abort.png'), 100, 25,
             "onORUPbtn.TButton",
             PhotoImage(file=self.imgsysdir + 'abortZ.png'))]
        self.orupExitBtns = [('newcar.png', w / 1.55, h / 2.325,
                              'self.big_orup_exit()',
                              PhotoImage(file=self.imgsysdir + 'newCar.png'),
                              40, 25, "onORUPbtn.TButton"),
                             ('accept.png', w / 1.7, h / 1.6,
                              'self.launchExitProtocol()',
                              PhotoImage(file=self.imgsysdir + 'accept.png'),
                              80, 25, "onORUPbtn.TButton",
                              PhotoImage(file=self.imgsysdir + 'acceptZ.png')),
                             ('abort.png', w / 2.45, h / 1.6,
                              'self.destroyORUP(mode="decline")',
                              PhotoImage(file=self.imgsysdir + 'abort.png'),
                              80, 25, "onORUPbtn.TButton",
                              PhotoImage(file=self.imgsysdir + 'abortZ.png'))]
        self.yesCloseAppBtn = [('yes.png', w / 2.3, h / 1.85,
                                'operator.closeApp()',
                                PhotoImage(file=self.imgsysdir + 'yes.png'),
                                40, 25, "onORUPbtn.TButton",
                                PhotoImage(file=self.imgsysdir + 'yesZ.png'))]
        self.yesCloseRecBtn = [('yes.png', w / 2.3, h / 1.85,
                                'operator.close_record(self.record_id)',
                                PhotoImage(file=self.imgsysdir + 'yes.png'),
                                40, 25, "onORUPbtn.TButton",
                                PhotoImage(file=self.imgsysdir + 'yesZ.png'))]
        self.manual_control_info_bar = (
        'manual_control_info_bar.png', w / 1.85, h / 2.5,
        PhotoImage(file=self.imgsysdir + 'manual_control_info_bar.png'))
        self.manual_gate_control_btn = [
            ('open.png', w / 9, h / 1.0477489768076398,
             'operator.manual_gate_control.openWin()',
             PhotoImage(file=self.imgsysdir + 'manual_gate_control.png'), 150,
             25,
             "onGreyBtn.TButton",
             PhotoImage(file=self.imgsysdir + 'manual_gate_controlZ.png'))]

        # Содержит позиции кнопок ручного открытия-закрытия шлагбаумов для режима зеркало (True) и обычного (False)
        self.manual_btn_coords = {True: {
            'internal_open': (w / 1.4342454728370221, h / 1.0477489768076398),
            'external_open': (w / 3.17949260042283, h / 1.0477489768076398),
            'internal_close': (w / 1.264245472837022, h / 1.0477489768076398),
            'external_close': (w / 4.547949260042283, h / 1.0477489768076398)},

                                  False: {'external_open': (
                                  w / 1.4342454728370221,
                                  h / 1.0477489768076398),
                                          'internal_open': (
                                          w / 3.17949260042283,
                                          h / 1.0477489768076398),
                                          'external_close': (
                                          w / 1.264245472837022,
                                          h / 1.0477489768076398),
                                          'internal_close': (
                                          w / 4.547949260042283,
                                          h / 1.0477489768076398)}}

        self.manual_open_internal_gate_btn = [('open.png',
                                               self.manual_btn_coords[
                                                   self.mirrored][
                                                   'internal_open'][0],
                                               self.manual_btn_coords[
                                                   self.mirrored][
                                                   'internal_open'][1],
                                               'operator.open_exit_gate()',
                                               PhotoImage(
                                                   file=self.imgsysdir + 'open.png'),
                                               60, 25,
                                               'onGreyBtn.TButton',
                                               PhotoImage(
                                                   file=self.imgsysdir + 'openZ.png'))]
        self.manual_close_internal_gate_btn = [('close.png',
                                                self.manual_btn_coords[
                                                    self.mirrored][
                                                    'internal_close'][0],
                                                self.manual_btn_coords[
                                                    self.mirrored][
                                                    'internal_close'][1],
                                                'operator.close_exit_gate()',
                                                PhotoImage(
                                                    file=self.imgsysdir + 'close.png'),
                                                60, 25,
                                                'onGreyBtn.TButton',
                                                PhotoImage(
                                                    file=self.imgsysdir + 'closeZ.png'))]
        self.manual_open_external_gate_btn = [('open.png',
                                               self.manual_btn_coords[
                                                   self.mirrored][
                                                   'external_open'][0],
                                               self.manual_btn_coords[
                                                   self.mirrored][
                                                   'external_open'][1],
                                               'operator.open_entry_gate()',
                                               PhotoImage(
                                                   file=self.imgsysdir + 'open.png'),
                                               60, 25,
                                               'onGreyBtn.TButton',
                                               PhotoImage(
                                                   file=self.imgsysdir + 'openZ.png'))]
        self.manual_close_external_gate_btn = [('close.png',
                                                self.manual_btn_coords[
                                                    self.mirrored][
                                                    'external_close'][0],
                                                self.manual_btn_coords[
                                                    self.mirrored][
                                                    'external_close'][1],
                                                'operator.close_entry_gate()',
                                                PhotoImage(
                                                    file=self.imgsysdir + 'close.png'),
                                                60, 25,
                                                'onGreyBtn.TButton',
                                                PhotoImage(
                                                    file=self.imgsysdir + 'closeZ.png'))]

        self.auto_gate_control_btn = [
            ('auto_gate_control', w / 13.9, h / 1.0477489768076398,
             'operator.mainPage.openWin()',
             PhotoImage(file=self.imgsysdir + 'auto_gate_control.png'), 150,
             25,
             "onGreyBtn.TButton",
             PhotoImage(file=self.imgsysdir + 'auto_gate_controlZ.png'))]
        self.record_change_btns = [
            ('change.png', w / 1.6032, h / 1.4, 'self.change_record()',
             PhotoImage(file=self.imgsysdir + 'change.png'), 100, 25,
             "onORUPbtn.TButton",
             PhotoImage(file=self.imgsysdir + 'changeZ.png')),

            ('cancel.png', self.w / 2.4927, self.h / 1.4,
             'self.destroyORUP(mode="decline")',
             PhotoImage(file=self.imgsysdir + 'cancel.png'), 100, 25,
             "onORUPbtn.TButton",
             PhotoImage(file=self.imgsysdir + 'cancelZ.png'))]
        self.noCloseBlockImg = [('no.png', w / 1.75, h / 1.85,
                                 'self.destroyBlockImg(mode="total")',
                                 PhotoImage(file=self.imgsysdir + 'no.png'),
                                 40, 25, "onORUPbtn.TButton",
                                 PhotoImage(file=self.imgsysdir + 'noZ.png'))]
        self.exitBtns = self.yesCloseAppBtn + self.noCloseBlockImg
        self.closeRecBtns = self.yesCloseRecBtn + self.noCloseBlockImg
        self.entry_gate_base = (
        'gate_base.png', w / 2.8402366863905324, h / 1.1560981160512434,
        PhotoImage(file=self.imgsysdir + 'gate_base.png'))
        self.exit_gate_base = (
        'gate_base.png', w / 1.5106215578284816, h / 1.1560981160512434,
        PhotoImage(file=self.imgsysdir + 'gate_base.png'))
        self.gateBtns = [
            ('open_internal.png', w / 3.17949260042283, h / 1.0477489768076398,
             orupActExit,
             PhotoImage(file=self.imgsysdir + 'open.png'), 60, 25,
             'onGreyBtn.TButton',
             PhotoImage(file=self.imgsysdir + 'openZ.png')),
            ('open_external.png', w / 1.4342454728370221,
             h / 1.0477489768076398, orupAct,
             PhotoImage(file=self.imgsysdir + 'open.png'), 60, 25,
             'onGreyBtn.TButton',
             PhotoImage(file=self.imgsysdir + 'openZ.png'))]
        self.authBtns = [
            self.exitBtnAuth,
            self.minimize_btn,
            ('enter.png', w / 2, h / 1.40, 'self.send_auth_command()',
             PhotoImage(file=self.imgsysdir + 'enter.png'), 25, 25,
             'authWinBtn.TButton',
             PhotoImage(file=self.imgsysdir + 'enterZ.png'))]
        self.blockWinBtns = [('close.png',
                              PhotoImage(file=self.imgsysdir + 'close.png'),
                              self.bw / 2,
                              self.bh / 1.1, 'operator.destroyBlockWin()')]
        self.closeAuto = [('close.png',
                           PhotoImage(file=self.imgsysdir + 'close.png'),
                           self.bw / 2,
                           self.bh / 1.1,
                           'operator.lateCars.drawConfirmWin()')]

        self.addComm = ('addComm', self.w / 2, self.h / 2.05,
                        PhotoImage(file=self.imgsysdir + 'addComm.png'))
        self.addCommAccept = ('accept.png', self.w / 1.71, self.h / 1.6,
                              'self.add_comm()',
                              PhotoImage(file=self.imgsysdir + 'accept.png'),
                              80, 25,
                              "onORUPbtn.TButton",
                              PhotoImage(file=self.imgsysdir + 'acceptZ.png'))
        self.addCommAbort = ('cancel.png', self.w / 2.41, self.h / 1.6,
                             'self.destroyBlockImg(mode="total")',
                             PhotoImage(file=self.imgsysdir + 'cancel.png'),
                             80, 25, "onORUPbtn.TButton",
                             PhotoImage(file=self.imgsysdir + 'cancelZ.png'))
        self.addCommBtns = [self.addCommAccept, self.addCommAbort]

        self.lateConfirmBtns = [('yes.png', w / 2.3, h / 1.85,
                                 'operator.closeAuto()',
                                 PhotoImage(file=self.imgsysdir + 'yes.png'),
                                 40, 25),
                                ('no.png', w / 1.75, h / 1.85,
                                 'operator.lateCars.destroyBlockImg(mode="total"")',
                                 PhotoImage(file=self.imgsysdir + 'no.png'),
                                 40, 25)]
        self.blockWinBtnsS = [('close.png',
                               PhotoImage(file=self.imgsysdir + 'close.png'),
                               self.bwS / 2,
                               self.bhS / 1.1, 'operator.destroyBlockWin()')]
        self.entry = [('entry.png', w / 3.879, h / 3.303, '...')]
        self.copybtn = [('copy.png', w / 1.707, h / 1.407,
                         'operator.current.admincopy()')]
        self.copyherebtn = [('copyhere.png', w / 1.347, h / 1.407,
                             'operator.current.determine_dway("admin")')]
        # List generators for ojects #

        self.slanimimgs = [PhotoImage(file=x) for x in
                           glob(self.slideanimpath + '//*')]
        self.clomimgs = [PhotoImage(file=x) for x in
                         glob(self.slideanimpath + '//*')]

        # Данные для рисовки мультика
        self.right_pos = self.w / 1.34581, self.h / 1.29729
        self.center_pos = self.w / 2.25, self.h / 1.4014
        self.left_pos = self.w / 5.4859, self.h / 1.29729
        self.car_poses = {'r': self.right_pos, 'c': self.center_pos,
                          'l': self.left_pos}
        self.car_face_info = {'enter': 'car_out_icon', 'exit': 'car_in_icon'}

    def getImgPath(self, rootdir, imgname):
        dir = os.path.join(rootdir, imgname)
        ph = os.path.join(dir, imgname)
        return ph
