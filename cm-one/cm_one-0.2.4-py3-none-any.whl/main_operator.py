import _tkinter

from cm.modules import *
import threading
import pickle
from time import sleep
from cm.wlistener import WListener
from cm.configs import config as s
from traceback import format_exc
from cm.styles import fonts
from ar_qdk.main import ARQDK
from cm.gcore_interaction import db_functions as db_funcs
from orup_errors.main import OrupErrorsManager
import sys
from qpi.main import QPI


class Operator:
    """ Основной оператор взaимодействия между окнами, его экземляр распределяется
	между всеми модулями и используются для их взаимной обработки """

    def __init__(self, root, settings, scale, can, deffaultScreenSize,
                 loadingcan, ar_ip, ar_port=52250):
        self.root = root
        self.currentPage = None
        self.status_ready = False
        self.current = 'main'
        self.unfinished_records = []
        self.loadingcan = loadingcan
        self.loading_repcentage = 0
        self.deffaultScreenSize = deffaultScreenSize
        self.current = 'main'
        self.settings = settings
        self.smlist = ['0', ]
        self.ar_ip = ar_ip
        self.ar_qdk = ARQDK(ar_ip, int(ar_port))
        while True:
            try:
                self.ar_qdk.make_connection()
                self.loadingcan.delete('no_connection_info')
                break
            except ConnectionRefusedError:
                self.no_ar_connection()
                sleep(3)
        self.general_tables_dict = {}
        self.get_wdb_tables_info()

        self.terminal = Terminal(root, settings, self, can)
        self.terminal.launchingOperations()
        self.main_btns_drawn = False
        self.exitFlag = False
        self.road_anim_info = {self.settings.exit_gate: {'pos': 0, 'img': ...,
                                                         'busy': False},
                               self.settings.entry_gate: {'pos': 0, 'img': ...,
                                                          'busy': False},
                               'active': False}
        self.animation = 'off'

        self.scale = scale
        self.wr = WListener(ip=s.wrip, port=s.wrport, ar_ip=self.ar_ip)
        self.aborted = False
        self.userRole = 'moder'

        ###################### PAGES ###################################
        self.authWin = AuthWin(root, settings, self, can)
        self.mainPage = MainPage(root, settings, self, can)
        self.statPage = Statistic(root, settings, self, can)
        self.sysNot = SysNot(root, settings, self, can)
        self.manual_gate_control = ManualGateControl(root, settings, self, can)
        #########################LAUNCHING##############################
        self.authWin.openWin()

        scale_thread = threading.Thread(target=self.wr.scale_reciever,
                         args=(ar_ip,))
        scale_thread.daemon = True
        scale_thread.start() # Запуск сервера для получения данных о сервере
        threading.Thread(target=self.scaleRecieving,
                         args=()).start()  # Запуск демона для обработки показания весов
        threading.Thread(target=self.ar_reciever_thread, args=()).start()
        # Данные для рисования грузовика на весовой платформе
        self.orup_error_manager = OrupErrorsManager(canvas=self.terminal.can,
                                                    types_list=self.get_trash_types_reprs(),
                                                    cats_list=self.get_trash_cats_reprs(),
                                                    text_color=cs.orup_error_txt_color,
                                                    debtors_list=[],
                                                    carriers_list=self.get_clients_reprs())
        self.gcore_status = True
        self.create_qpi()


    def create_qpi(self):
        self.qpi = QPI('0.0.0.0', 50505, without_auth=True,
                       mark_disconnect=False,
                       core=self, auto_start=False)
        qpi_thread = threading.Thread(target=self.qpi.launch_mainloop)
        qpi_thread.daemon = True
        qpi_thread.start()


    def get_api_support_methods(self):
        methods = {'zoom_app': {'method': self.terminal.set_window_normal}}
        return methods

    def scaleRecieving(self):
        '''Добавляет данные из сервера принятия весов в список для дальнейшей обработки'''
        while True:
            data = self.wr.wlisten_tcp()
            self.smlist.append(data)
            sleep(1)
            self.smlist = self.smlist[15:]

    def getToolBarBtns(self):
        '''Получить кнопки тул-бара'''
        toolBarBtns = self.settings.toolBarBtns
        return toolBarBtns

    def recieve_ar_responses(self):
        response = self.ar_qdk.get_data()
        if not response:
            return response
        print("AR_SIGNALL:", response)
        try:
            core_method = response['core_method']
            method_result = response['info']
            return core_method, method_result
        except KeyError:
            print(format_exc())
            pass

    def closeApp(self):
        """ Функция выполняющая завершающие операции, при закрытии программы """
        self.ar_qdk.capture_cm_terminated()
        self.ar_qdk.restart_unit()
        self.root.destroy()
        sleep(5)
        sys.exit(0)

    def ar_reciever_thread(self):
        while True:
            response = self.recieve_ar_responses()
            if not response:
                break
            else:
                core_method, method_result = response
                self.operate_ar_response(core_method, method_result)


    def operate_ar_response(self, core_method, method_result):
        if core_method == 'get_unfinished_records':
            if method_result['status'] == 'success':
                self.operate_get_unfinished_records(method_result['info'])
            else:
                self.mainPage.tar.clearTree()
        if core_method == 'update_round_status':
            self.update_status_operate(method_result)
        if core_method == 'update_round_status':
            self.update_status_operate(method_result)
        elif core_method == 'get_last_event' and method_result[
            'status'] == 'success':
            self.operate_last_event(**method_result['info'][0])
        elif core_method == 'faultDetected':
            self.terminal.errors += [{'level1': method_result['info']}]
        elif core_method == 'try_auth_user' and \
                method_result['status'] == 'success':
            self.try_login(method_result['info'][0]['auth_status'],
                           method_result['info'][0]['id'])
        elif core_method == 'get_history':
            self.operate_get_history(method_result['status'],
                                     method_result['info'])
        elif core_method == 'get_table_info':
            self.operate_table_info(s.tables_info, self.general_tables_dict,
                                    method_result['tablename'],
                                    method_result['info'])
        elif core_method == 'update_gate_status':
            self.operate_gate_changes_command(**method_result)
        elif core_method == 'car_detected' and self.ifORUPcanAppear():
            self.car_detected_operate(auto_id=method_result['auto_id'],
                                      client_id=method_result['last_carrier'],
                                      trash_cat_id=method_result[
                                          'last_trash_cat'],
                                      trash_type_id=method_result[
                                          'last_trash_type'],
                                      course=method_result['course'],
                                      have_gross=method_result['have_gross'],
                                      car_protocol=method_result[
                                          'car_protocol'],
                                      polygon=method_result['last_polygon'])
        elif core_method == 'get_health_monitor':
            self.operate_get_health_monitor(method_result)
        elif core_method == 'get_status':
            self.operate_get_status(method_result)

    def operate_get_status(self, status, *args, **kwargs):
        """ Получить статус GCore"""
        self.gcore_status = status

    def operate_get_health_monitor(self, health_monitor: dict, *args,
                                   **kwargs):
        """ От GCore пришел словарь, содержащий информацию типа health_monitor"""
        self.terminal.check_gcore_health(health_monitor)
        self.sysNot.tar.fillTree(health_monitor)

    def operate_last_event(self, trash_cat, trash_type, carrier, *args,
                           **kwargs):
        """ От GCore пришла информация о последнем заезде авто """
        carrier = self.get_client_repr(carrier)
        trash_cat = self.get_trash_cat_repr(trash_cat)
        trash_type = self.get_trash_type_repr(trash_type)

        self.currentPage.contragentCombo.set(self.validate_last_event(carrier))
        self.currentPage.trashCatOm.set(self.validate_last_event(trash_cat))
        self.currentPage.trashTypeOm.set(self.validate_last_event(trash_type))

    def validate_last_event(self, num):
        if num:
            return num
        else: return 0

    def operate_gate_changes_command(self, gate_name, status, *args, **kwargs):
        """ Обработчик команды от GCore об изменении положении стрелы шлагбаума """
        if gate_name == 'entry' and status == 'open':
            print('Внешний открывается')
            self.terminal.open_entry_gate_operation_start()
        elif gate_name == 'entry' and status == 'close':
            print('Внешний закрывается')
            self.terminal.close_entry_gate_operation_start()
        elif gate_name == 'exit' and status == 'open':
            print('Внутренний открывается')
            self.terminal.open_exit_gate_operation_start()
        elif gate_name == 'exit' and status == 'close':
            print('Внутренний закрывается')
            self.terminal.close_exit_gate_operation_start()

    def operate_table_info(self, tables_info, general_tables_dict, tablename,
                           result, *args, **kwargs):
        """ Когда пришли данные от GCore о содержимом таблицы tablename """
        # Получаем репрезентативное значние
        repr_value = tables_info[tablename]['repr']
        # Отформатировать данные, что бы получить данные типа {'repr':{col1:'val1'}, 'repr':{'col2': val2}}
        formated = self.format_wdb_table_info(result, keyname=repr_value)
        # Добавить в словарь, содержащие содержимое всех таблиц инфу вида {'tablename': {repr: {...}, repr: {...} }}
        general_tables_dict[tablename] = formated
        print("GENERAL TABLES DICT", general_tables_dict)
        self.create_loading_info(tablename, self.loadingcan)

    def create_loading_info(self, tablename, loadingcan):
        try:
            loadingcan.delete('loading_status')
            self.loading_repcentage += 100 / len(s.tables_info.keys())
            loading_percentage = str(int(self.loading_repcentage)) + '%'
            loadingcan.create_text(self.root.winfo_screenwidth() / 2,
                                   self.root.winfo_screenheight() / 2 * 1.32,
                                   text=s.tables_info[tablename][
                                       'loading_description'],
                                   font=fonts.loading_status_font,
                                   fill='white',
                                   tags=('loading_info', 'loading_status'))
            loadingcan.create_text(self.root.winfo_screenwidth() / 2,
                                   self.root.winfo_screenheight() / 2,
                                   text=loading_percentage,
                                   font=fonts.loading_percents_font,
                                   fill='white',
                                   tags=('loading_info', 'loading_status'))
        except _tkinter.TclError:
            pass


    def format_wdb_table_info(self, result: list, keyname: str, *args,
                              **kwargs):
        """ Создаем словарь, где ключом будет keyname записи, а значением - вся информация по записи
        (тоже в виде словаря)"""
        formated = {}
        for record in result:
            key = record[keyname]
            formated[key] = record
        return formated

    def operate_get_unfinished_records(self, info, *args, **kwargs):
        self.mainPage.tar.clearTree()
        try:
            self.unfinished_records = info
            self.fill_current_treeview(info)
            self.currentPage.tar.sortId(self.currentPage.tree, '#0', reverse=True)
        except:
            format_exc()

    def fill_current_treeview(self, info):
        for rec in info:
            rec['trash_cat'] = self.get_trash_cat_repr(rec['trash_cat'])
            self.mainPage.tar.fillTree(id=rec['id'], brutto=rec['brutto'],
                                       tara=rec['tara'], cargo=rec['cargo'],
                                       time_in=rec['time_in'],
                                       trash_cat=rec['trash_cat'],
                                       car_number=rec['car_number'],
                                       notes=rec['notes'])

    def operate_get_history(self, status, records):
        """ От GCore пришел список, содержащий информацию обо всех заездов за запрашиваемый период в виде словарей """
        self.statPage.tar.clearTree()
        self.statPage.weight_sum = 0
        self.statPage.records_amount = 0
        if status == 'success':
            self.statPage.records_amount = len(records)
            for record in records:
                self.statPage.tar.insertRec(id=record['record_id'],
                                            car_number=record['car_number'],
                                            carrier=self.get_client_repr(
                                                record.pop('carrier')),
                                            brutto=record['brutto'],
                                            tara=record['tara'],
                                            cargo=record['cargo'],
                                            trash_cat=self.get_trash_cat_repr(
                                                record.pop('trash_cat')),
                                            trash_type=self.get_trash_type_repr(
                                                record.pop('trash_type')),
                                            auto=self.get_auto_repr(
                                                record.pop('auto')),
                                            time_in=record['time_in'],
                                            time_out=record['time_out'],
                                            notes=record['notes'],
                                            alerts=record['alerts'])
                if record['cargo']:
                    self.statPage.weight_sum += record['cargo']
        try:
            self.currentPage.tar.sortId(self.currentPage.tree, '#0', reverse=True)
        except:
            pass
        # Разместить итоговую информацию (общий тоннаж и количество взвешиваний)
        self.statPage.place_amount_info(self.statPage.weight_sum,
                                        self.statPage.records_amount,
                                        tag='amount_info')

    def operate_ar_sys_info(self, info):
        for k, v in info.items():
            if k == 'data' and 'Внешний' in v and 'открывается.' in v:
                print('Внешний открывается')
                self.terminal.open_entry_gate_operation_start()
            elif k == 'data' and 'Внешний' in v and 'закрывается.' in v:
                print('Внешний закрывается')
                self.terminal.close_entry_gate_operation_start()
            elif k == 'data' and 'Внутренний' in v and 'открывается.' in v:
                print('Внутренний открывается')
                self.terminal.open_exit_gate_operation_start()
            elif k == 'data' and 'Внутренний' in v and 'закрывается.' in v:
                print('Внутренний закрывается')
                self.terminal.close_exit_gate_operation_start()

    def update_status_operate(self, info):
        # Если получена команда на обновление статуса заезда
        self.status_ready = False
        self.road_anim_info['active'] = True
        for k, v in info.items():
            self.road_anim_info[k] = v
        if (info['status'].strip() == 'Ожидание пересечения фотоэлементов.'):
            self.mainPage.make_abort_active()
        if (info['protocol'].strip() == 'Машина заезжает.' or info[
            'protocol'].strip() == 'Машина выезжает.'):
            self.updateMainTree()
        self.drawStatus()
        if str(info['notes']).strip() == 'Запись обновлена':
            self.updateMainTree()
        if (
                self.current == 'MainPage' or self.current == 'ManualGateControl') and not self.currentPage.blockImgDrawn:
            self.drawCarMoving()
        if (info['status'].strip() == 'Протокол завершен'
                or info['status'].strip() == 'Время истекло!'
                or info['status'].strip() == 'Заезд прерван вручную!'):
            self.operateStatusEnd()

    def draw_road_anim(self):
        if self.road_anim_info['active']:
            self.drawCarMoving()
            self.drawStatus()

    def car_detected_operate(self, auto_id: int, client_id: int,
                             trash_cat_id: int, trash_type_id: int,
                             course: str, have_gross: bool, car_protocol,
                             polygon: id, **kwargs):
        # Если получена команда на открытие ОРУП
        self.currentPage.orupState = True
        # Получить репрезентативные значения по ID
        client_repr = self.get_client_repr(client_id)
        trash_cat_repr = self.get_trash_cat_repr(trash_cat_id)
        trash_type_repr = self.get_trash_type_repr(trash_type_id)
        auto_repr = self.get_auto_repr(auto_id)
        polygon = self.get_polygon_repr(polygon)
        self.currentPage.car_protocol = car_protocol
        if have_gross:
            # Если брутто взвешено, вывести ОРУП-тара
            self.currentPage.orupActExit(carnum=auto_repr, call_method="auto",
                                         course=course)
        else:
            # Если же нет (надо инициировать заезд), вывести ОРУП-брутто
            self.currentPage.orupAct(carnum=auto_repr, contragent=client_repr,
                                     trashType=trash_type_repr,
                                     trashCat=trash_cat_repr,
                                     call_method="auto",
                                     car_protocol=car_protocol,
                                     course=course, polygon=polygon)

    def fetch_if_record_init(self, carnum):
        active_cars = self.terminal.get_cars_inside()
        if carnum in active_cars:
            return True

    def fetch_car_protocol(self, carnum):
        try:
            car_protocol = self.general_tables_dict[s.auto_table][carnum][
                'id_type']
        except KeyError:
            car_protocol = 'tails'
        return car_protocol

    def open_entry_gate(self):
        self.ar_qdk.operate_gate_manual_control(operation='open',
                                                gate_name='entry')

    def close_entry_gate(self):
        self.ar_qdk.operate_gate_manual_control(operation='close',
                                                gate_name='entry')

    def open_exit_gate(self):
        self.ar_qdk.operate_gate_manual_control(operation='open',
                                                gate_name='exit')

    def close_exit_gate(self):
        self.ar_qdk.operate_gate_manual_control(operation='close',
                                                gate_name='exit')

    def ifORUPcanAppear(self):
        # Возвращает TRUE, если можно нарисовать окно ОРУП
        if (self.currentPage and self.current != 'AuthWin'
                and self.current != 'ManualGateControl'
                and self.status_ready and not self.currentPage.blockImgDrawn):
            return True
        else:
            return False

    def getInfoFromDict(self, info, target):
        # Получить зачение словаря с информацией о команде по ключу
        goal = info[target]
        if goal == 'none':
            goal = 'Неизвестно'
        return goal

    def operateStatusEnd(self):
        '''Обработчик завершения заезда авто'''
        sleep(2)
        self.currentPage.can.delete('mtext', 'car_icon')
        self.status_ready = True
        self.road_anim_info['active'] = False
        self.mainPage.make_abort_unactive()

    def updateMainTree(self, mode='usual'):
        '''Обновить таблицу текущих записей'''
        if self.current == 'MainPage' and self.mainPage.orupState == False:
            self.mainPage.updateTree()
            if mode == 'create':
                self.mainPage.drawMainTree()

    def getData(self, sock):
        '''Получает сериализированные данные и возвращает их в исходную форму'''
        data = sock.recv(4096)
        if data: data = pickle.loads(data)
        return data

    def getOrupMode(self, course, id_type):
        '''Определить атрибут, передаваемый ОРУПу, согласно курсу движения авто'''
        mode = '_'.join((id_type, course))
        return mode

    def drawStatus(self):
        '''Рисует статус заезда текстом при заезде-выезде на главном меню'''
        self.mainPage.can.delete('mtext')
        if self.current == 'MainPage' and self.mainPage.orupState == False:
            num = 'Гос. номер авто:\n' + self.road_anim_info['carnum']
            status = 'Статус:\n' + self.road_anim_info['status']
            notes = 'Примечания:\n' + str(self.road_anim_info['notes'])
            self.mainPage.can.create_text(self.terminal.w / 9.15,
                                          self.terminal.h / 5.12,
                                          text=num, font=fonts.status_text,
                                          tag='mtext', fill='#BABABA',
                                          anchor=NW)
            self.mainPage.can.create_text(self.terminal.w / 9.15,
                                          self.terminal.h / 3.84,
                                          text=status, font=fonts.status_text,
                                          tag='mtext', fill='#BABABA',
                                          anchor=NW)
            self.mainPage.can.create_text(self.terminal.w / 9.15,
                                          self.terminal.h / 3.12,
                                          text=notes, font=fonts.status_text,
                                          tag='mtext', fill='#BABABA',
                                          anchor=NW)

    def drawCarMoving(self):
        '''Рисует грузовик на грузовой платформе при инициировании проокола
		заезда или выезда на главном меню'''
        self.car_protocol = self.road_anim_info['protocol']
        self.car_direction = self.road_anim_info['course']

        car_direction_txt = self.road_anim_info['face']
        cur_pos_txt = self.road_anim_info['pos']

        cur_pos_cm = self.settings.car_poses[cur_pos_txt]
        obj = self.settings.car_face_info[car_direction_txt]
        obj = self.terminal.getAttrByName(obj)
        self.drawCarIcon(obj, cur_pos_cm)

    def drawCarIcon(self, obj, poses):
        self.mainPage.can.delete('car_icon')
        self.mainPage.can.create_image(poses, image=obj[3], anchor=NW,
                                       tag='car_icon')

    def try_login(self, status, id, *args, **kwargs):
        """ Обрабатывает результат авторизации от GravityCore """
        if status:
            self.current_userid = id
            self.currentPage.drawToolbar()
            self.authWin.rebinding()
            self.mainPage.openWin()
            self.status_ready = True
            if not self.currentPage.clockLaunched:
                self.currentPage.start_clock()
                self.currentPage.clockLaunched = True

    def get_gcore_status(self):
        # Запросить статус GCore
        self.ar_qdk.get_status()

    def close_record(self, record_id):
        """ Закрыть незаконченную запись (только раунд брутто) """
        self.ar_qdk.close_opened_record(record_id=record_id)
        self.currentPage.destroyBlockImg()

    def open_new_page(self, page):
        try:
            self.currentPage.page_close_operations()
        except:
            pass
        self.current = page.name
        self.currentPage = page

    def get_polygon_objects_reprs(self, table_name=s.polygon_objects_table):
        """ Вернуть репрезентативные значения из таблицы организаций-пользователей весовой площадкой """
        return self.get_table_reprs(table_name)

    def get_polygon_object_id(self, polygon_repr):
        return db_funcs.get_id_by_repr_table(self.general_tables_dict,
                                             s.polygon_objects_table,
                                             polygon_repr)

    def get_auto_reprs(self, auto_table=s.auto_table):
        """ Вернуть репрезентативные значения из таблицы авто """
        return self.get_table_reprs(auto_table)

    def get_auto_repr(self, auto_id):
        """ Вернуть репрезентативные значения из таблицы юзеров """
        return db_funcs.get_repr_by_id_table(self.general_tables_dict,
                                             s.auto_table, auto_id)

    def get_auto_id(self, auto_repr):
        """ Вернуть id юзера с репрезегтативным значением auto_repr"""
        return db_funcs.get_id_by_repr_table(self.general_tables_dict,
                                             s.auto_table, auto_repr)

    def get_users_reprs(self, users_table=s.users_table):
        """ Вернуть репрезентативные значения из таблицы users"""
        return self.get_table_reprs(users_table)

    def get_user_repr(self, user_id):
        """ Вернуть репрезентативные значения из таблицы юзеров """
        return db_funcs.get_repr_by_id_table(self.general_tables_dict,
                                             s.users_table, user_id)

    def get_user_id(self, user_repr):
        """ Вернуть id юзера с репрезегтативным значением user_repr"""
        return db_funcs.get_id_by_repr_table(self.general_tables_dict,
                                             s.users_table, user_repr)

    def get_trash_types_reprs(self, trash_types_table=s.trash_types_table):
        """ Вернуть все репрезентативные значения из таблицы видов грузов """
        return self.get_table_reprs(trash_types_table)

    def get_trash_type_repr(self, trash_type_id):
        """ Вернуть репрезентативное название trash_type по его id """
        return db_funcs.get_repr_by_id_table(self.general_tables_dict,
                                             s.trash_types_table,
                                             trash_type_id)

    def get_polygon_repr(self, polygon_id):
        """ Вернуть репрезентативное название полигона по его id """
        return db_funcs.get_repr_by_id_table(self.general_tables_dict,
                                             s.polygon_objects_table,
                                             polygon_id)

    def get_trash_type_id(self, type_name):
        """ Вернуть id вида груза type_name"""
        return db_funcs.get_id_by_repr_table(self.general_tables_dict,
                                             s.trash_types_table, type_name)

    def get_trash_cats_reprs(self, trash_cats_table=s.trash_cats_table):
        """ Вернуть репрезентативные значения из таблицы категорий грузов """
        return self.get_table_reprs(trash_cats_table)

    def get_trash_cat_repr(self, trash_cat_id):
        """ Вернуть репрезентативное название trash_cat по его id """
        return db_funcs.get_repr_by_id_table(self.general_tables_dict,
                                             s.trash_cats_table,
                                             trash_cat_id)

    def get_trash_cat_id(self, cat_name):
        """ Вернуть id категории груза cat_name"""
        return db_funcs.get_id_by_repr_table(self.general_tables_dict,
                                             s.trash_cats_table,
                                             cat_name)

    def get_clients_reprs(self, clients_table=s.clients_table):
        """ Вернуть все репрезентативные значения из таблицы Клиенты"""
        return self.get_table_reprs(clients_table)

    def get_client_repr(self, client_id):
        """ Вернуть репрезентативное название client по его id """
        return db_funcs.get_repr_by_id_table(self.general_tables_dict,
                                             s.clients_table, client_id)

    def get_client_id(self, client):
        """ Вернуть id клиента client"""
        return db_funcs.get_id_by_repr_table(self.general_tables_dict,
                                             s.clients_table, client)

    def get_table_reprs(self, table_name):
        """ Вернуть репрезентативные (понтятные для людей) значения из таблицы tablename
         ( например cat_name из trash_cats) """
        return db_funcs.get_table_rerps(self.general_tables_dict, table_name)

    def get_trashtypes_by_trashcat_repr(self, trash_cat_repr):
        """ Вернуть список видов грузов, у которых trash_cat = trash_cat_repr[id]"""
        trash_types = db_funcs.get_trashtypes_by_trashcat_repr(
            self.general_tables_dict, s.trash_types_table,
            s.trash_cats_table, trash_cat_repr)
        if trash_cat_repr != 'Прочее' and trash_cat_repr.strip() != 'ТКО':
            # Добавить виды грузов, присущих категории "Прочее"
            trash_types += db_funcs.get_trashtypes_by_trashcat_repr(
                self.general_tables_dict, s.trash_types_table,
                s.trash_cats_table, 'Прочее')
        return trash_types

    def get_gcore_health_monitor(self):
        """ Получить состояние GCore """
        self.ar_qdk.get_health_monitor()

    def get_wdb_tables_info(self):
        """ Сохранить все данные таблиц wdb в словарь вида {tablename0: [info0, info1], tablename1: [info4, info[2]}"""
        for tablename in list(s.tables_info.keys()):
            self.ar_qdk.get_table_info(table_name=tablename)
            while True:
                response = self.recieve_ar_responses()
                core_method, method_result = response
                if core_method == 'get_table_info':
                    self.operate_ar_response(core_method, method_result)
                    break

    def no_ar_connection(self):
        """ Если нет подключения к AR """
        self.loadingcan.delete('no_connection_info')
        self.loadingcan.create_text(self.root.winfo_screenwidth() / 2,
                                    self.root.winfo_screenheight() / 2,
                                    text='Не удалось подключиться к ядру...'
                                         '\nПерезапуск...',
                                    font=fonts.loading_status_font,
                                    fill='white',
                                    anchor='s',
                                    justify='center',
                                    tags = ('no_connection_info'))
