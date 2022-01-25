from tkinter import *
from tkinter import ttk
import _thread as thread
from glob import glob
import datetime, threading, time
from cm.configs import config as s
from cm.widgets.drop_down_combobox import AutocompleteCombobox
from pyscreenshot import grab
from PIL import ImageFilter, Image, ImageTk
from traceback import format_exc
from time import sleep
import locale
import cm.styles.color_solutions as cs
from cm.styles import fonts
import pickle
from cm.styles import element_sizes as el_sizes


class Terminal():
    """Супер-класс для всех остальных модулей-окон (статистика, диспуты и проч)"""

    def __init__(self, root, settings, operator, can):
        self.operator = operator
        self.root = root
        self.w = settings.screenwidth
        self.h = settings.screenheight
        self.screencenter = self.w / 2
        self.screenmiddle = (self.screencenter, self.h / 2)
        self.font = '"Montserrat SemiBold" 11'
        self.title = ''  # Название окна, должно быть предопределено
        self.settings = settings
        self.rootdir = self.settings.rootdir
        self.screensize = '{}x{}'.format(self.w, self.h)
        self.can = can
        self.textcolor = '#BABABA'
        self.clockLaunched = False
        self.dayDisputs = {}
        self.poligonsList = []
        self.ifDisputs = 0
        self.hiden_widgets = []
        self.errors = []
        self.trash = []
        self.messagewas = False
        self.mutex = thread.allocate_lock()
        self.cickling = True
        self.weightlist = [0]
        self.userRole = 'moder'
        self.orupState = False
        self.abort_all_errors_shown()
        self.blockImgDrawn = False
        self.orupMode = 'enter'
        self.listname = []
        self.gate_arrow_imgs = {}
        self.win_widgets = []
        self.blurDrawn = False
        self.car_choose_mode = 'auto'
        self.carnum_was = ''
        self.car_protocol = None
        self.sent_car_number = None

    def carnumCallback(self, P):
        '''Вызывается каждый раз, когда в поле для ввода гос номера на
		въездном ОРУП случается событие типа write'''
        boolean = False
        if P == "":
            # Нужно для того, что бы можно было стирать ввод
            return True
        else:
            if len(P) > 9:
                # Некорректная длина номера, не позволять длину больше 9
                return False
            for p in P:
                if p in s.allowed_carnum_symbols or str.isdigit(p) or p == "":
                    # Проверить вводимый символ на факт нахождения в списке допустимых
                    boolean = True
                else:
                    boolean = False
            return boolean

    def launchingOperations(self):
        '''Выполняет стартовые операции при выполнении программы'''
        threading.Thread(target=self.checking_thread, args=()).start()
        self.operator.ar_qdk.capture_cm_launched()
        # locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
        # self.root.bind('<Button-1>', lambda event : self.indoctrinator(event,self.operator))

    def getHistoryData(self, data='today', typeMode='id', catMode='id'):
        history = self.tar.getTodayHistory2(s.book)
        return history

    def get_timenow(self):
        '''Возвращает отформатированную, читабельную дату'''
        today = datetime.datetime.today()
        frmt = today.strftime('%Y.%m.%d %H:%M:%S')
        return frmt

    def creating_canvas(self, master, bg):
        '''Создает холст'''
        self.can.delete('maincanv', 'statusel', 'win', 'tree')
        obj = self.getAttrByName(bg)
        self.can.create_image(obj[1], obj[2], image=obj[3],
                              anchor=NW, tag='maincanv')
        self.can.update()

    def drawSlices(self, mode='def'):
        '''Рисует слоя (градиент,фонт) и накладывает их друг на друга'''
        if mode == 'AuthWin':
            # obj = self.getAttrByName('gradient')
            self.drawWin('maincanv', 'logo', 'login', 'password')
            # self.can.create_image(obj[1], obj[2], image=obj[3],
            #                      anchor=NW, tag='maincanv')
        elif mode == 'shadow':
            obj = self.getAttrByName('shadow')
            self.can.create_image(obj[1], obj[2], image=obj[3],
                                  anchor=NW, tag='maincanv')
        else:
            #	obj = self.getAttrByName('frontscreen')
            self.drawWin('maincanv', 'toolbar')

    def getAttrByName(self, name):
        '''Получить объект из settings, по его имени в строковом виде'''
        obj = 'self.settings.%s' % name
        obj = eval(obj)
        return obj

    def getCurUsr(self):
        curUsr = self.operator.authWin.currentUser
        return curUsr

    def update_window(self):
        self.blockwin.destroy()
        self.operator.open_main()

    def initBlockImg(self, name, btnsname, slice='shadow', mode='new',
                     seconds=[], hide_widgets=[], **kwargs):
        self.blockImgDrawn = True
        self.can.delete('clockel')
        if not self.blurDrawn:
            self.drawBlurScreen()
        else:
            self.can.itemconfigure(self.bluredScreen, state='normal')
        self.can.delete(self.settings.exit_gate, self.settings.entry_gate,
                        'statusel', 'car_icon')
        self.drawBlockImg(name=name)
        addBtns = self.getAttrByName(btnsname)
        self.buttons_creation(buttons=addBtns, tagname='tempBtn')
        self.hiden_widgets = self.hiden_widgets + hide_widgets + self.created_buttons
        try:
            self.hiden_widgets += self.operator.toolbar_btns
        except:
            pass
        try:
            self.hiden_widgets.append(self.usersComboBox)
            self.hiden_widgets.append(self.loginEntry)
        except:
            pass
        self.hide_widgets(self.hiden_widgets)

        try:
            self.tree.lower()
        except:
            pass

    def drawBlockImg(self, name, master='def'):
        image = self.getAttrByName(name)
        if master == 'def':
            master = self.can
        master.create_image(image[1], image[2], image=image[3], tag='blockimg')

    def drawBlurScreen(self):
        '''Рисует заблюренный фон'''
        self.listname = []
        # self.drawWin('shadow', 'shadow')
        screenshot = grab(bbox=(0, 0, self.w, self.h))  # Сделать скриншот
        screenshot = screenshot.filter(ImageFilter.BLUR)
        self.listname.append(screenshot)
        image = ImageTk.PhotoImage(self.listname[-1])
        self.listname.append(image)
        self.bluredScreen = self.can.create_image(self.screenmiddle,
                                                  image=self.listname[-1],
                                                  tags=('blurScreen'))
        self.listname.append(self.bluredScreen)
        self.blurDrawn = True
        self.can.delete('shadow')

    def destroyBlockImg(self, mode='total'):
        self.can.delete('blockimg', 'shadow', 'errorbackground', 'tempBtn')
        self.show_widgets()
        self.unbindORUP()
        try:
            self.tree.lift()
            self.can.itemconfigure(self.bluredScreen, state='hidden')
        except:
            pass
        self.hiden_widgets = []
        if self.operator.current == 'MainPage' or self.operator.current == 'ManualGateControl':
            self.draw_gate_arrows()
        if mode != 'block_flag_fix':
            self.blockImgDrawn = False
        self.show_time()
        self.operator.statPage.place_amount_info(
            self.operator.statPage.weight_sum,
            self.operator.statPage.records_amount,
            tag='amount_info')

    def slide_anim(self):
        i = 0
        animlist = []
        for animimg in self.settings.slanimimgs:
            a = self.can.create_image(self.w / 2, self.h / 2, image=animimg,
                                      tag='animel')
            animlist.append(a)
        while i != 2:
            self.can.delete(animlist[i])
            time.sleep(0.07)
            i += 1
        self.can.delete('animel')

    def thread_slideanim(self):
        anim = threading.Thread(target=self.slide_anim, args=())
        anim.setDaemon(True)
        anim.start()

    def create_main_buttons(self):
        self.operator.toolbar_btns = self.buttons_creation(
            buttons=self.settings.toolBarBtns, tagname='btn')

    def buttons_creation(self, buttons='def', tagname='btn'):
        ''' Функция создания кнопок'''
        self.can.delete(tagname)
        all_buttons = []
        if tagname == 'winBtn':
            self.created_buttons = []
        if buttons == 'def':
            buttons = self.buttons
            if self.name != 'AuthWin':
                buttons += [self.settings.exitBtn, self.settings.lockBtn,
                            self.settings.minimize_btn]
        for obj in buttons:
            button = self.get_create_btn(obj)
            self.can.create_window(obj[1], obj[2], window=button, tag=tagname)
            if tagname == 'winBtn':
                self.created_buttons.append(button)
            all_buttons.append(button)
        return all_buttons

    def minimize_window(self):
        """ Свернуть программу """
        self.root.wm_state('iconic')

    def get_create_btn(self, obj):
        button = ttk.Button(self.root, command=lambda image=obj, self=self,
                                                      operator=self.operator: eval(
            obj[3]),
                            padding='0 0 0 0', takefocus=False)
        button['cursor'] = 'hand2'
        button['image'] = obj[4]
        button.bind("<Enter>", lambda event, button=button,
                                      image=obj: self.btn_enter(button, image))
        button.bind("<Leave>", lambda event, button=button,
                                      image=obj: self.btn_leave(button, image))
        button['width'] = 0
        print("OBJ0", obj[0])
        if obj[0].strip() == 'notifUs':
            self.notif_btn = button
        try:
            button['style'] = obj[7]
        except:
            pass
        return button

    def btn_enter(self, button, image):
        try:
            button['image'] = image[8]
        except:
            pass

    def btn_leave(self, button, image):
        try:
            button['image'] = image[4]
        except:
            pass

    def getDaysBetween(self, end, numdays):
        date_list = [end - datetime.timedelta(days=x) for x in range(numdays)]
        return date_list

    def start_clock(self):
        thread = threading.Thread(target=self.show_time_cycle, args=())
        thread.start()

    def show_time_cycle(self):
        olddate = datetime.datetime(1997, 8, 24)
        while True:
            date = datetime.datetime.now()
            diff = (date - olddate).total_seconds()
            if self.operator.current != 'AuthWin' and diff > 59 and self.operator.currentPage.blockImgDrawn == False:
                olddate = self.show_time()
                time.sleep(1)
            else:
                # print('Не удалось нарисовать время, diff', diff)
                time.sleep(3)

    def show_time(self):
        date = datetime.datetime.now()
        datestr = date.strftime('%d %b')
        timestr = date.strftime('%H:%M')
        self.can.delete('clockel')
        if self.operator.currentPage.blockImgDrawn == False:
            self.can.create_text(self.settings.w / 18.841379310344827,
                                 self.h / 10.971428571428572,
                                 text=datestr, font=fonts.time_font,
                                 fill=self.textcolor, tag='clockel',
                                 justify='center')
            self.can.create_text(self.settings.w / 19.514285714285716,
                                 self.h / 7.68,
                                 text=timestr, font=fonts.date_font,
                                 fill=self.textcolor, tag='clockel',
                                 justify='center')
            olddate = date
        else:
            print('not false', self.operator.currentPage.blockImgDrawn)
            olddate = date
        return olddate

    def format_mainscreens(self):
        settings = self.settings
        self.format_image(settings.mainscreenpath, settings.screensize)
        self.format_image(settings.dwnldbgpath, (int(self.w / 2.56),
                                                 int(self.h / 4.267)))
        for image in glob(self.settings.slideanimpath + '\\*'):
            self.format_image(image, settings.screensize)

    def checking_thread(self):
        '''Проверяет сосотяние весов каждую секунду и отрисовывает при наличии обновлений'''
        while True:
            weight = self.operator.smlist[-1]
            new_state = self.get_new_weight()
            if ((
                    self.operator.current == 'MainPage' or self.operator.current == 'ManualGateControl') and
                    self.operator.currentPage.blockImgDrawn == False):
                self.can.delete('statusel')
                old_state = weight
                self.draw_weight(new_state)
            time.sleep(1)

    def get_new_weight(self):
        weight = self.operator.smlist[-1]
        new_state = weight + ' кг'
        return new_state

    # print('not equal!')
    # print('here')
    # else: pass

    def drawing(self, canimg='backscreen'):
        ''' Родовая функция заполнения экрана (кнопки,холст,фокусировка)
		Кнопки уникальны для каждого окна, и должны быть предопределены'''
        self.can.delete('maincanv', 'tree', 'picker', 'tempBtn')
        if self.operator.animation == 'on':
            self.thread_slideanim()

    def bindArrows(self):
        if not self.settings.mirrored:
            left_button = self.operator.currentPage.orupActExit
            right_button = self.operator.currentPage.orupAct
        else:
            left_button = self.operator.currentPage.orupAct
            right_button = self.operator.currentPage.orupActExit
        self.root.bind('<Left>', lambda event: left_button())
        self.root.bind('<Right>', lambda event: right_button())

    def unbindArrows(self):
        self.root.unbind('<Left>')
        self.root.unbind('<Right>')

    def drawWin(self, tag='win', *names):
        for arg in names:
            obj = self.getAttrByName(arg)
            self.can.create_image(obj[1], obj[2], image=obj[3], tag=tag)

    def drawObj(self, *names):
        for arg in names:
            obj = self.getAttrByName(arg)
            self.can.create_window(obj[0], obj[1], window=obj[2])

    def drawToolbar(self):
        objects = [self.settings.toolbar]
        for obj in objects:
            self.can.create_image(obj[1], obj[2], image=obj[3], tag='toolbar')

    def format_image(self, imagepath, size):
        imgobj = Image.open(imagepath).resize(size, Image.ANTIALIAS)
        imgobj.save(imagepath)

    def draw_block_win(self, name):
        self.operator.current = name
        if name == 'chatwin':
            xsize = self.settings.bwS
            ysize = self.settings.bhS
            buttons = self.settings.chatBtns
        self.blockwin = Canvas(self.root, highlightthickness=0)
        img = self.settings.chatwin
        self.blockwin.create_image(img[1], img[2], image=img[3])
        self.blockwin.config(width=xsize, height=ysize)
        self.can.create_window(self.screenmiddle, window=self.blockwin)

    def draw_weight(self, weight=None):
        """ Рисует вес """
        if not weight:
            weight = self.get_new_weight()
        self.can.create_text(self.settings.weight_show_posses,
                             font=fonts.weight_font, text=weight,
                             fill='#BABABA',
                             tag='statusel')
        return weight

    def openWin(self):
        self.can.delete('winBtn')
        self.operator.open_new_page(self)
        self.blurDrawn = False
        self.win_widgets = []
        self.drawing()
        self.draw_picker()
        self.can.tag_raise('clockel')
        self.operator.get_gcore_health_monitor()
        self.operator.ar_qdk.catch_window_switch(self.operator.current)

    def draw_picker(self, ):
        self.can.delete('picker')
        try:
            self.can.create_image(self.btn_name[1], self.btn_name[2],
                                  image=self.settings.picker, tag='picker')
        except AttributeError:
            print(format_exc())

    def getEntry(self, w=30, h=1, bg='#272727', fill='#BABABA'):
        var = StringVar(self.root)
        newEntry = Entry(self.root, bd=0, width=w, textvariable=var, bg=bg,
                         fg=fill, font=fonts.general_entry_font,
                         disabledbackground=bg, disabledforeground=fill,
                         highlightthickness=0)
        return newEntry

    def getText(self, w=50, h=5, bg='#272727', fill='#BABABA',
                font=fonts.orup_font, *args, **kwargs):
        newText = Text(self.root, bd=0, width=w, height=h, bg=bg, fg=fill,
                       font=fonts.general_text_font)
        return newText

    def getOptionMenu(self, deff, listname, w=30, h=0, bg='#272727',
                      fg='#BABABA',
                      varname='self.deffValue', mode='deff', tracecomm='',
                      font=fonts.general_optionmenu_font):
        com1 = '{} = StringVar(self.root)'.format(varname)
        com2 = '{}.set(deff)'.format(varname)
        exec(com1)
        exec(com2)
        option_menu = OptionMenu(self.root, eval(varname), *listname)
        option_menu.config(indicatoron=0, font=font, bg=bg, width=w,
                           height=h, fg=fg, highlightthickness=0,
                           highlightbackground='blue', highlightcolor='red',
                           anchor='nw', relief='flat')
        option_menu['borderwidth'] = 0
        option_menu["highlightthickness"] = 0
        option_menu["menu"].config(bg='#3D3D3D', fg='#E2E2E2',
                                   activebackground=cs.orup_active_color,
                                   font=fonts.orup_font, relief='flat',
                                   borderwidth=0)
        option_menu['menu']['borderwidth'] = 0
        if mode == 'trace':
            self.chosenTrashCat = eval(varname).get()
            eval(varname).trace("w", tracecomm)
        return option_menu

    def big_orup_exit(self, carnum='', carrier='Физлицо', trash_type='Прочее',
                      trash_cat='Прочее', call_method='manual',
                      car_protocol='NEG', course='OUT'):
        # Создает большой ОРУП при нажатии на кнопку на малой ОРУП
        self.destroyORUP(mode='total')
        self.orupAct(carnum, carrier, trash_type, trash_cat, call_method,
                     car_protocol, course)

    def set_window_normal(self, state='zoomed', **kwargs):
        if self.root.wm_state() == 'iconic':
            self.root.wm_state(state)

    def orupAct(self, carnum='', contragent='Физлицо', trashType='Прочее',
                trashCat='ПО', call_method='manual',
                car_protocol='tails', course='IN', polygon=None):
        self.operator.get_gcore_status()
        self.set_window_normal()
        # self.can.delete('clockel')
        self.carnum_was = carnum
        self.car_course = course
        self.orupState = True
        self.initBlockImg('orupWinUs', 'orupEnterBtns')
        self.posEntrys(carnum, trashType, trashCat, contragent,
                       call_method=call_method, car_protocol=car_protocol,
                       polygon=polygon)
        self.turn_on_request_last_event()
        self.root.bind('<Return>', lambda event: self.initOrupAct())
        self.root.bind('<Escape>',
                       lambda event: self.destroyORUP(mode="decline"))
        self.root.bind("<Button-1>",
                       lambda event: self.clear_optionmenu(event))
        self.unbindArrows()

    def orupActExit(self, carnum='deff', call_method="manual", course='OUT'):
        self.destroyORUP(mode='total')
        self.operator.get_gcore_status()
        self.carnum_was = carnum
        self.set_window_normal()
        self.can.delete('clockel')
        self.course = course
        self.car_course = course
        self.exCarIndex = 0
        self.orupState = True
        self.initBlockImg(name='orupWinEx', btnsname='orupExitBtns')
        self.posExitInt(carnum, call_method)
        self.root.bind('<Return>', lambda event: self.launchExitProtocol())
        self.root.bind('<Escape>',
                       lambda event: self.destroyORUP(mode="decline"))
        self.root.bind('<Up>', lambda event: self.arrowUp())
        self.root.bind('<Down>', lambda event: self.arrowDown())
        self.unbindArrows()

    def arrowDown(self):
        if self.exCarIndex < len(self.exCarNums) - 1:
            self.exCarIndex = + 1
        else:
            self.exCarIndex = 0
        self.carNumVar.set(self.exCarNums[self.exCarIndex])
        print(self.exCarIndex)

    def arrowUp(self):
        if self.exCarIndex > 0:
            print('was more than zero - ', self.exCarIndex)
            self.exCarIndex = self.exCarIndex - 1
        else:
            self.exCarIndex = len(self.exCarNums) - 1
        self.carNumVar.set(self.exCarNums[self.exCarIndex])

    def posExitInt(self, car_num, callback_method, spec_protocols='exit'):
        # Разместить виджеты на выездном ОРУП
        self.car_choose_mode = callback_method
        self.exCarNums = self.get_cars_inside()
        print("EXCARNUMS:", self.exCarNums, "LEN", self.exCarNums)
        clist = []
        if callback_method == 'manual':
            clist = self.exCarNums
            # for car_num in self.exCarNums:
            #   clist.append(car_num)
            self.exCarNums = clist
        if self.exCarNums != None and len(self.exCarNums):
            self.carNumVar = StringVar()
            self.escOrupOpt = self.getOptionMenu(deff=self.exCarNums[0],
                                                 listname=self.exCarNums,
                                                 w=el_sizes.option_menus[
                                                     'choose_car'][
                                                     self.screensize]['width'],
                                                 bg=cs.orup_bg_color,
                                                 varname='self.carNumVar')
            self.can.create_window(self.w / 1.9, self.h / 2.320,
                                   window=self.escOrupOpt, tag='orupentry')
            if callback_method == 'auto':
                self.carNumVar.set(car_num)
                self.escOrupOpt['state'] = 'disabled'
        self.commEx = self.getText(h=1,
                                   w=el_sizes.text_boxes['orup_exit_comm'][
                                       self.screensize]['width'],
                                   bg=cs.orup_bg_color, font=fonts.orup_font)
        self.can.create_window(self.w / 1.825, self.h / 2.025,
                               window=self.commEx,
                               tag='orupentry')
        self.pos_orup_protocols(spec_protocols)

    def get_cars_inside(self):
        return [car['car_number'] for car in self.operator.unfinished_records
                if not car['time_out']]

    def launchExitProtocol(self, mode='redbgEx'):
        self.operator.get_gcore_status()
        carnum = self.carNumVar.get()
        data_dict = {}
        data_dict['ar_status'] = self.operator.gcore_status
        data_dict['car_number'] = carnum
        data_dict['have_rfid'] = self.check_car_rfid(carnum)
        data_dict['weight_data'] = int(self.operator.smlist[-1])
        data_dict['photo_object'] = self.settings.redbgEx[3]
        data_dict['car_protocol'] = self.operator.fetch_car_protocol(carnum)
        data_dict['sqlshell'] = object
        data_dict['course'] = self.course
        data_dict['have_brutto'] = self.operator.fetch_if_record_init(carnum)
        data_dict['choose_mode'] = self.car_choose_mode
        data_dict['photo_object'] = self.settings.redbgEx[3]
        response = self.operator.orup_error_manager.check_orup_errors(
            orup='tara',
            xpos=self.settings.redbgEx[1],
            ypos=self.settings.redbgEx[2],
            **data_dict)
        if not response:
            # self.init_ar_comm_sending(orup=self.settings.orup_exit_comm)
            # self.operator.ar_qdk.start_car_protocol()
            self.start_car_protocol(orup_mode=self.settings.orup_exit_comm)

    def start_car_protocol(self, orup_mode, carnum=None):
        self.operator.status_ready = False
        info = self.get_entrys_info(orup_mode)
        if self.car_course != None:
            info['course'] = self.car_course
        if carnum != None:
            info['carnum'] = carnum
        self.operator.ar_qdk.start_car_protocol(info)
        self.operator.ar_qdk.catch_orup_accept(car_number=info['carnum'])
        self.destroyORUP(mode='total')

    def check_car_init_again(self, carnum):
        # Проверяет, не приехала ли машина с ТКО опять взвешивать брутто, не взвесив до этого тару
        car_inside = self.operator.fetch_if_record_init(carnum)
        if car_inside and self.car_course == 'IN' and self.car_protocol == 'rfid':
            return True

    def form_send_msg(self, **kwargs):
        msg = {}
        for k, v in kwargs.items():
            msg[k] = v
        return msg

    def get_entrys_info(self, orup):
        # Получить данные из полей ввода ОРУП (въезд или выезд определяется по перменной orup)
        if orup == self.settings.orup_enter_comm:
            info = self.get_orup_entry_ids()
        elif orup == self.settings.orup_exit_comm:
            info = self.get_ex_entrys_info()
        info['car_choose_mode'] = self.car_choose_mode
        info['dlinnomer'] = self.dlinnomer_var.get()
        info['polomka'] = self.polomka_var.get()
        info['orup_mode'] = orup
        return info

    def get_orup_entry_ids(self):
        # Получить ID тех данных, что представлены были в ОРУП
        info = self.get_orup_entry_reprs()  # Сначала полные имена
        # Потом начинаем преоброзовывать, вставляя их ID
        info['carrier'] = self.operator.get_client_id(info['carrier'])
        info['trash_cat'] = self.operator.get_trash_cat_id(info['trash_cat'])
        info['trash_type'] = self.operator.get_trash_type_id(info['trash_type'])
        info['operator'] = self.operator.get_user_id(info['operator'])
        info['polygon_object'] = self.operator.get_polygon_object_id(info['polygon_object'])
        return info

    def get_orup_entry_reprs(self):
        """ Получить данные из полей ввода въездного оруп"""
        info = {}
        info['carnum'] = self.carnum.get()
        info['carrier'] = self.contragentCombo.get()
        info['trash_cat'] = self.trashCatOm.get()
        info['trash_type'] = self.trashTypeOm.get()
        info['operator'] = self.operator.authWin.currentUser
        info['polygon_object'] = self.obj_choose_combo.get()
        info['comm'] = self.comm.get("1.0", 'end-1c')
        info['course'] = 'IN'
        info['carnum_was'] = self.carnum_was
        return info

    def get_ex_entrys_info(self):
        # Получить данные из всех полей ввода выездного ОРУП
        info = {}
        info['course'] = 'OUT'
        info['carnum'] = self.carNumVar.get()
        info['comm'] = self.commEx.get("1.0", 'end-1c')
        return info

    def turn_on_request_last_event(self):
        """ Включить запрос данных о последнем заезде машины, если вбили гос.номер """
        self.orupCarNumVar.trace_add('write', self.car_number_change_reaction)
        # Привязать функцию реакции софта на ввод гос. номера
        vcmd = self.root.register(self.carnumCallback)
        self.carnum.validatecommand = (vcmd, '%P')

    def car_number_change_reaction(self, *args):
        # Функция реакции программы на совершение действий типа write в combobox для ввода гос.номера
        carnum = self.orupCarNumVar.get()
        value = len(carnum)
        self.orupCarNumVar.set(carnum.upper())
        if value < 8:
            # Сделать красную обводку
            self.carnum['style'] = 'orupIncorrect.TCombobox'
        else:
            # Оставить обычное оформление
            self.carnum['style'] = 'orup.TCombobox'
        if value >= 8 and carnum != self.sent_car_number:
            # Если длина гос. номер корректная, и запрос get_last_event по этому номеру еще не отправлялся - отправить
            self.operator.ar_qdk.get_last_event(
                auto_id=self.operator.get_auto_id(carnum))
            self.sent_car_number = carnum

    def check_gcore_health(self, health_monitor, *args, **kwargs):
        """ Проверяет health_monitor, представляющий из себя словарь вида
        {'Состояние камеры': {'status':False, 'info': 'Обрыв связи'}, 'ФТП': {'status':True, 'info': 'Все в порядке'}},
        Если встречает status=False, меняет иконку окна нотификаций на красную. Если же все хорошо - на обычную."""
        incorrect = self.if_incorrect_status(health_monitor)
        if incorrect:
            self.set_notif_alert()
        else:
            self.unset_notif_alert()

    def if_incorrect_status(self, health_monitor, *args, **kwargs):
        """ Перебирает все элементы системы и чекает их статус. Возвращает True, если хотя бы один элемент не работает
        """
        status = [info['status'] for info in list(health_monitor.values())]
        if False in status:
            return True

    def set_notif_alert(self):
        """ Сделать иконку окна нотификаций красной (что-то не так в health_monitor)
        """
        try:
            self.settings.toolBarBtns.remove(self.settings.notifBtn)
            self.settings.toolBarBtns.append(self.settings.notifIconAlert)
        except:
            pass

    def unset_notif_alert(self):
        """ Сделать иконку окна нотификаций красной (что-то не так в health_monitor)
        """
        try:
            self.settings.toolBarBtns.remove(self.settings.notifIconAlert)
            self.settings.toolBarBtns.append(self.settings.notifBtn)
        except:
            pass

    def posEntrys(self, carnum, trashtype, trashcat, contragent='', notes='',
                  spec_protocols='entry',
                  car_protocol='tails', call_method='auto', polygon=None):
        self.car_choose_mode = call_method
        # Вставить поля для выбора перевозчика, ввода гос.номера, выбора кат. груза и вида груза, и ввода комментария
        self.create_orup_carrier()
        self.create_orup_carnum(carnum)
        if carnum != '' and car_protocol == 'rfid':
            self.block_entry_set_value(self.carnum, carnum)
        else:
            self.entry_set_value(self.carnum, carnum)
        self.create_orup_tc()
        self.create_orup_tt()
        self.create_orup_object_choose(polygon)
        self.create_orup_comm(notes)
        # Попробовать вставить в поля переданные данные, если не получится - вставить маску
        self.try_set_attr_all(trashcat, trashtype, contragent)
        # Заблокировать поля на редактирование, если есть необходимость
        # self.block_entrys(car_protocol, trashcat, trashtype, contragent)
        # Вставить чек-боксы для выбора "Длинномер|Поломка", если есть необходимость
        self.pos_orup_protocols(spec_protocols)

    def create_orup_comm(self, notes):
        self.comm = self.getText(h=1, w=
        el_sizes.text_boxes['orup_entry_comm'][self.screensize]['width'],
                                 bg=cs.orup_bg_color, font=fonts.orup_font)
        self.comm.insert(1.0, notes)
        self.can.create_window(self.w / 1.78, self.h / 1.655, window=self.comm,
                               tag='orupentry')

    def create_orup_carrier(self):
        # Создать комбобокс на въездном ОРУП для ввода названия перевозчика
        self.contragentCombo = self.create_orup_combobox(self.w / 1.78,
                                                         self.h / 2.7)
        self.contragentCombo.set_completion_list(
            self.operator.get_clients_reprs())

    def create_orup_object_choose(self, polygon):
        # Создать комбобокс на въездном ОРУП для ввода названия организации, принимающей груз
        polygon_objects = self.operator.get_polygon_objects_reprs()  # Получить repr значнеия организаций
        self.obj_choose_combo = self.create_orup_combobox(self.w / 1.78,
                                                          self.h / 2.33)
        self.obj_choose_combo.set_completion_list(polygon_objects)
        if polygon == None:
            self.obj_choose_combo.set(polygon_objects[0])
        else:
            self.obj_choose_combo.set(polygon)

    def create_orup_tt(self):
        # Создать комбобокс на въездном ОРУП для ввода вида груза (trash type)
        self.trashTypeOm = self.create_orup_combobox(self.w / 1.78,
                                                     self.h / 1.825,
                                                     tags=('orupentry',
                                                           'trashTypeOm',))
        self.trashTypeOm.set('Выберите вид груза')

    def create_orup_combobox(self, xpos, ypos, width=29, height=3,
                             tags=('orupentry',), *args, **kwargs):
        # Универсальный конструктор для создания полей на въездном ОРУП
        some_cb = self.create_combobox(self.root, xpos, ypos, tags=tags,
                                       width=
                                       el_sizes.comboboxes['orup.general'][
                                           self.screensize]['width'],
                                       height=
                                       el_sizes.comboboxes['orup.general'][
                                           self.screensize]['height'],
                                       foreground=cs.orup_fg_color,
                                       font=fonts.orup_font, *args, **kwargs)
        self.configure_combobox(some_cb)
        return some_cb

    def create_combobox(self, root, xpos, ypos, tags, *args, **kwargs):
        # Универсальный конструктор создания и размещения всяких Combobox
        some_cb = AutocompleteCombobox(root)
        some_cb.config(*args, **kwargs)
        self.can.create_window(xpos, ypos, window=some_cb, tag=tags)
        return some_cb

    def create_orup_carnum(self, request_last_event=False):
        # Создать комбобокс на въездном ОРУП для ввода гос. номера
        self.orupCarNumVar = StringVar()
        self.carnum = self.create_orup_combobox(self.w / 1.78, self.h / 3.2,
                                                validate='all',
                                                textvariable=self.orupCarNumVar)
        self.carnum.set_completion_list(self.operator.get_auto_reprs())

    def turn_on_request_last_event(self):
        """ Включить запрос данных о последнем заезде машины, если вбили гос.номер """
        self.orupCarNumVar.trace_add('write', self.car_number_change_reaction)
        # Привязать функцию реакции софта на ввод гос. номера
        vcmd = self.root.register(self.carnumCallback)
        self.carnum.validatecommand = (vcmd, '%P')

    def create_orup_tc(self):
        # Создать комбобокс на въездном ОРУП для выбора категории груза
        self.trashCatVar = StringVar()
        self.trashCatOm = self.create_orup_combobox(self.w / 1.78,
                                                    self.h / 2.05,
                                                    textvariable=self.trashCatVar)
        self.trashCatVar.trace_add('write', self.posTrashTypes)
        self.trashCatOm.set_completion_list(
            self.operator.get_trash_cats_reprs())

    def posTrashTypes(self, a='a', b='b', c='c', d='d', e='e'):
        self.chosenTrashCat = self.trashCatOm.get()
        if self.chosenTrashCat == '':
            trashtypes = ['Выберите вид груза', ]
        else:
            try:
                trashtypes = self.operator.get_trashtypes_by_trashcat_repr(
                    self.chosenTrashCat).copy()
            except KeyError:
                trashtypes = []
        self.trashTypeOm.set_completion_list(trashtypes)
        if self.chosenTrashCat.strip() == 'ТКО':
            self.trashTypeOm.set('4 класс')
        else:
            self.trashTypeOm.set('Прочее')

    def try_set_attr_all(self, trashcat, trashtype, carrier):
        # Попытка вставить данные, переданные в ОРУП в соответствующие окна, если не получится, вставляется сообщение
        # ошибки
        self.try_set_attr(self.trashCatOm, trashcat,
                          self.operator.get_trash_cats_reprs(),
                          'Выберите категорию груза')
        self.try_set_attr(self.trashTypeOm, trashtype,
                          self.operator.get_trash_types_reprs(),
                          'Выберите вид груза')
        self.try_set_attr(self.contragentCombo, carrier,
                          self.operator.get_clients_reprs(),
                          'Выберите перевозчика')

    def block_entrys(self, mode, trash_cat, trash_type, carrier):
        # Для всех полей ОРУП (кроме коммента) вставить значение по умолчанию и запретить редактирование
        if not 'rfid' in mode:
            self.block_entry_set_value(self.trashCatOm, trash_cat)
            self.block_entry_set_value(self.trashTypeOm, trash_type)
            self.block_entry_set_value(self.contragentCombo, carrier)

    def block_entry_set_value(self, entry, value):
        # Вставляет в поле значение по умолчанию и запрещает редактирование
        self.entry_set_value(entry, value)
        entry['state'] = 'disabled'

    def entry_set_value(self, entry, value):
        entry.delete(0, END)
        if value:
            entry.insert(0, value)

    def pos_orup_protocols(self, mode):
        if mode:
            self.polomka_var = IntVar(value=0)
            self.dlinnomer_var = IntVar(value=0)
            self.polomka_check = ttk.Checkbutton(variable=self.polomka_var)
            self.dlinnomer_check = ttk.Checkbutton(variable=self.dlinnomer_var)
            self.polomka_check['style'] = 'check_orup.TCheckbutton'
            self.dlinnomer_check['style'] = 'check_orup.TCheckbutton'
            if mode == 'entry':
                xpos_polomka = self.w / 2.17
                xpos_dlinnomer = self.w / 1.78
                ypos = self.h / 1.48
            else:
                xpos_polomka = self.w / 2.112
                xpos_dlinnomer = self.w / 1.752
                ypos = self.h / 1.8
            self.can.create_window(xpos_polomka, ypos,
                                   window=self.polomka_check, tag='orupentry')
            self.can.create_window(xpos_dlinnomer, ypos,
                                   window=self.dlinnomer_check,
                                   tag='orupentry')

    def configure_combobox(self, om):
        om.master.option_add('*TCombobox*Listbox.background', '#3D3D3D')
        om.master.option_add('*TCombobox*Listbox.foreground', '#E2E2E2')
        om.master.option_add('*TCombobox*Listbox.selectBackground',
                             cs.orup_active_color)
        om.master.option_add('*TCombobox*Listbox.font', fonts.orup_font)
        om['height'] = 15
        om['style'] = 'orup.TCombobox'

    def clear_optionmenu(self,
                         event):  # that you must include the event as an arg, even if you don't use it.
        if 'combobox' in str(event.widget):
            event.widget.delete(0, "end")
            try:
                event.widget.set_completion_list_demo(event.widget.all_list[0])
            except:
                print(format_exc())
        return None

    def get_btn_by_name(self, btn_name_png, btns_list):
        for btn in btns_list:
            if btn[0] == btn_name_png:
                return btn[7]

    def try_set_attr(self, optionmenu, attr, admitted, fail_message='Укажите'):
        # Пытается присовить optionmenu значение attr, если attr принадлежит множеству admitted. Если же нет
        # присваивает fail_message):
        if attr in admitted:
            optionmenu.set(attr)
        else:
            optionmenu.set(fail_message)

    def checkOrupCarnum(self):
        if len(self.orupCarNumVar.get()) < 8:
            return True

    def checkOrupContragent(self):
        insert = self.contragentCombo.get()
        if insert not in self.operator.contragentsList:
            return True

    def checkRfid(self, carnum):
        for car in self.operator.terminal.carlist:
            if carnum == car[0] and car[5] == 'rfid':
                print('have a contact!')
                return True

    def init_car_again_error(self, mode):
        msg = 'Вы пытаетесь взвесить брутто для машины, у которого брутто уже есть.' \
              '\nНажимая принять, вы закроете прошлую запись'
        self.initErrorWin(text=msg, name=mode)
        self.car_again_error_shown = True

    def initOrupAct(self, mode='redbg'):
        carnum = self.orupCarNumVar.get()
        self.car_protocol = self.operator.fetch_car_protocol(carnum)
        data_dict = {}
        data_dict['car_number'] = carnum
        data_dict['car_protocol'] = self.car_protocol
        data_dict['ar_status'] = self.operator.gcore_status
        data_dict['course'] = self.car_course
        data_dict['chosen_trash_cat'] = self.trashCatOm.get()
        data_dict['type_name'] = self.trashTypeOm.get()
        data_dict['weight_data'] = int(self.operator.smlist[-1])
        data_dict['carrier_name'] = self.contragentCombo.get()
        data_dict['sqlshell'] = object
        data_dict['have_brutto'] = self.operator.fetch_if_record_init(carnum)
        data_dict['have_rfid'] = self.check_car_rfid(carnum)
        data_dict['choose_mode'] = self.car_choose_mode
        data_dict['photo_object'] = self.settings.redbg[3]
        response = self.operator.orup_error_manager.check_orup_errors(
            orup='brutto',
            xpos=self.settings.redbg[1],
            ypos=self.settings.redbg[2],
            **data_dict)
        if not response:
            self.start_car_protocol(orup_mode=self.settings.orup_enter_comm)

    def check_car_rfid(self, carnum):
        try:
            rfid = self.operator.general_tables_dict[s.auto_table][carnum][
                'rfid']
        except KeyError:
            rfid = None
        return rfid

    def check_scale_errors(self):
        if int(self.operator.smlist[-1]) % 10 != 0:
            return True

    def check_absence_error(self, string_var, listname):
        # Проверяет значение переменной string_var на факт нахождения в списке listname
        # Возвращает True, если string_name НЕ присутствует в listname
        insert = string_var.get()
        if insert.lower() not in [x.lower() for x in listname]:
            return True

    def initErrorWin(self, text, name='redbg'):
        self.can.delete('errorwintxt')
        if name == 'redbgEx':
            btnsname = 'orupExitBtns'
            blockWinImg = 'orupWinEx'
            textXpos = self.w / 2
            textYpos = self.h / 1.35
        elif name == 'record_changing':
            btnsname = 'record_change_btns'
            blockWinImg = 'record_change_win'
            textXpos = self.w / 2
            textYpos = self.h / 1.4
            name = 'redbg'
        else:
            btnsname = 'orupEnterBtns'
            blockWinImg = 'orupWinUs'
            textXpos = self.w / 2
            textYpos = self.h / 1.2
        self.destroyBlockImg(mode='block_flag_fix')
        self.drawWin('errorbackground', name)
        self.initBlockImg(name=blockWinImg, btnsname=btnsname, mode='new')
        self.can.update()
        self.can.create_text(textXpos, textYpos, text=text,
                             font=fonts.general_error_text,
                             fill=self.textcolor,
                             tags=('errorwin', 'errorwintxt'), justify=CENTER)

    def initOccupError(self, mode):
        msg = "Программа занята обработкой проезда другой машины!"
        self.initErrorWin(text=msg, name=mode)

    def initNoCarNumError(self, mode):
        msg = 'Введите гос. номер!'
        self.initErrorWin(text=msg, name=mode)

    def initNoBruttoError(self, mode):
        msg = 'Данная машина не взвешивала брутто!\nПеред взвешиванием тары необходимо взвесить брутто.'
        self.initErrorWin(text=msg, name=mode)
        self.bruttoErrorShown = True

    def initNoContragentError(self, mode):
        msg = 'Проверьте правильность названия перевозчика!'
        self.initErrorWin(text=msg, name=mode)

    def initRfidError(self, mode):
        print('DETECTED RFID')
        msg = "Внимание у данного авто установлена метка RFID!\nНажмите еще раз для ручного пропуска."
        self.initErrorWin(text=msg, name=mode)
        self.rfidErrorShown = True

    def initDebtError(self, mode, forbide_reason):
        msg = "Внимание! Данной организации запрещен въезд на территорию!\nПричина: {}".format(
            forbide_reason)
        self.initErrorWin(text=msg)
        self.debtErrorShown = True

    def destroyORUP(self, mode='deff'):
        self.can.delete('orupentry', 'shadow', 'errorwin')
        self.destroyBlockImg(mode)
        self.orupState = False
        self.car_course = None
        self.car_protocol = None
        self.operator.updateMainTree()
        self.abort_all_errors_shown()
        if mode == 'decline':
            self.operator.ar_qdk.catch_orup_decline(car_number=self.carnum_was)
        if self.operator.current == 'MainPage' or self.operator.currentPage == 'ManualGateControl':
            self.draw_weight()
            if self.operator.currentPage == 'MainPage':
                self.operator.draw_road_anim()

    def abort_all_errors_shown(self):
        self.bruttoErrorShown = False
        self.rfidErrorShown = False
        self.debtErrorShown = False
        self.car_again_error_shown = False

    def unbindORUP(self):
        self.root.unbind('<Return>')
        self.root.unbind('<Escape>')
        self.root.unbind('<UP>')
        self.root.unbind('<DOWN>')
        self.root.unbind('<Button-1>')
        self.bindArrows()

    def page_close_operations(self):
        pass

    def hide_widgets(self, widgets):
        for widget in widgets:
            widget.lower()

    def show_widgets(self, widgets='deff'):
        if widgets == 'deff':
            widgets = self.hiden_widgets
        for widget in widgets:
            widget.lift()

    def get_attr_and_draw(self, attr, *args, **kwargs):
        obj = self.getAttrByName(attr)
        imgobj = self.can.create_image(obj[1], obj[2], image=obj[3], *args,
                                       **kwargs)
        return imgobj

    def draw_gate_arrows(self):
        self.draw_set_arrow(self.settings.exit_gate)
        self.draw_set_arrow(self.settings.entry_gate)

    def open_entry_gate_operation_start(self):
        # threading.Thread(target=self.rotate_gate_arrow, args=(self.settings.entry_gate, 'open', 'IN', -1, -80)).start()
        threading.Thread(target=self.rotate_gate_arrow, args=(
            self.settings.entry_gate, 'open', 'OUT', 1, 80)).start()

    def open_exit_gate_operation_start(self):
        threading.Thread(target=self.rotate_gate_arrow, args=(
            self.settings.exit_gate, 'open', 'OUT', 1, 80)).start()

    # threading.Thread(target=self.rotate_gate_arrow, args=(self.settings.entry_gate, 'open', 'IN', -1, -80)).start()

    def close_entry_gate_operation_start(self):
        threading.Thread(target=self.rotate_gate_arrow, args=(
            self.settings.entry_gate, 'close', 'OUT', -1, 0)).start()

    def close_exit_gate_operation_start(self):
        threading.Thread(target=self.rotate_gate_arrow, args=(
            self.settings.exit_gate, 'close', 'OUT', -1, 0)).start()

    def rotate_gate_arrow(self, arrow_attr, pos, course, step=1, endpos=80,
                          sleeptime=0.025):
        arrow_info = self.operator.road_anim_info[arrow_attr]
        if arrow_info['busy']:
            return
        else:
            arrow_info['busy'] = True
        while arrow_info['pos'] != endpos:
            self.can.delete(arrow_attr)
            if (
                    self.operator.current == 'MainPage' or self.operator.current == 'ManualGateControl') and \
                    self.operator.currentPage.blockImgDrawn == False:
                self.draw_set_arrow(arrow_attr)
            arrow_info['pos'] += step
            sleep(sleeptime)
        arrow_info['busy'] = False

    def drawExitWin(self, name='exitwin', slice='shadow', btnsname='exitBtns',
                    *seconds, **kwargs):
        if self.blockImgDrawn == False:
            self.initBlockImg(name=name, btnsname=btnsname, mode='new')

    def draw_set_arrow(self, arrow_attr):
        self.can.delete(arrow_attr)
        arrow_info = self.operator.road_anim_info[arrow_attr]
        image = Image.open(self.settings.imgsysdir + 'gate_arrow.png')
        start = 0
        end = image.height
        obj = self.getAttrByName(arrow_attr)
        tags = ['maincanv'] + [arrow_attr]
        # print('Установка стрел', self.operator.road_anim_info)
        tkimage = ImageTk.PhotoImage(
            image.rotate(arrow_info['pos'], expand=True, center=(start, end)))
        self.can.create_image(obj[1], obj[2], image=tkimage, tags=tags)
        self.operator.road_anim_info[arrow_attr]['img'] = tkimage
        self.operator.road_anim_info[arrow_attr]['img_obg'] = image
