""" Лаунчер Gravity interface """

from cm.configs.settings import Settings
from cm import functions
from cm.main_operator import *
from cm.wlistener import WListener
from traceback import format_exc
import screeninfo
import os



monitors = screeninfo.get_monitors()
width = monitors[0].width
height = monitors[0].height
deffaultScreenSize = (width, height)
dirpath = os.path.dirname(os.path.realpath(__file__))
img_dir = os.path.join(dirpath, 'imgs')
loadingWin = os.path.join(img_dir, 'loadingWin.png')

root = Tk()
root.grab_set()
root.focus_set()
root.attributes('-fullscreen', True)

loadingcan = Canvas(root, highlightthickness=0)
loadingcan.pack(fill=BOTH, expand=YES)
photoimg = PhotoImage(file=loadingWin)
loadingcan.create_image(width / 2, height / 2, image=photoimg)
loadingcan.create_text(width / 2, height / 2 * 1.24, text='Добро пожаловать',
                       font=fonts.loading_welcome_font,
                       fill='white', tag='loadingtext')

def check_double():
    """ Проверить, запущена ли уже программа """
    from cm_adb import client, server
    ip, port, msg = 'localhost', 1001, 'MSG'
    try:
        client.client(ip, port, msg)
        loadingcan.delete('loadingtext')
        loadingcan.create_text(width/2, height/2 * 1.24,
                               text='Программа уже запущена, вы пытаетесь запустить ее повторно!\nЕсли это не так, позвоните в тех. поддержку.',
                               font=fonts.loading_status_font, fill='white',
                               justify='center')
        sleep(5)
        zoom_another_copy()
        os._exit(0)
    except ConnectionRefusedError:
        server.CMADBServer(ip,port)._start()


def zoom_another_copy():
    """ Выполняется, если попытаться запустить дубль. Разворачивает
    первоначальную копию"""
    from cm_qdk.main import CMQDK
    cm_qdk = CMQDK('localhost', 50505)
    cm_qdk.make_connection()
    cm_qdk.zoom_app()
    cm_qdk.get_data()


from cm.styles.styles import *


def startLoading():
    '''Инициализация проекта, выполняется параллельно с окном загрузки'''
    # root.grab_set()
    # root.focus_set()
    arg_parser = functions.create_parser()
    namespace = arg_parser.parse_args()
    settings = Settings(root, dirpath, mirrored=eval(namespace.mirrored))
    wlistener = WListener('Въезд', 'COM1', 9600, ar_ip=namespace.ar_ip)
    can = Canvas(root, highlightthickness=0, bg=cs.main_background_color)
    check_double()
    for canvas in [loadingcan, can]:
        functions.draw_version_on_screen(canvas=canvas,
                                         xpos=settings.screenwidth - 30,
                                         ypos=settings.screenheight - 30,
                                         version_text=settings.version + ' v.',
                                         font=fonts.version_font)
    Operator(root, settings, wlistener, can, deffaultScreenSize,
             loadingcan, ar_ip=namespace.ar_ip, ar_port=namespace.ar_port)
    loadingcan.destroy()
    # root.overrideredirect(False)
    root.attributes('-fullscreen', True)
    can.pack(fill=BOTH, expand=YES)
    root.geometry("{0}x{1}-0-0".format(root.winfo_screenwidth(),
                                       root.winfo_screenheight()))


def startLoadingThread():
    """ Запуск инициализации загрузки параллельным потоком """
    threading.Thread(target=startLoading, args=()).start()


def launch_mainloop():
    """ Запустить оснвной цикл работы """
    root.after(100, startLoadingThread)
    try:
        root.mainloop()
    except:
        # При выходе из программы - трассировать текст исключения и выполнить
        # необходимые завершающие работы
        print(format_exc())
        os._exit(0)


launch_mainloop()
